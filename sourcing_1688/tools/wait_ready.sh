#!/bin/zsh
# wait_ready.sh <tab_id> [max_s] — ждёт readyState=complete, затем 4 с на догрузку
T=${0:A:h}; i=0; max=${2:-40}
while [ $i -lt $max ]; do
  s=$("$T/chrome_bg.sh" js $1 'document.readyState' 2>/dev/null) && [ "$s" = "complete" ] && { sleep 4; exit 0; }
  sleep 2; i=$((i+2))
done
exit 1
