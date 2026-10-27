#!/bin/zsh
# широкий поиск: при капче — час паузы и продолжить (до 8 раз); капчу не трогаем
cd "${0:A:h}"; export CBG_MAIN=1
for r in 1 2 3 4 5 6 7 8; do
  python3 -I kq_wide.py >> kq.log 2>&1 && break
  echo "$(date +%H:%M) пауза час после стопа" >> kq.log
  for m in $(seq 1 60); do sleep 60; done
done
echo "chain_wide готово $(date +%H:%M)" >> kq.log
