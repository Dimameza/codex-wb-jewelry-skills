"""29.10: докачка 16 позиций заказа 100 без карточки (по образцу refetch.py). 28.10: перекачка карточек 1688, восстановленных из черновика после обрыва details.json (нет размеров, веса, сплава, вариантов).
Пишет в details_refetch.json атомарно; сначала позиции из плана; при капче — стоп."""
import json, os, random, subprocess, sys, time, atexit, signal
W = os.path.dirname(os.path.abspath(__file__)); T = "/Volumes/ADATA SD810/WB/Подбор/1688_данные/tools"
env = dict(os.environ, CBG_MAIN="1")
cb = lambda *a: subprocess.run([f"{T}/chrome_bg.sh", *a], capture_output=True, text=True, timeout=120, env=env).stdout.strip()
ids = json.load(open(f"{W}/refetch_ids16.json")); F = f"{W}/details_refetch.json"
out = json.load(open(F)) if os.path.exists(F) else {}
def save(): json.dump(out, open(F + ".tmp", "w"), ensure_ascii=False); os.replace(F + ".tmp", F)
atexit.register(save); signal.signal(signal.SIGTERM, lambda *a: sys.exit(0))
_o2 = f"{W}/details_refetch2.json"   # второй поток идёт с конца списка
todo = [i for i in ids if i not in out]; tid = None
for n, i in enumerate(todo):
    if n % 10 == 0 and os.path.exists(_o2) and i in json.load(open(_o2)): print("встретились со вторым потоком", flush=True); break
    url = f"https://detail.1688.com/offer/{i}.html"
    tid = cb("open", url) if tid is None else (cb("nav", tid, url) or tid)
    subprocess.run([f"{T}/wait_ready.sh", tid, "50"], timeout=80); time.sleep(3)
    try: d = json.loads(cb("js", tid, f"{T}/detail_scrape.js"))
    except Exception: d = {"blocked": True}
    if "chrome-error" in (d.get("url") or ""):
        time.sleep(60); continue
    if d.get("blocked"): print("СТОП: капча/вход на", i, flush=True); break
    out[i] = d
    if (n + 1) % 10 == 0: save()
    print(n + 1, len(todo), i, bool(d.get("weights")), flush=True)
    time.sleep(9 + random.random() * 3)
if tid: cb("close", tid)
print("готово", len(out), flush=True)
