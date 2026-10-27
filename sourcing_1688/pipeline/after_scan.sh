#!/bin/zsh
# после догрузки витрин: сопоставление → добор фото → вход Kimi → отбор по фото → страница находок
cd "${0:A:h}"; F="/Volumes/ADATA SD810/WB/Подбор/1688_данные/factories_2026-10-22"
while pgrep -f scan_only.sh >/dev/null; do sleep 60; done
python3 -I match.py >> match.log 2>&1
python3 -I ../1688_данные/tools/img_backfill.py pool_1688.json "$F" >> match.log 2>&1
python3 -I - <<'PY' >> match.log 2>&1
import json
pool=json.load(open("pool_1688.json")); src=open("prep_kimi.py").read()
src=src.replace('pool = json.load(open(f"{W}/pool_1688.json"))','pool = [p for p in json.load(open(f"{W}/pool_1688.json")) if p.get("img")]')
exec(compile(src,"prep_kimi.py","exec"),{"__file__":"prep_kimi.py"})
PY
for i in $(seq 1 8); do
  perl -e 'alarm 7200; exec @ARGV' ~/.kimi-code/bin/kimi -m kimi-code/k3 -p "$(cat TASK_kimi_taste.md)" > kimi_taste.log 2>&1
  grep -q "error: failed" kimi_taste.log || break; sleep 1200
done
python3 -I preview.py >> match.log 2>&1
echo "after_scan done $(date +%H:%M)" >> match.log
