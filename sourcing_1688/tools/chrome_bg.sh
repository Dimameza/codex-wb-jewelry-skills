#!/bin/zsh
# Фоновые вкладки Chrome через AppleScript: без курсора, клавиатуры и активации.
# Новые вкладки открываются в ОТДЕЛЬНОМ свёрнутом окне (создаётся один раз, id в /tmp/chrome_bg_window),
# чтобы не мелькать в окнах пользователя. Вкладка ищется по id во всех окнах.
#   chrome_bg.sh open <url>         -> id вкладки
#   chrome_bg.sh nav <id> <url> | js <id> <file|код> | main <id> <file|код> | get <id> <key> | title <id> | close <id>
set -e
cmd=$1; shift
[ -n "$1" ] && [[ "$1" == *E* || "$1" == *.* ]] && [[ "$cmd" != open ]] && set -- "$(python3 -c "import sys;print(int(round(float(sys.argv[1]))))" "$1")" "${@:2}"
WF=/tmp/chrome_bg_window

FIND='on findTab(tid)
  tell application "Google Chrome"
    repeat with w in windows
      repeat with t in tabs of w
        if ((id of t) as text) is tid then return {w, t}
      end repeat
    end repeat
  end tell
  error "tab not found"
end findTab
'

restore_user_tab() {  # если наша вкладка вышла вперёд — вернуть вкладку пользователя
  local key=$(python3 -c "import sys;print(int(float(sys.argv[1])))" "$1")
  [ -f /tmp/chrome_bg_user_$key ] || return 0
  osascript -e "tell application \"Google Chrome\"
    repeat with w in windows
      if ((id of active tab of w) as text) is \"$key\" then
        set done to false
        repeat with i from 1 to count of tabs of w
          if ((id of tab i of w) as text) is \"$(cat /tmp/chrome_bg_user_$key)\" then
            set active tab index of w to i
            set done to true
          end if
        end repeat
        if not done then
          set k to active tab index of w
          if k > 1 then
            set active tab index of w to (k - 1)
          else if (count of tabs of w) > 1 then
            set active tab index of w to 2
          end if
        end if
      end if
    end repeat
  end tell" >/dev/null 2>&1 || true
}

case $cmd in
  open)
    if [ -n "$CBG_MAIN" ]; then
      # одна вкладка в конце основного окна, без нового окна (оно может мелькнуть при создании)
      osascript -e 'on run argv
  tell application "Google Chrome"
    set w to window 1
    set keep to active tab index of w
    set uid to id of active tab of w
    try
      set uid to (do shell script "cat /tmp/chrome_bg_user_" & uid)   -- активна наша вкладка: берём её «пользовательскую»
    end try
    set t to make new tab at end of tabs of w with properties {URL:(item 1 of argv)}
    set active tab index of w to keep
    set tid to id of t
    do shell script "echo " & uid & " > /tmp/chrome_bg_user_" & tid
    return tid
  end tell
end run' "$1"
      exit 0
    fi
    osascript - "$1" "$WF" <<'EOF'
on run argv
  set u to item 1 of argv
  set wf to item 2 of argv
  set wid to 0
  try
    set wid to (do shell script "cat " & quoted form of wf) as integer
  end try
  tell application "Google Chrome"
    set w to missing value
    if wid is not 0 then
      repeat with x in windows
        if id of x is wid then set w to x
      end repeat
    end if
    if w is missing value then
      set w to make new window with properties {mode:"normal"}
      set minimized of w to true
      do shell script "echo " & (id of w) & " > " & quoted form of wf
      set URL of active tab of w to u
      return id of active tab of w
    end if
    if minimized of w is false then set minimized of w to true
    set t to make new tab at end of tabs of w with properties {URL:u}
    return id of t
  end tell
end run
EOF
    ;;
  nav)
    # переход через JS внутри вкладки: Chrome при этом не выводит вкладку вперёд (set URL — выводит)
    u=$(python3 -c "import json,sys;print(json.dumps(sys.argv[1]))" "$2")
    "$0" js "$1" "(function(){location.href=$u;return 'ok';})()" >/dev/null 2>&1 || \
      osascript -e "$FIND" -e "on run argv
  set r to findTab(item 1 of argv)
  tell application \"Google Chrome\" to set URL of (item 2 of r) to (item 2 of argv)
end run" "$1" "$2"
    restore_user_tab $1 ;;
  title)
    osascript -e "$FIND" -e "on run argv
  set r to findTab(item 1 of argv)
  tell application \"Google Chrome\" to return title of (item 2 of r)
end run" "$1" ;;
  js)
    if [ -f "$2" ]; then src="$2"; else src=$(mktemp -t cbg); print -r -- "$2" > "$src"; fi
    osascript -e "$FIND" -e 'on run argv
  set r to findTab(item 1 of argv)
  set code to read POSIX file (item 2 of argv) as «class utf8»
  tell application "Google Chrome" to return execute (item 2 of r) javascript code
end run' "$1" "$src"
    ;;
  main)
    # код в ОСНОВНОМ мире страницы (execute javascript работает в изолированном и не видит её JS-объекты)
    if [ -f "$2" ]; then code=$(cat "$2"); else code="$2"; fi
    w=$(mktemp -t cbgm)
    python3 -c 'import json,sys;print("(function(){var s=document.createElement(\"script\");s.textContent="+json.dumps(sys.stdin.read())+";document.documentElement.appendChild(s);s.remove();return \"ok\";})()")' <<< "$code" > "$w"
    "$0" js "$1" "$w" ;;
  get)
    "$0" js "$1" "(function(){var e=document.getElementById('__o_$2');return e?e.textContent:'';})()" ;;
  close)
    # последнюю вкладку фонового окна не закрываем — иначе закроется окно и следующее open создаст новое (мелькнёт)
    osascript -e "$FIND" -e 'on run argv
  set r to findTab(item 1 of argv)
  set wid to 0
  try
    set wid to (do shell script "cat " & quoted form of (item 2 of argv)) as integer
  end try
  tell application "Google Chrome"
    set w to item 1 of r
    if (id of w) is wid and (count of tabs of w) is 1 then
      set URL of (item 2 of r) to "about:blank"
    else
      close (item 2 of r)
    end if
  end tell
end run' "$1" "$WF"
    ;;
  *) echo "usage: open|nav|js|main|get|title|close" >&2; exit 2 ;;
esac
