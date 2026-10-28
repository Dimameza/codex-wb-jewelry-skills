"""Проверка Claude по фото для широкого поиска (26.10).
python wide_review.py montage OUT_DIR   — непроверенные позиции со вкусом ≥3 из codex_taste_w*.json → снимок wide_snap.json + листы wrev_N.jpg (48 на лист)
python wide_review.py verdict '{"с":[..],"о":[..],"у":[..],"н":[..]}' — номера по снимку; кого не назвал — «ок» по умолчанию не ставится"""
import glob, json, os, sys
W = os.path.dirname(os.path.abspath(__file__))
pr = json.load(open(f"{W}/photo_review.json"))
if sys.argv[1] == "montage":
    from PIL import Image, ImageDraw
    t = {}
    for f in sorted(glob.glob(f"{W}/codex_taste_w*.json")):
        t.update(json.load(open(f)))
    pool = {p["id"]: p for p in json.load(open(f"{W}/pool_1688.json"))}
    ids = [k for k, v in t.items() if (v.get("taste") or 0) >= 3 and k not in pr and k in pool]
    ids.sort(key=lambda k: (pool[k]["seg"], -(t[k]["taste"] or 0)))
    json.dump(ids, open(f"{W}/wide_snap.json", "w"))
    for b in range(0, len(ids), 48):
        M = Image.new("RGB", (8 * 200, 6 * 200), "white"); d = ImageDraw.Draw(M)
        for i, k in enumerate(ids[b:b + 48]):
            x, y = (i % 8) * 200, (i // 8) * 200
            try:
                im = Image.open(f"{W}/wide_img/{k}.jpg").convert("RGB"); im.thumbnail((195, 195)); M.paste(im, (x + 2, y + 2))
            except Exception:
                pass
            d.rectangle((x + 2, y + 2, x + 92, y + 20), fill="yellow"); d.text((x + 5, y + 5), f"{b + i + 1} t{t[k]['taste']} ¥{pool[k]['price']:.0f}", fill="black")
        M.save(f"{sys.argv[2]}/wrev_{b // 48}.jpg", quality=80)
    print(len(ids), "к проверке,", (len(ids) + 47) // 48, "листов")
else:
    ids = json.load(open(f"{W}/wide_snap.json")); v = json.loads(sys.argv[2])
    V = {"с": ("ок, сильно", "ядро профиля (широкий поиск 26.10)"), "о": ("ок", "в профиле (широкий поиск 26.10)"),
         "у": ("ок, условно", "широкий профиль — допустимо (26.10)"), "н": ("нет по фото", "не профиль (26.10)")}
    for code, nums in v.items():
        for n in nums:
            pr[ids[n - 1]] = {"v": V[code][0], "c": V[code][1]}
    json.dump(pr, open(f"{W}/photo_review.json", "w"), ensure_ascii=False, indent=1)
    print("записано", sum(len(x) for x in v.values()), "из", len(ids))
