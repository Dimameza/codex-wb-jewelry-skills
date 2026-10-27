"""Черновик заказа из лучших по вкусу (Kimi): цена/вес с карточек 1688, цена продажи — по похожему хиту WB, ROI — модель ТЗ 06.10.
ROI = (0,0343·P − 6,30) / ((22 + 0,285·вес_г)/12,72 + ¥) − 1   (восстановлено по 55 строкам ТЗ, погрешность ±0,16 ¥)"""
import json, os, re, statistics as st, sys
from openpyxl import Workbook
from openpyxl.drawing.image import Image as XImage
from openpyxl.styles import Alignment, Font, PatternFill
from PIL import Image

W = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1]
pool = {p["id"]: p for p in json.load(open(f"{W}/pool_1688.json"))}
taste = json.load(open(f"{W}/kimi_taste.json"))
import glob
for extra in ["kimi_taste3.json", "kimi_taste4.json", "kimi_taste5.json", "codex_taste6.json", "codex_taste6a.json", "codex_taste6b.json"] + sorted(os.path.basename(f) for f in glob.glob(f"{W}/codex_taste_w*.json")):   # волны Kimi/Codex + широкий поиск 26.10
    if os.path.exists(f"{W}/{extra}"):
        for k, v in json.load(open(f"{W}/{extra}")).items():
            if v.get("taste") is not None:
                taste.setdefault(k, v)
det = json.load(open(f"{W}/details.json"))
wb = json.load(open(f"{W}/wb_slice.json"))
wbrow = {r["nm"]: r for r in wb["rows"]}
segchk = {s["seg"]: s["check_med"] for s in wb["segments"]}
SEGDIR = json.load(open(f"{W}/seg_dirs.json"))
WDEF = {"А3 набор 3": 60, "А4 набор 4+": 80, "А2/Б колье|подвеска+серьги": 35, "Г крест": 20, "колье": 30, "чокер": 30, "серьги": 15, "бусы": 40, "подвеска": 15, "набор прочий": 60}


def roi(P, y, w):
    return ((0.0343 * P - 6.30) / ((22 + 0.285 * w) / 12.72 + y) - 1) * 100


def nums(s):
    return [float(x) for x in re.findall(r"\d+(?:\.\d+)?", s or "")]


def weight(d, seg):
    t = d.get("weights") or ""
    if "重量" not in t:
        return WDEF.get(seg, 40), "допущение"
    rows = t.split("\n")[1:]
    ws = []
    for r in rows:
        if r.startswith("商品详情"):
            break
        n = nums(r)
        if n:
            ws.append(n[-1])
    ws = [x for x in ws if 2 < x <= 300]   # больше 300 г у бижутерии — ошибка разбора (например, «2026年»)
    return (st.median(ws), "карточка") if ws else (WDEF.get(seg, 40), "заглушка → допущение")


rows, seen_dupe = [], set()
PR0 = json.load(open(f"{W}/photo_review.json")) if os.path.exists(f"{W}/photo_review.json") else {}
for pid, v in taste.items():
    t_ok = (v.get("taste") or 0) >= 4 or ((v.get("taste") or 0) == 3 and PR0.get(pid, {}).get("v", "").startswith("ок"))   # вкус 3 — только прошедшие фото (24.10)
    if not t_ok or pid not in pool or pid not in det:   # в черновик — только с ценой и весом с карточки
        continue
    p = pool[pid]
    d = det.get(pid, {})
    y = max(nums(d.get("sku_price_scale"))) if nums(d.get("sku_price_scale")) else p["price"]
    w, wsrc = weight(d, p["seg"])
    ref = wbrow.get(str(v.get("like_wb") or ""))
    if ref and ref.get("orders30"):
        P, psrc = ref["rub30"] / ref["orders30"], f"чек хита WB {ref['nm']}"
    else:
        P, psrc = segchk.get(p["seg"]) or 700, "медиана сегмента (похожего хита нет)"
    if P > 1600:   # дорогой хит (натуральный жемчуг и т.п.) завышает ROI — потолок цены 1 600 ₽ (верхний ярус владельца 1 300–1 420)
        P, psrc = 1600, psrc + " → урезана до 1 600"
    r = roi(P, y, w)
    dup = re.search(r"дубл\w*\s*(\d{10,13})", v.get("why") or "")
    rows.append({"id": pid, "seg": p["seg"], "price": y, "w": w, "wsrc": wsrc, "s30": p["s30"], "taste": v["taste"], "like": v.get("like_score"),
                 "why": v.get("why"), "ref": ref, "P": round(P), "psrc": psrc, "roi": round(r), "url": p["url"], "shop": p["shop"],
                 "dup_of": dup.group(1) if dup else None, "img": f"{W}/img/{SEGDIR.get(p['seg'], '')}/{pid}.jpg"})
# дубли: из пары оставить вариант с большими продажами фабрики
byid = {r["id"]: r for r in rows}
for r in rows:
    o = byid.get(r["dup_of"] or "")
    if o:
        loser = r if (r["s30"], r["taste"]) < (o["s30"], o["taste"]) else o
        loser["dupe"] = (o if loser is r else r)["id"]
