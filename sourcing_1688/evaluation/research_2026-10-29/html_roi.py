"""30.10: HTML-отчёт с вкладками — по каждой позиции раскрывающаяся логика ROI по канону и причина решения.
Только чтение: пересчитывает рынок и ROI так же, как price_check_canon.py и consensus_canon.py, ничего не сохраняет в scored.json.
Пишет критерии_2026-10-28/ревью_плана/логика_ROI_2026-10-30.html (один файл, миниатюры внутри)."""
import base64, io, json, os, sys
from collections import defaultdict
from PIL import Image
sys.path.insert(0, os.path.abspath("../wb_price_check_2026-10-28")); _c = os.getcwd(); os.chdir("../wb_price_check_2026-10-28")
from analyze import pool
os.chdir(_c)
from price_check import group
CF = json.load(open("canon_fit.json")); SPP, DRR = 0.35, 0.10
s = json.load(open("scored.json")); con = json.load(open("стили/consensus.json"))
SCP = json.load(open("../wb_price_check_2026-10-28/sculpt/sculpt_pool.json"))["pool"]
F = json.load(open("наборы_серьги/final_sets_canon.json"))
SETS = {"А2/Б колье|подвеска+серьги", "А3 набор 3", "А4 набор 4+", "набор прочий", "кольца набор"}
sk = lambda seg: "набор" if seg in SETS else "колье" if seg in ("колье", "чокер", "подвеска") else "серьги" if seg == "серьги" else None
HIT = {108, 111, 114, 199}
PLAN = {k: json.load(open(f"consensus_plan_{k}.json")) for k in ("cap0", "cap3", "cap3_half70")}
QTY = json.load(open("consensus_qty_cap3_half70.json"))

def roi(P, inv):
    """ROI по канону при цене продавца P (до СПП): (pre − реклама − вложения), с прибыли УСН 15 %."""
    pre = CF["a"] * P + CF["b"]; g = pre - DRR * P - inv; prof = g * 0.85 if g > 0 else g
    return round(pre), round(DRR * P), round(prof), round(100 * prof / inv)

def thumb(n):
    p = f"plan_thumbs/{n:04d}.jpg"
    if not os.path.exists(p): return ""
    im = Image.open(p).convert("RGB"); im.thumbnail((72, 72)); b = io.BytesIO(); im.save(b, "JPEG", quality=70)
    return base64.b64encode(b.getvalue()).decode()

PH = "../критерии_2026-10-28/ревью_плана/логика_ROI_фото"   # 30.10: крупные фото для окна с приближением (рядом с HTML)
def big(job):
    src, dst = job
    if os.path.exists(dst): return
    im = Image.open(src).convert("RGB"); im.thumbnail((1000, 1000)); im.save(dst, "JPEG", quality=80)
def photos():
    from concurrent.futures import ThreadPoolExecutor
    os.makedirs(PH, exist_ok=True)
    jobs = [(src, f"{PH}/{i + 1:04d}_{k + 1}.jpg") for i, r in enumerate(s) for k, src in enumerate(p for p in r.get("imgs") or [] if os.path.exists(p))]
    with ThreadPoolExecutor(8) as pl: list(pl.map(big, jobs))
photos()

# 30.10: аналоги по фото (analogs_embed.py): 3 самые похожие из карточек, которые подтверждают цену, и почти одинаковые — копии
import numpy as np
AW = json.load(open("analogs_wb.json")); EM = np.load("analogs_emb.npz"); WBI = {x["nm"]: k for k, x in enumerate(AW)}
SIM = np.maximum(EM["ours"] @ EM["wb"].T, EM["ours34"] @ EM["wb"].T)   # косинус CLIP, 1485 × карточки WB (фото целиком и обрезанное до 3:4)
ORB = json.load(open("analogs_orb.json"))   # копии: совпадение точек фото ORB + RANSAC (analogs_orb.py); ≥30 — то же фото, 10–29 — похожая модель
COPY, NEAR = 30, 10
EYEA = json.load(open("eye_analogs/eye_analogs.json")) if os.path.exists("eye_analogs/eye_analogs.json") else {}   # 30.10: аналоги проверены глазами (0 далеко, 1 близко, 2 та же вещь)
USED = set()
def card(nm, i):
    k = WBI.get(str(nm))
    if k is None: return None
    USED.add(str(nm)); return dict(nm=str(nm), sim=round(float(SIM[i, k]), 3))
def pct(v, q): return v[min(len(v) - 1, int(q * len(v)))] if v else None

