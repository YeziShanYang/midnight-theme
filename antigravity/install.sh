#!/bin/bash
# Midnight theme for Antigravity (macOS)
#   ./install.sh              install / update the color theme
#   ./install.sh --glow       also add the background glows (patches the app)
#   ./install.sh --no-glow    remove the glows, keep the color theme
#   ./install.sh --uninstall  remove everything
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
QT="$HERE/../qtcreator"
EXT_ID="midnight-theme.midnight-theme"
MARK="<!-- midnight-glow -->"

# 1. Find Antigravity
APP=""
CANDIDATES=("/Applications/Antigravity IDE.app" "/Applications/Antigravity.app"
            "$HOME/Applications/Antigravity IDE.app" "$HOME/Applications/Antigravity.app")
if command -v mdfind >/dev/null; then
  while IFS= read -r p; do CANDIDATES+=("$p"); done \
    < <(mdfind "kMDItemCFBundleIdentifier == 'com.google.antigravity*'" 2>/dev/null)
fi
for app in "${CANDIDATES[@]}"; do
  if [[ -d "$app/Contents/Resources/app/bin" ]]; then APP="$app"; break; fi
done
if [[ -z "$APP" ]]; then
  echo "Couldn't find Antigravity in /Applications or ~/Applications." >&2
  exit 1
fi
RES="$APP/Contents/Resources/app"
CLI="$(find "$RES/bin" -maxdepth 1 -type f -perm -u+x | head -n 1)"
WB="$RES/out/vs/code/electron-browser/workbench"
echo "Using: $APP"

# Antigravity checks its own files against checksums in product.json, and
# warns that the install is corrupt if one doesn't match. Keep the
# workbench.html entry in step with the file.
update_checksum() {
  python3 - "$RES/product.json" "$WB/workbench.html" <<'PY'
import base64, hashlib, re, sys
product, html = sys.argv[1], sys.argv[2]
digest = base64.b64encode(hashlib.sha256(open(html, "rb").read()).digest()).decode().rstrip("=")
text = open(product).read()
key = '"vs/code/electron-browser/workbench/workbench.html"'
new = re.sub(re.escape(key) + r'\s*:\s*"[^"]*"', f'{key}: "{digest}"', text)
if new != text:
    open(product, "w").write(new)
PY
}

remove_glow() {
  if [[ -f "$WB/workbench.html.midnight-orig" ]]; then
    mv "$WB/workbench.html.midnight-orig" "$WB/workbench.html"
  elif grep -q "$MARK" "$WB/workbench.html"; then
    sed -i '' "/$MARK/d" "$WB/workbench.html"
  fi
  rm -f "$WB/midnight-glow.css" "$WB"/midnight-*.png
  update_checksum
}

if [[ "${1:-}" == "--uninstall" ]]; then
  remove_glow
  "$CLI" --uninstall-extension "$EXT_ID" >/dev/null 2>&1 || true
  echo "Midnight removed. Reload Antigravity and pick another color theme."
  exit 0
fi
if [[ "${1:-}" == "--no-glow" ]]; then
  remove_glow
  echo "Glows removed. Reload Antigravity (Developer: Reload Window) to see it."
  exit 0
fi

# 2. Package the color theme as a .vsix and install it
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
python3 - "$HERE/extension" "$TMP/midnight.vsix" <<'PY'
import json, os, sys, zipfile
src, out = sys.argv[1], sys.argv[2]
pkg = json.load(open(os.path.join(src, "package.json")))
manifest = f"""<?xml version="1.0" encoding="utf-8"?>
<PackageManifest Version="2.0.0" xmlns="http://schemas.microsoft.com/developer/vsx-schema/2011">
  <Metadata>
    <Identity Language="en-US" Id="{pkg['name']}" Version="{pkg['version']}" Publisher="{pkg['publisher']}"/>
    <DisplayName>{pkg['displayName']}</DisplayName>
    <Description xml:space="preserve">{pkg['description']}</Description>
    <Categories>Themes</Categories>
    <Properties>
      <Property Id="Microsoft.VisualStudio.Code.Engine" Value="{pkg['engines']['vscode']}"/>
    </Properties>
  </Metadata>
  <Installation><InstallationTarget Id="Microsoft.VisualStudio.Code"/></Installation>
  <Dependencies/>
  <Assets>
    <Asset Type="Microsoft.VisualStudio.Code.Manifest" Path="extension/package.json" Addressable="true"/>
  </Assets>
</PackageManifest>
"""
types = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension=".json" ContentType="application/json"/>
  <Default Extension=".vsixmanifest" ContentType="text/xml"/>
</Types>
"""
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("extension.vsixmanifest", manifest)
    z.writestr("[Content_Types].xml", types)
    for root, _, files in os.walk(src):
        for f in files:
            if f.startswith("."):
                continue
            path = os.path.join(root, f)
            z.write(path, "extension/" + os.path.relpath(path, src))
PY
"$CLI" --install-extension "$TMP/midnight.vsix" --force

# 3. Optional glows: link midnight-glow.css into the app's workbench.html
if [[ "${1:-}" == "--glow" ]]; then
  if ! touch "$WB/.midnight-test" 2>/dev/null; then
    echo >&2
    echo "The color theme is installed, but macOS blocked the glow patch: this terminal" >&2
    echo "can't change files inside $APP." >&2
    echo "Allow it in System Settings → Privacy & Security → App Management, then rerun." >&2
    exit 1
  fi
  rm -f "$WB/.midnight-test"
  [[ -f "$WB/workbench.html.midnight-orig" ]] || cp "$WB/workbench.html" "$WB/workbench.html.midnight-orig"
  if [[ -f "$QT/bg-editor@2x.png" ]]; then
    # The picture (see ../qtcreator/README.md), pinned to the bottom-right
    cp "$QT/bg-editor@2x.png" "$WB/midnight-editor@2x.png"
    POS="right bottom"; SIZE="1400px 900px"
  else
    cp "$QT/stars-editor@2x.png" "$WB/midnight-editor@2x.png"
    POS="right top"; SIZE="1400px 320px"
  fi
  cp "$QT/stars-sidebar@2x.png" "$WB/midnight-stars-sidebar@2x.png"
  sed -e "s|@EDITOR_IMAGE@|midnight-editor@2x.png|" -e "s|@EDITOR_POS@|$POS|" -e "s|@EDITOR_SIZE@|$SIZE|" \
      -e "s|\"stars-sidebar@2x.png\"|\"midnight-stars-sidebar@2x.png\"|" \
      "$HERE/midnight-glow.css" > "$WB/midnight-glow.css"
  # Link it after the workbench's own stylesheet, so its rules win
  sed "s|^\(.*workbench.desktop.main.css.*\)$|\1\\
	<link rel=\"stylesheet\" href=\"./midnight-glow.css\"> $MARK|" \
      "$WB/workbench.html.midnight-orig" > "$WB/workbench.html"
  update_checksum
  GLOW=1
fi

echo
echo "Installed. Now in Antigravity:"
echo "  1. Reload the window (⌘⇧P → Developer: Reload Window), or restart it"
echo "  2. ⌘K ⌘T → Midnight"
if [[ -z "${GLOW:-}" ]]; then
  echo
  echo "For the background glows, run ./install.sh --glow. Antigravity updates"
  echo "replace the patched files, so rerun it after each update."
fi
