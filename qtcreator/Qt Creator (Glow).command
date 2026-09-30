#!/bin/bash
# Starts Qt Creator with the Midnight glow stylesheet.
# Double-click in Finder, or run from Terminal. (Run install.sh first.)
QSS="$HOME/.config/QtProject/qtcreator/midnight-glow.qss"

if [[ ! -f "$QSS" ]]; then
  echo "Glow stylesheet not found. Run install.sh first."; exit 1
fi
if pgrep -xq "Qt Creator"; then
  echo "Qt Creator is already running. Quit it first (⌘Q), then run this again."; exit 1
fi

open -a "Qt Creator" --args -stylesheet="$QSS"

# Confirm the new instance actually got the stylesheet
sleep 3
if ps -o args= -p "$(pgrep -x "Qt Creator" | head -1)" 2>/dev/null | grep -q -- "-stylesheet="; then
  echo "Qt Creator started with the glow stylesheet."
else
  echo "Warning: Qt Creator is running WITHOUT the glow stylesheet."
fi
