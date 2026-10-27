#!/bin/bash
# Installs Ink Koi into a Firefox profile.
#
#   ./install.sh                  install into the default profile
#   ./install.sh <profile-dir>    install into that profile
#   ./install.sh --list           list the profiles found
#   ./install.sh --uninstall [<profile-dir>]
#   add --tidy to also turn off stories, sponsored shortcuts and weather
#   on the new tab page
#
# Copies chrome/ into the profile, and turns on the pref that makes Firefox
# read userChrome.css and userContent.css. Any existing userChrome.css or
# userContent.css is backed up first. Quit Firefox before running it.

set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
FF="$HOME/Library/Application Support/Firefox"
TAG="// ink-koi"
PREF="user_pref(\"toolkit.legacyUserProfileCustomizations.stylesheets\", true); $TAG"
TIDY=(
  "user_pref(\"browser.newtabpage.activity-stream.feeds.section.topstories\", false); $TAG"
  "user_pref(\"browser.newtabpage.activity-stream.showSponsored\", false); $TAG"
  "user_pref(\"browser.newtabpage.activity-stream.showSponsoredTopSites\", false); $TAG"
  "user_pref(\"browser.newtabpage.activity-stream.showWeather\", false); $TAG"
)

list_profiles() {
  for p in "$FF"/Profiles/*/; do
    [ -f "$p/prefs.js" ] || continue
    echo "  ${p%/}"
  done
}

default_profile() {
  # The profile Firefox opens by default is in the [Install...] section.
  local rel
  rel=$(awk -F= '/^\[Install/{s=1;next} /^\[/{s=0} s&&$1=="Default"{print $2; exit}' "$FF/profiles.ini" 2>/dev/null || true)
  [ -n "$rel" ] && echo "$FF/$rel"
}

uninstall=0
tidy=0
args=()
for a in "$@"; do
  if [ "$a" = "--tidy" ]; then tidy=1; else args+=("$a"); fi
done
set -- "${args[@]+"${args[@]}"}"

if [ "${1:-}" = "--list" ]; then
  echo "Firefox profiles:"; list_profiles; exit 0
elif [ "${1:-}" = "--uninstall" ]; then
  uninstall=1; shift
fi

PROFILE="${1:-$(default_profile)}"
if [ -z "$PROFILE" ] || [ ! -d "$PROFILE" ]; then
  echo "Couldn't find a Firefox profile. Pass one, for example:"
  list_profiles
  echo "(Firefox shows the one it's using at about:support, under Profile Folder.)"
  exit 1
fi

if pgrep -xq firefox; then
  echo "Firefox is running. Quit it first (Cmd-Q), then run this again."
  exit 1
fi

CHROME="$PROFILE/chrome"
STAMP=$(date +%Y%m%d-%H%M%S)

if [ $uninstall = 1 ]; then
  rm -rf "$CHROME/ink-koi"
  for f in userChrome.css userContent.css; do
    if grep -q "Ink Koi for Firefox" "$CHROME/$f" 2>/dev/null; then rm "$CHROME/$f"; fi
  done
  if [ -f "$PROFILE/user.js" ]; then
    grep -v -F "$TAG" "$PROFILE/user.js" > "$PROFILE/user.js.tmp" || true
    mv "$PROFILE/user.js.tmp" "$PROFILE/user.js"
  fi
  echo "Removed Ink Koi from $PROFILE"
  echo "Backups of earlier styles, if any, are in $CHROME (*.bak-*)."
  exit 0
fi

mkdir -p "$CHROME"
for f in userChrome.css userContent.css; do
  if [ -f "$CHROME/$f" ] && ! grep -q "Ink Koi for Firefox" "$CHROME/$f"; then
    cp "$CHROME/$f" "$CHROME/$f.bak-$STAMP"
    echo "Backed up your $f to $f.bak-$STAMP"
  fi
  cp "$HERE/chrome/$f" "$CHROME/$f"
done
rm -rf "$CHROME/ink-koi"
if ls "$HERE"/chrome/ink-koi/*.png >/dev/null 2>&1; then
  cp -R "$HERE/chrome/ink-koi" "$CHROME/ink-koi"
else
  echo "No koi pictures built yet, so the new tab page will be plain paper."
  echo "See \"The picture\" in README.md to add them."
fi

# user.js is re-applied at every start, so the lines are tagged and
# rewritten on each install.
if [ -f "$PROFILE/user.js" ]; then
  grep -v -F "$TAG" "$PROFILE/user.js" > "$PROFILE/user.js.tmp" || true
  mv "$PROFILE/user.js.tmp" "$PROFILE/user.js"
fi
echo "$PREF" >> "$PROFILE/user.js"
if [ $tidy = 1 ]; then
  printf '%s\n' "${TIDY[@]}" >> "$PROFILE/user.js"
  echo "Turned off stories, sponsored shortcuts and weather on the new tab page."
fi

echo "Installed Ink Koi into $PROFILE"
echo "Start Firefox. It follows Firefox's Light / Dark setting."
