"""Цена основного варианта и вес по карточкам 64 лучших: одна вкладка в конце основного окна, переход раз в 11 с."""
import json, os, random, subprocess, sys, time
W = os.path.dirname(os.path.abspath(__file__)); T = "/Volumes/ADATA SD810/WB/Подбор/1688_данные/tools"
env = dict(os.environ, CBG_MAIN="1")
cb = lambda *a: subprocess.run([f"{T}/chrome_bg.sh", *a], capture_output=True, text=True, timeout=120, env=env).stdout.strip()
ids = json.load(open(f"{W}/best_ids.json"))
out = json.load(open(f"{W}/details.json")) if os.path.exists(f"{W}/details.json") else {}
todo = [i for i in ids if i not in out]
tid = None


def save():   # 27.10: атомарно (обрыв записи стёр 1073 карточки) и раз в 10 карточек — файл 5 МБ, перезапись на каждой тормозила
    json.dump(out, open(f"{W}/details.json.tmp", "w"), ensure_ascii=False); os.replace(f"{W}/details.json.tmp", f"{W}/details.json")


import atexit, signal
atexit.register(save); signal.signal(signal.SIGTERM, lambda *a: sys.exit(0))
for n, i in enumerate(todo):
    url = f"https://detail.1688.com/offer/{i}.html"
    if tid is None:
        tid = cb("open", url)
    else:
        cb("nav", tid, url)
    subprocess.run([f"{T}/wait_ready.sh", tid, "50"], timeout=80); time.sleep(3)
    raw = cb("js", tid, f"{T}/detail_scrape.js")
    try:
        d = json.loads(raw)
    except Exception:
        d = {"blocked": True, "raw": raw[:200]}
    if d.get("blocked"):
        print("СТОП: капча/вход на", i, flush=True); break
    out[i] = d
    if (n + 1) % 10 == 0:
        save()
    print(n + 1, len(todo), i, d.get("sku_price_scale"), (d.get("weights") or "")[:60].replace("\n", " | "), flush=True)
    time.sleep(11 + random.random() * 3)
if tid:
    cb("close", tid)
print("готово", len(out))
