#!/bin/zsh
# описания Codex и Kimi: по 2 параллельные дорожки на каждого, каждая — 2 порции подряд
cd "${0:A:h}"; C="/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex"; K=/Users/dmitrijmizinov/.kimi-code/bin/kimi
codex_lane() { for k in "$@"; do echo "$(date +%H:%M) codex $k старт" >> run.log; perl -e 'alarm 7200; exec @ARGV' "$C" exec -m gpt-6.1-sol --cd "$PWD" --skip-git-repo-check -s workspace-write -c mcp_servers.n8n-mcp.enabled=false -o "out/codex_${k}_final.md" - < "TASK_codex_$k.md" > "out/codex_$k.log" 2>&1; echo "$(date +%H:%M) codex $k конец" >> run.log; done; }
kimi_lane() { for k in "$@"; do echo "$(date +%H:%M) kimi $k старт" >> run.log; perl -e 'alarm 7200; exec @ARGV' "$K" -p "$(cat TASK_kimi_$k.md)" > "out/kimi_$k.log" 2>&1; echo "$(date +%H:%M) kimi $k конец" >> run.log; done; }
codex_lane 1 3 & codex_lane 2 4 & kimi_lane 1 3 & kimi_lane 2 4 &
wait; echo "$(date +%H:%M) все внешние готовы" >> run.log
