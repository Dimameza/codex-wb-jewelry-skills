"""Заказ 1000 (26.10): офферы широкого поиска 1688 → кандидаты для Codex порциями.
python wide_prep.py [--final]  — собирает всё новое; если набралось ≥ CHUNK (или --final), пишет следующую порцию codex_input_wN.json + TASK_codex_wN.md."""
import glob, json, os, re, subprocess, sys, shutil
W = os.path.dirname(os.path.abspath(__file__)); K = "/Volumes/ADATA SD810/WB/Подбор/1688_данные/wide_2026-10-26"
CHUNK = int(os.environ.get("CHUNK", "350"))   # 27.10: комплекты — порции меньше
src = open(f"{W}/match.py").read(); exec(src[src.index("BAD ="):src.index("known = set()")])   # BAD, SILVER, seg_cn — общие правила
os.makedirs(f"{W}/wide_img", exist_ok=True)
seen = {p["id"] for p in json.load(open(f"{W}/pool_1688.json"))}            # уже оценённые/известные
seen |= {x["id"] for x in json.load(open(f"{W}/kq_sets.json"))}
done = set()
for f in glob.glob(f"{W}/codex_input_w*.json"):
    for s in json.load(open(f))["segments"].values():
        done |= {c["id"] for c in s["candidates"]}
cand = {}
KQ_DIRS = [K, "/Volumes/ADATA SD810/WB/Подбор/1688_данные/sets_2026-10-27"]   # 27.10: + поиск комплектов (добор до 300)
SETS_ONLY = bool(os.environ.get("SETS_ONLY"))   # 27.10: только наборы с колье
SETSEG = {"А2/Б колье|подвеска+серьги", "А3 набор 3", "А4 набор 4+", "набор прочий"}
for f in sorted(f for k in KQ_DIRS for f in glob.glob(f"{k}/kq/*.json")):
    if os.path.basename(f).startswith("._"):
        continue
    d = json.load(open(f))
    for r in d.get("rows", []):
        i = r.get("offerId"); t = r.get("title") or ""
        if not i or i in seen or i in done or i in cand or BAD.search(t) or SILVER.search(t):
            continue
        try:
            p = float(re.findall(r"[\d.]+", r.get("price") or "")[0])
        except IndexError:
            continue
        tr = int(re.sub(r"\D", "", r.get("trade") or "") or 0)
        s = seg_cn(t)
        if not (5 <= p <= 30) or tr < 30 or s in ("прочее", "кольцо", "браслет", "кольца набор"):
            continue   # 26.10: браслеты зимой не берут (владелец)
        if SETS_ONLY and s not in SETSEG:
            continue
        if s == "набор прочий" and not any(w in t for w in ("项链", "项圈", "颈链", "锁骨链", "吊坠", "毛衣链")):
            continue   # набор без колье (браслет+кольцо и т. п.) — не основа
        cand[i] = {"id": i, "title": t, "price": p, "s30": tr, "seg": s, "shop": r.get("shop"), "img": r.get("img"), "kw": d.get("kw"),
                   "url": f"https://detail.1688.com/offer/{i}.html"}
final = "--final" in sys.argv
try:   # 26.10: защита от одновременного запуска (иначе дубль порции и битый пул)
    os.mkdir(f"{W}/wide_prep.lock")
except FileExistsError:
    sys.exit(print("wide_prep уже работает — пропуск"))
import atexit; atexit.register(lambda: os.rmdir(f"{W}/wide_prep.lock"))
print("новых кандидатов", len(cand), "в порциях уже", len(done))
if len(cand) < CHUNK and not (final and cand):
    sys.exit(0)
MAIN = {"колье", "чокер", "подвеска", "бусы", "А2/Б колье|подвеска+серьги", "А3 набор 3", "А4 набор 4+", "набор прочий", "Г крест"}
L = sorted(cand.values(), key=lambda x: (x["seg"] not in MAIN, -x["s30"]))[:CHUNK]   # основа — колье и комплекты
from concurrent.futures import ThreadPoolExecutor
def get(c):
    fn = f"{W}/wide_img/{c['id']}.jpg"
    if not os.path.exists(fn):
        subprocess.run(["curl", "-s", "-m", "20", "-o", fn, c["img"].replace(".220x220", "")])
with ThreadPoolExecutor(6) as ex:
    list(ex.map(get, L))
wb = json.load(open(f"{W}/wb_slice.json")); segs = {}
for c in L:
    if os.path.exists(f"{W}/wide_img/{c['id']}.jpg") and os.path.getsize(f"{W}/wide_img/{c['id']}.jpg") > 2000:
        segs.setdefault(c["seg"], []).append(c)
n = len(glob.glob(f"{W}/codex_input_w*.json")) + 1
out = {}
for s, cs in segs.items():
    refs = sorted([r for r in wb["rows"] if r["seg"] == s and (r.get("price") or 0) >= 500], key=lambda r: -(r["orders30"] or 0))[:6]
    for r in refs:
        a, b = f"{W}/codex6/wb_{r['nm']}.jpg", f"{W}/wide_img/wb_{r['nm']}.jpg"
        if os.path.exists(a) and not os.path.exists(b):
            shutil.copy(a, b)
        elif not os.path.exists(b) and r.get("img"):
            subprocess.run(["curl", "-s", "-m", "20", "-o", b, r["img"].replace("c516x688", "c246x328")])
    out[s] = {"wb_refs": [{k: r.get(k) for k in ("nm", "name", "price", "orders30")} for r in refs], "candidates": cs}
if not out:
    sys.exit(print("нет кандидатов с фото — порцию не создаю"))   # 27.10: иначе конвейер плодит пустые порции
json.dump({"segments": out}, open(f"{W}/codex_input_w{n}.json", "w"), ensure_ascii=False, indent=1)
pool = json.load(open(f"{W}/pool_1688.json"))   # кандидаты порции — в общий пул (черновик заказа берёт цену/сегмент оттуда)
pool += [{"seg": c["seg"], "shop": (c["shop"] or "").replace(".1688.com", ""), "shop_name": "", "id": c["id"], "price": c["price"], "s30": c["s30"],
          "sold_cum": None, "new90": False, "title": c["title"], "img": c["img"], "known": False, "wb_check_med": None, "wb_med_orders": None,
          "ceil_cny_roi200": None, "ceil_cny_top": None, "fits": True, "fits_top": True, "url": c["url"], "src": f"широкий поиск 26.10 · {c['kw']}"}
         for cs in out.values() for c in cs["candidates"]]
json.dump(pool, open(f"{W}/pool_1688.json", "w"), ensure_ascii=False, indent=1)
task = open(f"{W}/TASK_codex_taste6.md").read().replace("codex6/", "wide_img/").replace("codex_input6.json", f"codex_input_w{n}.json").replace("codex_taste6.json", f"codex_taste_w{n}.json")
task += "\n\nВАЖНО (26.10): профиль шире — taste 3 тоже идёт в заказ, ставь 3 честно для «нормально, не против профиля». Для каждого кандидата обязательно like_wb (ближайший бестселлер из wb_refs сегмента), если похожий есть.\n"
open(f"{W}/TASK_codex_w{n}.md", "w").write(task)
print("порция", n, "кандидатов", sum(len(v["candidates"]) for v in out.values()), {s: len(v["candidates"]) for s, v in out.items()})
