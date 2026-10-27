"""Контактный лист пар колье+серьги для проверки глазами: python pair_montage.py OUT_DIR [начало]"""
import json, os, sys
from PIL import Image, ImageDraw
W = os.path.dirname(os.path.abspath(__file__)); OUT = sys.argv[1]; start = int(sys.argv[2]) if len(sys.argv) > 2 else 0
import shutil
rev = json.load(open(f"{W}/sets_review.json")) if os.path.exists(f"{W}/sets_review.json") else {}
allp = json.load(open(f"{W}/" + os.environ.get("PAIRS", "sets7_pairs.json")))
snap = [p for p in allp if f"{p['neck']}+{p['ear']}" not in rev]   # только непроверенные, номера — по снимку
json.dump(snap, open(f"{W}/sets7_snap.json", "w"), ensure_ascii=False); pairs = snap[start:]
img = lambda k: next((f for f in (f"{W}/sets7/{k}.jpg", f"{W}/full/{k}_0.jpg") if os.path.exists(f)), None)
for b in range(0, len(pairs), 24):
    M = Image.new("RGB", (4 * 420, 6 * 215), "white"); d = ImageDraw.Draw(M)
    for i, p in enumerate(pairs[b:b + 24]):
        x, y = (i % 4) * 420, (i // 4) * 215
        for j, k in enumerate((p["neck"], p["ear"])):
            f = img(str(k))
            if f:
                im = Image.open(f).convert("RGB"); im.thumbnail((200, 200)); M.paste(im, (x + 5 + j * 205, y + 5))
        d.rectangle((x + 5, y + 5, x + 60, y + 24), fill="yellow"); d.text((x + 9, y + 9), f"{start + b + i + 1} s{p.get('score')}", fill="black")
    M.save(f"{OUT}/pairs_{(start + b) // 24}.jpg", quality=82)
print(len(pairs))
