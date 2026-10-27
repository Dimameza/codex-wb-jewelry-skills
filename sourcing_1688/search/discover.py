"""Фабрики комплектов (24.10): поиск 1688 по наборам: стилевые запросы × 2 страницы, магазины с наибольшими сделками, которых нет среди известных."""
import json, os, random, re, subprocess, time
D = os.path.dirname(os.path.abspath(__file__)); T = "/Volumes/ADATA SD810/WB/Подбор/1688_данные/tools"
env = dict(os.environ, CBG_MAIN="1")
cb = lambda *a: subprocess.run([f"{T}/chrome_bg.sh", *a], capture_output=True, text=True, timeout=120, env=env).stdout.strip()
KW = ["欧美 项链耳环 套装", "欧美 三件套 首饰", "四件套 首饰 欧美", "轻奢 项链耳环 套装 女", "复古 金色 项链耳环 套装", "夸张 金属 套装 首饰",
      "黑色 珐琅 套装 项链 耳环", "珍珠 项链耳环 套装 金色", "巴洛克珍珠 套装", "液态金属 项链 耳环 套装", "褶皱 金属 套装", "手镯 戒指 套装 欧美",
      "项链 手链 套装 金色", "项链 手链 耳环 三件套", "颈圈 耳环 套装", "蛇骨链 套装", "水钻 套装 欧美 夸张", "锆石 套装 轻奢 项链 手链",
      "复古 宝石 套装 项链耳环", "黑玛瑙 套装", "叠戴 项链 套装 多层", "戒指 套装 欧美 金属", "多件套 戒指 夸张", "手镯 套装 叠戴 金属",
      "两件套 项链耳环 欧美", "饰品套装 外贸 欧美", "跨境 首饰 套装 欧美", "法式 复古 套装 项链 耳环 手镯", "几何 金属 套装 夸张", "Y字链 套装"]
known = set()
for f in ["/Volumes/ADATA SD810/WB/Подбор/1688_данные/factories_2026-10-22/factories.json", "/Volumes/ADATA SD810/WB/Подбор/1688_данные/factories_2026-10-23/factories.json"]:
    known |= {x["host"].replace(".1688.com", "") for x in json.load(open(f))}
tid = None; shops = {}
for i, kw in enumerate(KW):
    for pg in (1, 2):
        fn = f"{D}/kq/{i:02d}_{pg}.json"
        if not os.path.exists(fn):
            url = "https://s.1688.com/kq/-" + kw.encode("gb18030").hex().upper() + ".html" + ("" if pg == 1 else "?beginPage=2")
            if tid is None: tid = cb("open", url)
            else: cb("nav", tid, url)
            subprocess.run([f"{T}/wait_ready.sh", tid, "50"], timeout=80); time.sleep(3)
            raw = cb("js", tid, f"{T}/kq_scrape.js")
            try: d = json.loads(raw)
            except Exception: d = {"blocked": True}
            if d.get("blocked"):
                print("СТОП: капча на", kw, pg, flush=True); break
            json.dump(d, open(fn, "w"), ensure_ascii=False)
            print(i, pg, kw, d.get("n"), flush=True)
            time.sleep(9 + random.random() * 4)
        d = json.load(open(fn))
        for r in d.get("rows", []):
            h = (r.get("shop") or "").replace(".1688.com", "")
            if not h or h in known: continue
            deals = int(re.sub(r"\D", "", r.get("trade") or "0") or 0)
            s = shops.setdefault(h, {"host": h + ".1688.com", "name": (r.get("company") or "").split("\n")[0], "deals": 0, "hits": 0, "kws": set()})
            s["deals"] += deals; s["hits"] += 1; s["kws"].add(kw)
    else:
        continue
    break
if tid: cb("close", tid)
top = sorted(shops.values(), key=lambda s: -(s["deals"] + 300 * len(s["kws"])))[:45]
for s in top: s["kws"] = sorted(s["kws"])
json.dump(top, open(f"{D}/new_shops.json", "w"), ensure_ascii=False, indent=1)
open(f"{D}/factories.tsv", "w").write("".join(f"N{i:02d}\t{s['host']}\t\t{s['name']}\n" for i, s in enumerate(top)))
print("новых магазинов", len(shops), "взято", len(top))