cache, rows_out = {}, []
for i, r in enumerate(s):
    n = i + 1; st_ = con[str(n)]["основной"]; qs, _ = group(r["seg"], st_)
    if st_ == "SCULPT" and sk(r["seg"]): key = ("S", sk(r["seg"])); qs = [f"скульптурное золото — {sk(r['seg'])} (аналоги глазами)"]
    else: key = ("Q",) + tuple(qs)
    if key not in cache: cache[key] = SCP[key[1]] if key[0] == "S" else pool(qs)
    rows = cache[key]; pack = 20 if r["seg"] in SETS else 0
    inv = 12.72 * r["cny"] + 22 + 0.285 * r["w"] + pack; need = (inv * CF["k"] - CF["b"]) / (CF["a"] - DRR); thr = need * (1 - SPP)
    assert round(need) == r["need_canon"], n
    hot = sorted(x["price"] for x in rows if x["orders30"] >= 30); med = hot[len(hot) // 2] if hot else None
    okr = [x for x in rows if x["orders30"] >= 30 and x["price"] >= thr]; fr = sum((x.get("rating_cnt") or 0) < 100 for x in okr)
    Pm = med / (1 - SPP) if med else None
    hotr = [x for x in rows if x["orders30"] >= 30]
    sup = sorted((c for c in (card(x["nm"], i) for x in okr) if c), key=lambda c: -c["sim"])
    low = sorted((c for c in (card(x["nm"], i) for x in hotr if x["price"] < thr) if c), key=lambda c: -c["sim"])
    cp = [dict(card(nm, i), orb=v, same=v >= COPY) for nm, v in ORB.get(str(n), []) if v >= NEAR]
    cpn = {c["nm"] for c in cp if c["same"]}; sup = [c for c in sup if c["nm"] not in cpn]; low = [c for c in low if c["nm"] not in cpn]   # копии показаны отдельно
    an = [dict(c, ok=1) for c in sup[:3]] + [dict(c, ok=0) for c in low[:max(0, 3 - len(sup))]]
    like = card(r["like"], i) if r.get("like") else None
    top = card(AW[int(np.argmax(SIM[i]))]["nm"], i)
    rows_out.append(dict(
        n=n, order=r["order"], row=r["row"], seg=r["seg"], style=r.get("style") or "", name=(r.get("descr") or {}).get("claude") or r.get("note") or "",
        cn=r["title"], url=r["url"], cny=r["cny"], w=r["w"], wsrc=r["wsrc"], pack=pack,
        yuan=round(12.72 * r["cny"]), cargo=round(0.285 * r["w"]), inv=round(inv), need=round(need), thr=round(thr),
        q0=qs[0] if qs else r["seg"], hot=len(hot), ok=len(okr), fresh=fr, med=med, Pm=round(Pm) if Pm else None,
        rm=roi(Pm, inv) if Pm else None, rn=roi(need, inv), hr=r.get("headroom"), total=r["total"],
        R=r["R"], stops=r["stops"], dec=r["decisionCANON"], why=r["whyCANON"], eye=r.get("eye"), hit=n in HIT,
        plan={k: PLAN[k].get(str(n)) for k in PLAN}, qty=QTY.get(str(n), 0), img=thumb(n), ph=sum(os.path.exists(p) for p in r.get("imgs") or []),
        dist=[pct(hot, q) for q in (0, .25, .5, .75)] + [hot[-1] if hot else None], an=an, cp=cp, like=like, top=top, nwb=len(AW), eyea=EYEA.get(str(n)), psrc=r["psrc"], P0=r["P"], qs=qs))

# место в группе «рынок × стиль» для тестов (как в consensus_canon.py)
T = defaultdict(list)
for x in rows_out:
    p = x["plan"]["cap0"]
    if p and p[0].startswith("тест"): T[(s[x["n"] - 1]["wbq_spp"]["запросы"][0] if s[x["n"] - 1]["wbq_spp"]["запросы"] else x["seg"], con[str(x["n"])]["основной"])].append((x["hr"] or 0, x["n"]))
RANK = {}
for (q, stl), v in T.items():
    v.sort(reverse=True)
    for j, (hr, n) in enumerate(v): RANK[n] = (j + 1, len(v), q, stl)
for x in rows_out: x["rank"] = RANK.get(x["n"])

sets = sorted([c for c in F if c["ok_canon"] and c["eye"]], key=lambda c: c["need_canon"])[:15]
setmeta = []
W = lambda k: s[k - 1]["w"]
for c in F:
    inv = 12.72 * c["cny"] + 22 + 0.285 * (W(c["neck"]) + W(c["ear"])) + 20
    med = c["headroom"] * c["thr_canon"] if c["headroom"] else None; Pm = med / (1 - SPP) if med else None
    setmeta.append(dict(neck=c["neck"], ear=c["ear"], cny=c["cny"], inv=round(inv), need=c["need_canon"], thr=c["thr_canon"], market=c["market_canon"],
                        fresh=c["fresh_canon"], ok=c["ok_canon"], eye=c["eye"], hr=c["headroom"], med=round(med) if med else None, Pm=round(Pm) if Pm else None,
                        rm=roi(Pm, inv) if Pm else None, inplan=c in sets, sim=c.get("sim")))

WBD = {x["nm"]: {k: x[k] for k in ("name", "price", "orders30", "rating_cnt", "url", "img")} for x in AW if x["nm"] in USED}
DATA = dict(items=rows_out, sets=setmeta, cf=CF, spp=SPP, drr=DRR, wb=WBD)
html = open("html_roi_template.html", encoding="utf-8").read().replace("/*DATA*/null", json.dumps(DATA, ensure_ascii=False))
out = "../критерии_2026-10-28/ревью_плана/логика_ROI_2026-10-30.html"
open(out, "w", encoding="utf-8").write(html)
print("позиций", len(rows_out), "наборов", len(setmeta), "в плане", len(sets), "размер МБ", round(os.path.getsize(out) / 1e6, 1))
