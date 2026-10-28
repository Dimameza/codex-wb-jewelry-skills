"""Контакт-лист продающихся карточек (≥30 заказов/30 дн., без ювелирки 925/585) по скульптурным запросам — для проверки глазами."""
import glob, json, os, subprocess
from PIL import Image, ImageDraw, ImageFont
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
os.makedirs("img", exist_ok=True); os.makedirs("sheets", exist_ok=True)
seen, rows = set(), []
for f in sorted(glob.glob("raw/q*.json")):
    if "/._" in f: continue
    d = json.load(open(f))
    for r in d["rows"]:
        n = (r.get("name") or "").lower()
        if r.get("orders30") is None or r["orders30"] < 30 or r["nm"] in seen or "925" in n or "585" in n or ("серебр" in n and "под серебро" not in n): continue
        seen.add(r["nm"]); r["q"] = d["query"]; rows.append(r)
rows.sort(key=lambda r: -r["orders30"])
for r in rows:
    p = f"img/{r['nm']}.jpg"
    if not os.path.exists(p) and r.get("img"):
        subprocess.run(["curl", "-sL", "--max-time", "20", "-A", UA, "-o", p + ".webp", r["img"]])
        try: Image.open(p + ".webp").convert("RGB").save(p, quality=85)
        except Exception: pass
        if os.path.exists(p + ".webp"): os.remove(p + ".webp")
font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 15)
W, H, C = 220, 330, 6
for k in range(0, len(rows), 24):
    part = rows[k:k + 24]; sh = Image.new("RGB", (W * C, (H + 40) * ((len(part) + C - 1) // C)), "white"); dr = ImageDraw.Draw(sh)
    for j, r in enumerate(part):
        x, y = (j % C) * W, (j // C) * (H + 40)
        try: im = Image.open(f"img/{r['nm']}.jpg"); im.thumbnail((W - 6, H)); sh.paste(im, (x + 3, y))
        except Exception: pass
        dr.text((x + 3, y + H + 2), f"#{k + j + 1}  {int(r['price'])}₽  {int(r['orders30'])} зак  {int(r.get('rating_cnt') or 0)} оц", fill="black", font=font)
        dr.text((x + 3, y + H + 20), r["q"][:28], fill="gray", font=font)
    sh.save(f"sheets/s{k // 24:02d}.jpg", quality=80)
json.dump(rows, open("hot.json", "w"), ensure_ascii=False)
print(len(rows), "карточек;", len(glob.glob("sheets/s*.jpg")), "листов")
