"""Добор фото кандидатов 1688: повторно запросить страницы витрины (tradenumdown/timedown), где лежат нужные id.
python3 img_backfill.py <pool_1688.json> <factories_dir>"""
import json, os, subprocess, sys, time
T = os.path.dirname(os.path.abspath(__file__)); POOL, F = sys.argv[1], sys.argv[2]
cb = lambda *a, timeout=120: subprocess.run([f"{T}/chrome_bg.sh", *a], capture_output=True, text=True, timeout=timeout).stdout.strip()
pool = json.load(open(POOL)); fac = {f["code"]: f for f in json.load(open(f"{F}/factories.json"))}
need = {}
for p in pool:
    if p.get("img"):
        continue
    d = json.load(open(f"{F}/shops/{p['shop']}.json")); r = next((x for x in d["rows"] if x["id"] == p["id"]), None)
    if r:
        need.setdefault(p["shop"], {}).setdefault((r.get("src") or "trade", r["page"]), []).append(p["id"])
print("нужно фото", sum(len(v) for s in need.values() for v in s.values()), "страниц", sum(len(s) for s in need.values()), flush=True)
first = next(iter(need))
tid = cb("open", f"https://{fac[first]['host']}/page/offerlist.htm"); subprocess.run([f"{T}/wait_ready.sh", tid, "60"]); time.sleep(4)
cb("main", tid, f"{T}/shop_scan.js")
js = """(async()=>{const r={};for(const [mem,sort,pn] of %s){const ct=await window.__req(mem,sort,pn);if(!ct){r.err=sort+pn;break;}
for(const o of (ct.offerList||[])){const u=JSON.stringify(o.offerImages||'').match(/ibank\\/[^"\\\\]+?\\.(?:jpg|jpeg|png|webp)/i);if(u)r[o.id]='https://cbu01.alicdn.com/img/'+u[0];}
await new Promise(x=>setTimeout(x,5000));}window.__put('bf',JSON.stringify(r));})()"""
imgs = {}
for shop, pages in need.items():
    jobs = [[fac[shop]["mem"], "tradenumdown" if src == "trade" else "timedown", pn] for (src, pn) in pages]
    cb("main", tid, "window.__put('bf','')"); cb("main", tid, js % json.dumps(jobs))
    for _ in range(60):
        time.sleep(5); out = cb("get", tid, "bf")
        if out:
            break
    r = json.loads(out or "{}"); err = r.pop("err", None); imgs.update(r)
    print(shop, "стр", len(jobs), "фото", len(r), "ошибка " + err if err else "", flush=True)
    if err:
        break
    time.sleep(15)
cb("close", tid)
for p in pool:
    if not p.get("img") and p["id"] in imgs:
        p["img"] = imgs[p["id"]]
json.dump(pool, open(POOL, "w"), ensure_ascii=False, indent=1)
print("с фото", sum(1 for p in pool if p.get("img")), "из", len(pool))