PR = json.load(open(f"{W}/photo_review.json")) if os.path.exists(f"{W}/photo_review.json") else {}
for r in rows:
    r["roi1330"] = round(roi(1330, r["price"], r["w"]))
    pv = PR.get(r["id"], {}).get("v", "")
    if pv in ("СНЯТЬ", "нет по фото", "нет фото", "дубль по фото"):
        r["verdict"] = "нет: снят по фото"
    elif r["roi"] < 200 and r["roi1330"] >= 200 and pv.startswith("ок") and not r.get("dupe") and r["price"] >= 5:
        r["verdict"] = "брать при цене от 1 330 ₽" if pv != "ок, условно" else "условно: при 1 330 ₽, фото на грани"
    elif r.get("dupe"):
        r["verdict"] = f"дубль {r['dupe']}"
    elif r["price"] < 5:
        r["verdict"] = "нет: дешевле ¥5"
    elif r["roi"] >= 200:
        r["verdict"] = "брать"
    elif r["roi"] >= 100:
        r["verdict"] = "условно: ROI 100–200 %"
    elif r["roi1330"] >= 100 and pv.startswith("ок") and r["price"] >= 5:
        r["verdict"] = "условно: ROI ≥100 % только при 1 330 ₽"   # правило заказа 1000 (владелец 26.10): ROI ≥100 % при цене продажи до 1 330 ₽
    else:
        r["verdict"] = "нет: ROI < 100 %"
rows.sort(key=lambda r: ({"брать": 0, "брать при цене от 1 330 ₽": 1}.get(r["verdict"], 2 if r["verdict"].startswith("условно") else 3), -r["roi"]))
wbk = Workbook(); ws = wbk.active; ws.title = "Черновик заказа"
H = ["фото 1688", "фото хита WB", "вердикт", "сегмент", "оффер 1688", "¥ (осн. вариант)", "вес, г", "вес — откуда", "продажи фабрики 30 дн", "вкус Kimi", "похож на хит",
     "хит WB", "хит: заказов 30 дн", "цена продажи ₽", "цена — откуда", "ROI %", "ROI при 1 330 ₽", "кол-во", "сумма ¥", "почему (Kimi)", "фабрика"]
ws.append(H)
for c in ws[1]:
    c.font = Font(bold=True); c.alignment = Alignment(wrap_text=True, vertical="top")
for i, wdt in enumerate([15, 15, 16, 16, 15, 9, 7, 11, 10, 7, 7, 12, 9, 9, 16, 7, 9, 7, 9, 60, 8]):
    ws.column_dimensions[chr(65 + i)].width = wdt
FILL = {"брать": "C6EFCE", "брать при цене от 1 330 ₽": "D9EAD3", "условно": "FFEB9C"}
for r in rows:
    qty = 50 if r["verdict"].startswith("брать") or r["verdict"].startswith("условно") else 0
    ref = r["ref"] or {}
    ws.append(["", "", r["verdict"], r["seg"], r["url"], r["price"], round(r["w"]), r["wsrc"], r["s30"], r["taste"], r["like"], ref.get("nm"),
               ref.get("orders30"), r["P"], r["psrc"], r["roi"], r["roi1330"], qty, round(qty * r["price"], 1), r["why"], r["shop"]])
    row = ws.max_row; ws.row_dimensions[row].height = 84
    for c in ws[row]:
        c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.cell(row, 3).fill = PatternFill("solid", fgColor=FILL.get(r["verdict"].split(":")[0], "FFC7CE"))
    for col, path in (("A", r["img"]), ("B", None)):
        if path and os.path.exists(path):
            tmp = f"/tmp/ord_{r['id']}.png"; im = Image.open(path).convert("RGB"); im.thumbnail((105, 105)); im.save(tmp); ws.add_image(XImage(tmp), f"{col}{row}")
ws.freeze_panes = "D2"
pr = json.load(open(f"{W}/photo_review.json")) if os.path.exists(f"{W}/photo_review.json") else {}
if pr:
    sh = wbk.create_sheet("Проверка фото")
    sh.append(["оффер", "вердикт по фото", "комментарий (фото в полном размере)"])
    for c in sh[1]:
        c.font = Font(bold=True)
    for o, n in pr.items():
        sh.append([f"https://detail.1688.com/offer/{o}.html", n["v"], n["c"]])
        sh.cell(sh.max_row, 2).fill = PatternFill("solid", fgColor={"СНЯТЬ": "FFC7CE", "на решение": "FFEB9C"}.get(n["v"], "C6EFCE"))
        sh.cell(sh.max_row, 3).alignment = Alignment(wrap_text=True)
    sh.column_dimensions["A"].width = 44; sh.column_dimensions["B"].width = 14; sh.column_dimensions["C"].width = 110
    for r in rows:   # снятые по фото — в вердикт основного листа не идут
        pass
m = wbk.create_sheet("Метод")
for line in [__doc__, "Источник: витрины 30 фабрик 1688 (22.10), срез WB 1 411 карточек (MPSTATS в выдаче, 22.10), отбор по фото — Kimi по профилю вкуса 03.10.",
             "Цена продажи — средний чек (выручка/заказы за 30 дн) похожего хита WB, которого указал Kimi; если похожего нет — медиана сегмента.",
             "Вердикт: брать — ROI ≥ 200 %; условно — 100–200 %; нет — ниже 100 % или дешевле ¥5. Дубли одного товара у разных фабрик — оставлен вариант с большими продажами.",
             "Кол-во 50 шт — правило новинок (пробная партия). Перед заказом: фото в полном размере (ворота v3), состав набора по вариантам, вес у продавца, если «допущение»."]:
    m.append([line])
m.column_dimensions["A"].width = 150
wbk.save(OUT)
from collections import Counter
c = Counter(r["verdict"].split(":")[0].split(" ")[0] for r in rows)
take = [r for r in rows if r["verdict"] == "брать"]
hi = [r for r in rows if r["verdict"] == "брать при цене от 1 330 ₽"]
print("брать при 1 330:", len(hi), "¥", round(sum(50 * r["price"] for r in hi)))
print(OUT, dict(c), "брать: позиций", len(take), "¥", round(sum(50 * r["price"] for r in take)))
