#!/bin/zsh
cd "${0:A:h}"; K=/Users/dmitrijmizinov/.kimi-code/bin/kimi
run() { for a in 1 2 3; do echo "$(date +%H:%M) kimi $1 попытка $a" >> run.log; perl -e 'alarm 7200; exec @ARGV' "$K" -p "$(cat TASK_kimi_$1.md)" > "out/kimi_$1.log" 2>&1; grep -q "connection_error" "out/kimi_$1.log" || break; sleep 120; done; echo "$(date +%H:%M) kimi $1 конец" >> run.log; }
run 3b & run 4b & wait; echo "$(date +%H:%M) kimi добор готов" >> run.log
