#!/bin/zsh
# 30.10: выдача WB БЕЗ ценового фильтра (28.10 стоял фильтр 1 000–1 700 ₽ — рынок обрезан снизу), MPSTATS-оверлей в фоновой вкладке Chrome
cd "${0:A:h}"; T="/Volumes/ADATA SD810/WB/Подбор/1688_данные/tools"; i=0
while read -r q; do
  i=$((i+1)); f=raw/q$(printf %02d $i).json
  [ -s $f ] && continue
  u="https://www.wildberries.ru/catalog/0/search.aspx?sort=popular&search=$(python3 -c 'import sys,urllib.parse;print(urllib.parse.quote(sys.argv[1]))' "$q")"
  id=$("$T/chrome_bg.sh" open "$u"); "$T/wait_ready.sh" $id 50
  sleep 6
  for y in 1500 3000 4500 6000 7500 9000 0; do "$T/chrome_bg.sh" js $id "window.scrollTo(0,$y);1" >/dev/null; sleep 4; done   # блоки MPSTATS грузятся только при прокрутке
  for w in 1 2 3; do
    sleep 6; out=$("$T/chrome_bg.sh" js $id "$T/wb_extract.js")
    n=$(print -r -- "$out" | python3 -c "import json,sys;d=json.load(sys.stdin);print(sum(r.get('orders30') is not None for r in d['rows']))")
    [ "$n" -ge 30 ] && break
  done
  print -r -- "$out" | python3 -c "import json,sys;d=json.load(sys.stdin);d['query']=sys.argv[1];json.dump(d,open(sys.argv[2],'w'),ensure_ascii=False);print(sys.argv[1],d['n'],sum(1 for r in d['rows'] if r.get('orders30') is not None))" "$q" $f
  "$T/chrome_bg.sh" close $id; sleep $((6 + RANDOM % 5))
done < queries.txt
echo done
