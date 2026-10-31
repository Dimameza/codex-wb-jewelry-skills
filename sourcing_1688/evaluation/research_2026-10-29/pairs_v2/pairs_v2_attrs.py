"""31.10: подбор серёг к колье по ТЗ v1 (ТЗ_подбор_серёг_к_колье_2026-10-31.md), шаги 1–5.
Колье — 56 колье пула наборов (те же, что в final_sets_before_rematch.json). Серьги — все позиции сегмента «серьги» без стоп-факторов.
Признаки (п. 4 ТЗ) — из трёх описаний фото: признак засчитывается, если его называют ≥2 описания; металл — metal.json; масштаб — слова + вес.
Кандидаты — серьги, которые проходят правила 5.2–5.5 по признакам; ранжирование — число общих признаков (5.6), затем CLIP. Пишет
pairs_v2_attrs.json и pair_sheets/c_NN.jpg (колье + до 8 кандидатов)."""
import json, os, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont
os.chdir(os.path.dirname(os.path.abspath(__file__)))
s = json.load(open("../scored.json")); M = json.load(open("../metal.json"))["ours"]; E = np.load("../analogs_emb.npz")
NECK = sorted({c["neck"] for c in json.load(open("final_sets_before_rematch.json"))})
NATIVE = [84, 481, 500, 509, 540, 545, 577, 585]; ALREADY = [79, 595]
EARS = [i + 1 for i, r in enumerate(s) if r["seg"] == "серьги" and not r["stops"]]
INS = {"жемчуг": r"жемчуг|перламутр", "страз": r"страз|кристалл|циркон|фианит", "эмаль": r"эмал", "смола": r"смол|янтар|акрил",
       "камень": r"камн|камен|кабошон|изумруд|рубин|оникс|бирюз|агат|малахит", "бусины": r"бусин|бусы"}
COL = {"белый": r"бел|прозрач|молочн", "чёрный": r"чёрн|черн", "красный": r"красн|бордо|вишн|рубин", "зелёный": r"зелён|зелен|изумруд|малахит",
       "синий": r"син|голуб|бирюз", "розовый": r"розов", "коричневый": r"коричн|янтар|карамел|тигров"}
SHP = {"круг": r"кругл|диск|монет", "овал": r"овал", "капля": r"капл", "кольцо": r"кольц|обруч|хуп|колечк", "квадрат": r"квадрат", "прямоугольник": r"прямоуг",
       "ромб": r"ромб", "треугольник": r"треугол", "сердце": r"сердц", "цветок": r"цвет[оык]|лепест|роз[аы]\b", "лист": r"лист", "звезда": r"звезд|солнц",
       "бант": r"бант", "спираль": r"спирал|завит", "волна": r"волн|изогн", "органика": r"мят|жидк|органическ|неровн|расплав"}
ROUND = {"круг", "овал", "капля", "кольцо", "сердце", "волна", "спираль", "органика"}; ANGLE = {"квадрат", "прямоугольник", "ромб", "треугольник"}
TEX = {"гладкая": r"гладк|зеркальн|полирован", "мятая": r"мят|жидк|расплав|органическ", "молотковая": r"молотк|чекан|рельефн|фактурн", "рифлёная": r"рифл|полос|ребрист", "ажурная": r"ажур|филигр"}
MOT = {"цветок": SHP["цветок"], "лист": SHP["лист"], "сердце": SHP["сердце"], "бант": SHP["бант"], "звезда": SHP["звезда"], "змея": r"зме", "монета": r"монет", "крест": r"крест"}
def votes(r, pat):
    d = [(v or "").lower() for v in (r.get("descr") or {}).values()]; return sum(bool(re.search(pat, x)) for x in d)
def attrs(n):
    r = s[n - 1]; neck = r["seg"] != "серьги"; k = lambda pat: votes(r, pat) >= 2
    ins = sorted(t for t, p in INS.items() if k(p)); col = sorted(t for t, p in COL.items() if k(p)) if ins else []
    shp = sorted(t for t, p in SHP.items() if k(p)); tex = sorted(t for t, p in TEX.items() if k(p)); mot = sorted(t for t, p in MOT.items() if k(p))
    fam = "округлое" if shp and set(shp) <= ROUND else "угловатое" if shp and set(shp) <= ANGLE else "смешанное" if shp else "?"
    w = r["w"]; wsc = (0 if w <= 15 else 1 if w <= 40 else 2 if w <= 80 else 3) if neck else (0 if w <= 8 else 1 if w <= 20 else 2 if w <= 35 else 3)
    words = votes(r, r"мелк|изящн|тонк|миниатюр|небольш"), votes(r, r"средн"), votes(r, r"крупн"), votes(r, r"массивн|statement|гигант|огромн")
    dsc = max(range(4), key=lambda j: (words[j], -abs(j - wsc))) if max(words) >= 2 else wsc
    return dict(n=n, metal=M[str(n)], ins=ins, col=col, shape=shp, fam=fam, tex=tex, mot=mot, w=w, scale_w=wsc, scale=dsc, wsrc=r["wsrc"])
