#!/bin/zsh
# сторож: если активной оказалась наша фоновая вкладка (есть /tmp/chrome_bg_user_<id>), переключить на ближайшую чужую слева
while true; do
  osascript <<'AS' >/dev/null 2>&1
tell application "Google Chrome"
  repeat with w in windows
    set a to active tab index of w
    set aid to (id of tab a of w) as text
    set ours to false
    try
      do shell script "test -f /tmp/chrome_bg_user_" & aid
      set ours to true
    end try
    if ours then
      repeat with i from (a - 1) to 1 by -1
        set tid to (id of tab i of w) as text
        set mine to false
        try
          do shell script "test -f /tmp/chrome_bg_user_" & tid
          set mine to true
        end try
        if not mine then
          set active tab index of w to i
          exit repeat
        end if
      end repeat
    end if
  end repeat
end tell
AS
  sleep 15
done
