#!/bin/zsh
# конвейер добора комплектов (27.10): каждые 10 мин — новая порция кандидатов → Codex (по одной порции за раз), пока поиск не закончится
setopt null_glob; cd "${0:A:h}"; K="/Volumes/ADATA SD810/WB/Подбор/1688_данные/sets_2026-10-27"; export SETS_ONLY=1 CHUNK=200
C="/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex"
while true; do
  fin=""; grep -q "chain_sets3 готово" "$K/kq.log" 2>/dev/null && fin="--final"
  python3 -I wide_prep.py $fin >> wide.log 2>&1
  for t in TASK_codex_w*.md; do
    n=${t#TASK_codex_w}; n=${n%.md}
    [ -f "codex_w$n.done" ] && continue
    echo "$(date +%H:%M) Codex порция $n старт" >> wide.log
    perl -e 'alarm 10800; exec @ARGV' "$C" exec -m gpt-6.1-sol --cd "$PWD" --skip-git-repo-check -s workspace-write -c mcp_servers.n8n-mcp.enabled=false -o codex_w${n}_out.md - < "$t" > codex_w$n.log 2>&1
    echo "$(date +%H:%M) Codex порция $n: оценено $(python3 -c "import json;print(len(json.load(open('codex_taste_w$n.json'))))" 2>/dev/null || echo 0)" >> wide.log
    touch "codex_w$n.done"
  done
  if [ -n "$fin" ]; then
    python3 -I wide_prep.py --final >> wide.log 2>&1
    ls TASK_codex_w*.md | while read t; do n=${t#TASK_codex_w}; n=${n%.md}; [ -f "codex_w$n.done" ] || continue 2; done
    [ -z "$(for t in TASK_codex_w*.md; do n=${t#TASK_codex_w}; n=${n%.md}; [ -f codex_w$n.done ] || echo x; done)" ] && break
  fi
  sleep 600
done
echo "sets_runner готово $(date +%H:%M)" >> wide.log
