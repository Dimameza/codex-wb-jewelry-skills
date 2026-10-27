#!/bin/zsh
# сбор карточек с автоповтором: после падения (таймаут страницы) — пересчитать недостающие и продолжить; до 6 попыток
cd "${0:A:h}"; export CBG_MAIN=1
for a in $(seq 1 60); do   # крутится, пока в best_ids.json есть несобранные (очередь пополняется по ходу)
  n=$(python3 -I -c "
import json
ids=json.load(open('best_ids.json')); d=json.load(open('details.json')); need=[k for k in ids if k not in d]
json.dump(need,open('best_ids.json','w')); print(len(need))")
  [ "$n" -eq 0 ] && break
  python3 -I fetch_details.py >> details.log 2>&1 || { echo "$(date +%H:%M) сбор упал, повтор $a (осталось $n)" >> details.log; sleep 30; }
done
echo "fetch_loop готово $(date +%H:%M)" >> details.log
