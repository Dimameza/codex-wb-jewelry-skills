"""Карточки 12 близнецов хитов на 1688: цена, ступени, минимальная партия, вес, цвета (фоновая вкладка Chrome; при капче — стоп)."""
import json, subprocess, time, random, os
T = "/Volumes/ADATA SD810/WB/Подбор/1688_данные/tools"; env = dict(os.environ, CBG_MAIN="1")
cb = lambda *a: subprocess.run([f"{T}/chrome_bg.sh", *a], capture_output=True, text=True, timeout=120, env=env).stdout.strip()
tw = json.load(open("twins_selected.json")); out = json.load(open("twins_details.json")) if os.path.exists("twins_details.json") else {}
tid = None
for t in tw:
    oid = t["offer"].split("/")[-1].split(".")[0]
    if oid in out: continue
    if tid is None: tid = cb("open", t["offer"])
    else: cb("nav", tid, t["offer"])
    subprocess.run([f"{T}/wait_ready.sh", tid, "50"], timeout=80); time.sleep(5)
    try: d = json.loads(cb("js", tid, f"{T}/detail_scrape.js"))
    except Exception: d = {"blocked": True}
    if d.get("blocked"): print("СТОП: капча/вход", oid, flush=True); break
    out[oid] = d; json.dump(out, open("twins_details.json", "w"), ensure_ascii=False, indent=1)
    print(oid, d.get("begin_amount"), (d.get("price_block") or "").replace("\n", " ")[:120], flush=True)
    time.sleep(8 + random.random() * 4)
if tid: cb("close", tid)
print("готово", len(out))
