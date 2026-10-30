"""30.10: листы для проверки глазами — кандидат и его 3 аналога WB из HTML-отчёта ROI.
Лист: 16 позиций (2 колонки × 8 строк), в строке: кандидат (рамка) + аналоги a, b, c. Пишет eye_analogs/sheet_NNN.jpg и eye_analogs/index.json."""
import json, os, re
from PIL import Image, ImageDraw, ImageFont
H = "../критерии_2026-10-28/ревью_плана/"; s = open(H + "логика_ROI_2026-10-30.html", encoding="utf-8").read()
D = json.loads(re.search(r"const D=(\{.*?\});\nconst I=", s, re.S).group(1))
O = "eye_analogs"; os.makedirs(O, exist_ok=True)
C, PER = 170, 16
try: FT = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 22)
except Exception: FT = ImageFont.load_default()
def tile(p, lab, col):
    t = Image.new("RGB", (C, C), "white")
    try: im = Image.open(p).convert("RGB"); im.thumbnail((C, C)); t.paste(im, ((C - im.width) // 2, (C - im.height) // 2))
    except Exception: pass
    d = ImageDraw.Draw(t); d.rectangle([0, 0, C - 1, C - 1], outline=col, width=4 if col != "#ccc" else 1)
    d.rectangle([0, 0, 12 + 13 * len(lab), 28], fill=col); d.text((5, 2), lab, fill="white" if col != "#ccc" else "black", font=FT)
    return t
items = [x for x in D["items"] if x["an"]]
idx = {}
for k in range(0, len(items), PER):
    sh = Image.new("RGB", (2 * 4 * C + 20, 8 * C), "#888"); part = items[k:k + PER]
    for j, x in enumerate(part):
        X, Y = (j // 8) * (4 * C + 20), (j % 8) * C
        sh.paste(tile(f"{H}логика_ROI_фото/{x['n']:04d}_1.jpg", f"{x['n']}", "#d02020"), (X, Y))
        for m, c in enumerate(x["an"][:3]):
            sh.paste(tile(f"{H}логика_ROI_фото/wb/{c['nm']}.jpg", "abc"[m], "#ccc"), (X + (m + 1) * C, Y))
    name = f"sheet_{k // PER + 1:03d}.jpg"; sh.save(f"{O}/{name}", quality=85)
    idx[name] = [dict(n=x["n"], seg=x["seg"], an=[c["nm"] for c in x["an"][:3]]) for x in part]
json.dump(idx, open(f"{O}/index.json", "w"), ensure_ascii=False)
print("листов", len(idx), "позиций", len(items))
