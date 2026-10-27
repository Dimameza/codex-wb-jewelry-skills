"""Спрос WB (срез 22.10) × предложение 1688 (витрины 59 фабрик 22.10): шорт-лист по сегментам.
Потолок закупки — канон ROI 200 % (память wb-bijou-subject-pick): ¥ ≈ 0,013 × (цена WB − 205)."""
import glob, json, os, re, statistics as st, sys

W = os.path.dirname(os.path.abspath(__file__))
F = "/Volumes/ADATA SD810/WB/Подбор/1688_данные/factories_2026-10-22"
wb = json.load(open(f"{W}/wb_slice.json"))
seg_stat = {s["seg"]: s for s in wb["segments"]}

BAD = re.compile(r"卡片|卡纸|首饰盒|包装盒|礼品盒|礼盒|收纳|饰品盒|包装袋|自封袋|袋子|补价|补差|差价|定做|耳堵|配件|散珠|半成品|diy|DIY|儿童|宝宝|新娘|婚纱|发夹|发卡|头饰|发圈|手机|钥匙扣|眼镜")
SILVER = re.compile(r"纯银|足银|999|18K金|真金")


def seg_cn(t):
    has = lambda *w: any(x in t for x in w)
    neck, ear, br, ring, pend = has("项链", "锁骨链", "颈链", "项圈", "毛衣链", "choker"), has("耳环", "耳钉", "耳坠", "耳饰", "耳夹", "耳线"), has("手链", "手镯", "手饰", "手串"), has("戒指", "指环"), has("吊坠")
    if has("十字"):
        return "Г крест"
    if has("胸针"):
        return "брошь"
    if has("套装", "两件套", "三件套", "四件套", "五件套", "一套", "组合") or ((neck or pend) and ear):
        k = sum([neck, ear, br, ring])
        if k >= 4 or has("四件套", "五件套"):
            return "А4 набор 4+"
        if k == 3 or has("三件套"):
            return "А3 набор 3"
        if (neck or pend) and ear and not br:
            return "А2/Б колье|подвеска+серьги"
        if ring and not (neck or ear):
            return "кольца набор"
        return "набор прочий"
    if has("项圈", "颈链", "choker"):
        return "чокер"
    if neck and has("珍珠") and not pend:
        return "бусы"
    if neck:
        return "колье"
    if pend:
        return "подвеска"
    if ear:
        return "серьги"
    if ring:
        return "кольцо"
    if br:
        return "браслет"
    return "прочее"


known = set()   # офферы, которые уже заказывали / уже в подборе новинок
for f in glob.glob("/Volumes/ADATA SD810/WB/Подбор/1688_данные/novinki55_2026-10-21/results/N*.json"):
    if not os.path.basename(f).startswith("._"):
        known.update(c["offerId"] for c in json.load(open(f)).get("candidates", []))
FDIRS = [F, "/Volumes/ADATA SD810/WB/Подбор/1688_данные/factories_2026-10-23", "/Volumes/ADATA SD810/WB/Подбор/1688_данные/factories_2026-10-24_sets"]
fac = {}
for fd in FDIRS:
    if os.path.exists(f"{fd}/factories.json"):
        fac.update({f["code"]: f for f in json.load(open(f"{fd}/factories.json"))})
pool = []
for fp in [x for fd in FDIRS for x in glob.glob(f"{fd}/shops/*.json")]:
    if os.path.basename(fp).startswith("._"):
        continue
    d = json.load(open(fp))
    for r in d.get("rows", []):
        t = r["t"]
        if r["p"] < 5 or r["p"] > 30 or BAD.search(t) or SILVER.search(t):
            continue
        new = r.get("created", 0) and (r["created"] / 1000) > (__import__("time").time() - 90 * 86400)
        if r["s30"] < 50 and not (new and r["s30"] >= 15):
            continue
        s = seg_cn(t)
        if s in ("прочее",):
            continue
        ss = seg_stat.get(s)
        check = ss["check_med"] if ss else None
        # вкус владельца: работать от 1 000 ₽ → потолок ¥11,1 при 1 057 ₽; верхний ярус ¥14,6 при 1 330 ₽
        ceil = round(0.013 * (max(check or 0, 1057) - 205), 1)
        ceil_top = round(0.013 * (max(check or 0, 1330) - 205), 1)
        pool.append({"seg": s, "shop": d["code"], "shop_name": fac.get(d["code"], {}).get("name", ""), "id": r["id"], "price": r["p"], "s30": r["s30"],
                     "sold_cum": r["vs"], "new90": bool(new), "title": t, "img": r["img"], "known": r["id"] in known,
                     "wb_check_med": check, "wb_med_orders": ss["med_orders"] if ss else None, "ceil_cny_roi200": ceil, "ceil_cny_top": ceil_top,
                     "fits": r["p"] <= ceil, "fits_top": r["p"] <= ceil_top, "url": f"https://detail.1688.com/offer/{r['id']}.html"})
# позиции, которые уже были в пуле (их оценивали Kimi/Codex/Claude), не выпадают из-за возраста «новинки 90 дн» (26.10)
if os.path.exists(f"{W}/pool_1688.json"):
    have = {p["id"] for p in pool}
    pool += [p for p in json.load(open(f"{W}/pool_1688.json")) if p["id"] not in have]
pool.sort(key=lambda x: (x["seg"], -x["s30"]))
json.dump(pool, open(f"{W}/pool_1688.json", "w"), ensure_ascii=False, indent=1)
by = {}
for p in pool:
    by.setdefault(p["seg"], []).append(p)
print(f"пул {len(pool)} (из них уже видели {sum(p['known'] for p in pool)}, новинки 90 дн {sum(p['new90'] for p in pool)})")
for s, L in sorted(by.items(), key=lambda x: -len(x[1])):
    fit = [p for p in L if p["fits"]]
    ss = seg_stat.get(s, {})
    print(f"{s:30} пул {len(L):4} в потолке {len(fit):4} | WB чек {ss.get('check_med')} мед.заказов {ss.get('med_orders')} | потолок ¥{L[0]['ceil_cny_roi200']}")
