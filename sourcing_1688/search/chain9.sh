#!/bin/zsh
# новые фабрики: поиск → витрины (порциями, час паузы после слайдера) → сопоставление → вход Kimi (комплекты 24.10)
cd "${0:A:h}"; export CBG_MAIN=1
for round in 1 2 3 4 5 6; do
  python3 -I ../tools/scan_factories.py "$PWD" "$PWD/factories.tsv" >> scan.log 2>&1
  n=$(python3 -c "
import json,os
fac=json.load(open('factories.json'))
ok=lambda c: os.path.exists('shops/'+c+'.json') and not json.load(open('shops/'+c+'.json')).get('err')
print(sum(1 for f in fac if f['mem'] and not ok(f['code'])))")
  echo "$(date +%H:%M) осталось витрин $n" >> scan.log
  [ "$n" -eq 0 ] && break
  for m in $(seq 1 60); do sleep 60; done
done
echo "chain9 витрины готовы $(date +%H:%M)" >> scan.log