SC = ["изящный", "средний", "крупный", "массивный"]
A = {n: attrs(n) for n in NECK + EARS}
def rules(a, b):
    """Правила 5.2–5.5 по признакам; None — проходит, иначе причина отказа."""
    if a["metal"] != b["metal"] and "other" not in (a["metal"], b["metal"]): return "металл"
    if abs(a["scale"] - b["scale"]) > 1: return "масштаб"
    if a["scale"] == 0 and b["scale"] >= 2: return "к изящному — крупные"
    if {a["fam"], b["fam"]} == {"округлое", "угловатое"}: return "форма"
    if a["ins"] and not set(a["ins"]) & set(b["ins"]): return "нет вставки того же типа"
    if a["ins"] and a["col"] and b["col"] and not set(a["col"]) & set(b["col"]): return "цвет вставки"
    if not a["ins"] and set(b["ins"]) & {"камень", "смола", "эмаль"}: return "крупная вставка к колье без вставок"
    return None
def common(a, b):
    c = [f"мотив: {x}" for x in set(a["mot"]) & set(b["mot"])] + [f"вставка: {x}" for x in set(a["ins"]) & set(b["ins"])]
    c += [f"фактура: {x}" for x in set(a["tex"]) & set(b["tex"]) if x != "гладкая"] + [f"форма: {x}" for x in set(a["shape"]) & set(b["shape"])]
    return c
OUT = {"native": NATIVE, "already_set": ALREADY, "neck": {}}
todo = [n for n in NECK if n not in NATIVE + ALREADY]
for n in todo:
    a = A[n]; cand, rej = [], {}
    for e in EARS:
        why = rules(a, A[e])
        if why: rej[why] = rej.get(why, 0) + 1; continue
        cand.append((len(common(a, A[e])), float(E["ours"][n - 1] @ E["ours"][e - 1]), e))
    cand.sort(reverse=True)
    OUT["neck"][str(n)] = dict(attrs=a, rejected=rej, cand=[dict(e=e, common=common(a, A[e]), sim=round(sim, 3), attrs=A[e]) for _, sim, e in cand[:8]], n_pass=len(cand))
json.dump(OUT, open("pairs_v2_attrs.json", "w"), ensure_ascii=False, indent=1)
# листы: колье + 8 кандидатов, под каждой карточкой — масштаб и общий признак
P = "../../критерии_2026-10-28/ревью_плана/логика_ROI_фото/"; os.makedirs("pair_sheets", exist_ok=True)
F = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 16); C = 160
def tile(n, lab, col, sub):
    t = Image.new("RGB", (C, C + 24), "white"); im = Image.open(f"{P}{n:04d}_1.jpg").convert("RGB"); im.thumbnail((C, C)); t.paste(im, ((C - im.width) // 2, (C - im.height) // 2))
    d = ImageDraw.Draw(t); d.rectangle([0, 0, 10 + 10 * len(lab), 21], fill=col); d.text((3, 1), lab, fill="white", font=F); d.text((3, C + 3), sub[:22], fill="black", font=F); return t
for k in range(0, len(todo), 4):
    part = todo[k:k + 4]; sh = Image.new("RGB", (9 * C, len(part) * (C + 24)), "#888")
    for j, n in enumerate(part):
        o = OUT["neck"][str(n)]; sh.paste(tile(n, str(n), "#d02020", SC[o["attrs"]["scale"]]), (0, j * (C + 24)))
        for m, c in enumerate(o["cand"]): sh.paste(tile(c["e"], f"{'abcdefgh'[m]} {c['e']}", "#333", SC[c["attrs"]["scale"]]), ((m + 1) * C, j * (C + 24)))
    sh.save(f"pair_sheets/c_{k // 4 + 1:02d}.jpg", quality=85)
print("колье на подбор", len(todo), "| серёг", len(EARS), "| без кандидатов:", [n for n in todo if not OUT["neck"][str(n)]["cand"]],
      "| кандидатов по правилам (медиана):", sorted(OUT["neck"][str(n)]["n_pass"] for n in todo)[len(todo) // 2], "| листов", (len(todo) + 3) // 4)
