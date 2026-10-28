import json
from PIL import Image, ImageDraw, ImageFont, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
rows = json.load(open("scored.json"))
CODE = {"скульптурное": "С", "жемчуг": "Ж", "чёрная": "Ч", "цветной": "К", "бант": "Б", "змея": "З"}
def codes(r):
    t = r["R"]["профиль"][1]; return "".join(v for k, v in CODE.items() if k in t) or "-"
def rd(r):
    t = r["R"]["читаемость"][1]; big = "(10); " in t.split("; ")[0] + "; " and not t.startswith(("в описании фото — мелкое", "по фото (CLIP) изделие занимает")); one = not ("коллаж" in t)
    return ("к" if big else "_") + ("о" if one else "_")
f = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 15)
T = 210; per = 40; idx = []
for i, r in enumerate(rows):
    idx.append([i + 1, r["order"], r["row"]])
json.dump(idx, open("eye/index.json", "w"))
for s in range(0, len(rows), per):
    ch = rows[s:s + per]; can = Image.new("RGB", (8 * T, 5 * (T + 22)), "white"); d = ImageDraw.Draw(can)
    for k, r in enumerate(ch):
        x = (k % 8) * T; y = (k // 8) * (T + 22)
        try:
            ims = [Image.open(p).convert("RGB") for p in r["imgs"] if p]
            if len(ims) == 2:
                for q, im in enumerate(ims): im.thumbnail((T // 2 - 2, T - 4)); can.paste(im, (x + 1 + q * (T // 2), y + 2))
            else:
                im = ims[0]; im.thumbnail((T - 4, T - 4)); can.paste(im, (x + 2, y + 2))
        except Exception: pass
        d.rectangle((x, y + T, x + T - 2, y + T + 20), fill="#ffe680")
        d.text((x + 3, y + T + 2), f"{s + k + 1} {rd(r)} {codes(r)}", fill="black", font=f)
    can.save(f"eye/s{s // per:02d}.jpg", quality=78)
print((len(rows) + per - 1) // per, "листов")
