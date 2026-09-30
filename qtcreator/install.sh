#!/bin/bash
# Midnight theme for Qt Creator (macOS)
#   ./install.sh              install / update
#   ./install.sh --uninstall  remove
#   ./install.sh --test-qss   install with a red status bar, to check the
#                             glow stylesheet loads (rerun without it after)
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
USERDIR="$HOME/.config/QtProject/qtcreator"
THEMES="$USERDIR/themes"
STYLES="$USERDIR/styles"

if [[ "${1:-}" == "--uninstall" ]]; then
  rm -f "$THEMES/midnight.creatortheme" "$STYLES/midnight.xml" "$STYLES/midnight-glow.xml" "$USERDIR/midnight-glow.qss" "$USERDIR"/stars-*.png "$USERDIR"/bg-*.png
  echo "Midnight removed. Pick another theme in Qt Creator → Settings → Environment → Interface."
  exit 0
fi

# 1. Find Qt Creator's own theme files, so Midnight matches your exact version
BASE=""
CANDIDATES=("/Applications/Qt Creator.app" "$HOME/Applications/Qt Creator.app" "$HOME/Qt/Qt Creator.app")
if command -v mdfind >/dev/null; then
  while IFS= read -r p; do CANDIDATES+=("$p"); done \
    < <(mdfind "kMDItemCFBundleIdentifier == 'org.qt-project.qtcreator'" 2>/dev/null)
fi
for app in "${CANDIDATES[@]}"; do
  if [[ -f "$app/Contents/Resources/themes/dark-2024.creatortheme" ]]; then
    BASE="$app/Contents/Resources/themes"; break
  fi
done
if [[ -z "$BASE" ]]; then
  BASE="$HERE/fallback"
  echo "Couldn't find Qt Creator.app, using the bundled base theme files instead."
else
  echo "Using base theme from: $BASE"
fi

mkdir -p "$THEMES" "$STYLES"

# 2. Copy the files the Dark (2024) theme includes (tokens, primitives, ...)
for f in "$BASE"/*.inc "$BASE"/*.figmatokens "$BASE"/*.tokenmapping; do
  [[ -e "$f" ]] && cp "$f" "$THEMES/"
done

# 3. Build midnight.creatortheme = Dark (2024) + Midnight colors
awk -v overrides="$HERE/midnight-colors.ini" '
  BEGIN {
    while ((getline line < overrides) > 0) {
      if (line ~ /^[[:space:]]*(;|$)/) continue
      split(line, kv, "="); keys[kv[1]] = 1; ov[++n] = line
    }
  }
  /^ThemeName=/                    { print "ThemeName=Midnight"; next }
  /^DefaultTextEditorColorScheme=/ { print "DefaultTextEditorColorScheme=midnight.xml"; next }
  /^\[Colors\]/ { print; print "; --- Midnight overrides ---"; for (i = 1; i <= n; i++) print ov[i]; print ""; next }
  { split($0, kv, "="); if (kv[1] in keys) next; print }
' "$BASE/dark-2024.creatortheme" > "$THEMES/midnight.creatortheme"

# 4. Editor color schemes + optional glow stylesheet
cp "$HERE/midnight.xml" "$HERE/midnight-glow.xml" "$STYLES/"
sed "s|@DIR@|$USERDIR|g" "$HERE/midnight-glow.qss" > "$USERDIR/midnight-glow.qss"
cp "$HERE"/stars-*.png "$USERDIR/"
if [[ -f "$HERE/bg-editor.png" ]]; then
  cp "$HERE"/bg-editor*.png "$USERDIR/"
else
  # No picture background (see README): just the stars, along the top
  rm -f "$USERDIR"/bg-editor*.png
  sed -i '' -e "s|bg-editor.png|stars-editor.png|" -e "s|background-position: bottom right|background-position: top right|" \
    "$USERDIR/midnight-glow.qss"
fi
if [[ "${1:-}" == "--test-qss" ]]; then
  printf '\n/* TEST: remove by rerunning install.sh */\nQStatusBar { background: red; }\n' >> "$USERDIR/midnight-glow.qss"
  echo "Test rule added: the status bar should be red after relaunching with the glow."
fi
chmod +x "$HERE/Qt Creator (Glow).command" 2>/dev/null || true
# Downloaded files get quarantined, which makes Gatekeeper block the launcher
xattr -d com.apple.quarantine "$HERE/Qt Creator (Glow).command" 2>/dev/null || true

echo
echo "Installed. Now in Qt Creator:"
echo "  1. Settings → Environment → Interface → Theme: Midnight, then restart"
echo "  2. Settings → Text Editor → Font & Colors → Color Scheme: Midnight"
echo
echo "For the background glows: choose the \"Midnight Glow\" color scheme instead,"
echo "and start Qt Creator with \"Qt Creator (Glow).command\"."
