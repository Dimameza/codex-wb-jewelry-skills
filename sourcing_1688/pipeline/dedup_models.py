"""Дубли одной модели у разных продавцов 1688 (27.10): одна и та же вещь под разными offerId или в другом цвете.
Дедуп по offerId их не ловит. Похожесть фото — CLIP ViT-B-32 (open_clip, laion2b) + phash; пары выше порога
собираются в листы для проверки глазами, подтверждённые пары склеиваются в группы, в группе остаётся одна позиция.

python dedup_models.py pairs ITEMS.json OUT_DIR [порог=0.86]   — пары похожих фото + листы dup_N.jpg (24 пары на лист)
python dedup_models.py groups OUT_DIR "1,2,5,..."              — номера подтверждённых пар → группы и список на удаление

ITEMS.json — список {"id", "img", "part", "row"}; part "2" (комплекты) важнее "1" (одиночные), внутри части — меньший row.
Запуск: uv run --with open_clip_torch --with pillow --with imagehash --with numpy python dedup_models.py ..."""
import json, os, sys

if sys.argv[1] == "pairs":
    import imagehash, numpy as np, open_clip, torch
    from PIL import Image, ImageDraw, ImageFile, ImageFont
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    items, out = json.load(open(sys.argv[2])), sys.argv[3]
    thr = float(sys.argv[4]) if len(sys.argv) > 4 else 0.86
    os.makedirs(out, exist_ok=True)
    idx = [i for i, x in enumerate(items) if x.get("img") and os.path.exists(x["img"])]
    m, _, pp = open_clip.create_model_and_transforms("ViT-B-32", pretrained="laion2b_s34b_b79k"); m.eval()
    embs, ph = [], {}
    with torch.no_grad():
        for k in range(0, len(idx), 64):
            ims = [Image.open(items[i]["img"]).convert("RGB") for i in idx[k:k + 64]]
            for i, im in zip(idx[k:k + 64], ims):
                ph[i] = imagehash.phash(im)
            e = m.encode_image(torch.stack([pp(im) for im in ims])); embs.append(e / e.norm(dim=-1, keepdim=True))
    S = torch.cat(embs).numpy() @ torch.cat(embs).numpy().T
    pairs = []
    for a in range(len(idx)):
        for b in range(a + 1, len(idx)):
            i, j = idx[a], idx[b]
            if items[i]["id"] == items[j]["id"]:
                continue
            s, dp = float(S[a, b]), int(ph[i] - ph[j])
            if s >= thr or dp <= 12:   # phash ловит одно и то же фото с водяным знаком или обрезкой
                pairs.append([i, j, round(s, 3), dp])
    pairs.sort(key=lambda x: -x[2])
    json.dump({"items": items, "pairs": pairs}, open(f"{out}/dup_snap.json", "w"), ensure_ascii=False)
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 16); T, per, cols = 230, 24, 4
    for sh in range(0, len(pairs), per):
        chunk = pairs[sh:sh + per]; rows = (len(chunk) + cols - 1) // cols
        can = Image.new("RGB", (cols * (2 * T + 20), rows * (T + 28)), "white"); d = ImageDraw.Draw(can)
        for k, (i, j, s, dp) in enumerate(chunk):
            x, y = (k % cols) * (2 * T + 20), (k // cols) * (T + 28)
            for q, it in enumerate((items[i], items[j])):
                im = Image.open(it["img"]).convert("RGB"); im.thumbnail((T, T)); can.paste(im, (x + q * T, y + 24))
            d.text((x + 2, y + 2), f"#{sh + k + 1}  s={s} p={dp}  {items[i].get('part')}/{items[j].get('part')}", fill="red", font=font)
            d.line([(x + 2 * T + 10, y), (x + 2 * T + 10, y + T + 28)], fill="black", width=3)
        can.save(f"{out}/dup_{sh // per}.jpg", quality=80)
    print("пар", len(pairs), "листов", (len(pairs) + per - 1) // per)
else:
    out = sys.argv[2]; snap = json.load(open(f"{out}/dup_snap.json")); items, pairs = snap["items"], snap["pairs"]
    ok = [int(x) for x in sys.argv[3].split(",") if x.strip()]
    par = {}

    def f(x):
        par.setdefault(x, x)
        while par[x] != x:
            x = par[x]
        return x
    for n in ok:
        i, j = pairs[n - 1][:2]; par[f(i)] = f(j)
    groups = {}
    for n in ok:
        for i in pairs[n - 1][:2]:
            groups.setdefault(f(i), set()).add(i)
    pri = lambda i: (0 if items[i].get("part") == "2" else 1, items[i].get("row") or 10 ** 9)
    drop = [i for g in groups.values() for i in sorted(g, key=pri)[1:]]
    json.dump({"groups": [sorted(g) for g in groups.values()], "drop": drop, "drop_ids": [items[i]["id"] for i in drop]},
              open(f"{out}/dup_groups.json", "w"), ensure_ascii=False)
    print("групп", len(groups), "убрать", len(drop))
