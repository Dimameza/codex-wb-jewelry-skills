#!/bin/zsh
# выгрузка витрин порциями (час паузы после слайдера) → сопоставление → Kimi отбор по фото (без браузера)
cd "${0:A:h}"; O="/Volumes/ADATA SD810/WB/Подбор/1688_данные/factories_2026-10-22"
left() { python3 -c "
import json,os
O='$O'; fac=json.load(open(O+'/factories.json'))
def ok(c):
    p=O+'/shops/'+c+'.json'
    return os.path.exists(p) and not json.load(open(p)).get('err')
print(sum(1 for f in fac if f['mem'] and not ok(f['code'])))"; }
for round in 1 2 3 4 5 6; do
  n=$(left); echo "$(date +%H:%M) осталось витрин $n" >> match.log
  [ "$n" -eq 0 ] && break
  for m in $(seq 1 60); do sleep 60; done
  python3 -I "../1688_данные/tools/scan_factories.py" "$O" "$O/factories.tsv" >> "$O/scan.log" 2>&1
done
python3 -I match.py >> match.log 2>&1 && python3 -I prep_kimi.py >> match.log 2>&1 || exit 1
for i in $(seq 1 12); do
  perl -e 'alarm 7200; exec @ARGV' ~/.kimi-code/bin/kimi -m kimi-code/k3 -p "$(cat TASK_kimi_taste.md)" > kimi_taste.log 2>&1
  grep -q "error: failed" kimi_taste.log || { echo "kimi ok $(date +%H:%M)" >> match.log; exit 0; }
  echo "kimi попытка $i: $(grep -o 'error: [^.]*' kimi_taste.log | head -1)" >> match.log; sleep 1200
done
