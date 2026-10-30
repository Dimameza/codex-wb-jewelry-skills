"""30.10: цвет металла (золото / серебро / прочее) у наших позиций и карточек WB — чтобы цену подтверждали аналоги того же цвета.
Проверка глазами показала: в группах «комплект с камнями», «комплект жемчуг», «колье сердце» и др. серебро и золото смешаны.
Наши: по описаниям Claude/Codex/Kimi (кто чаще: «золот» или «серебр»); при равенстве — CLIP. WB: по названию; иначе — CLIP.
CLIP: средний эмбеддинг подсказок «золотое» и «серебряное» украшение, отступ ≥ MARGIN, иначе «прочее» (жемчуг, бусы, шнур, неясно).
Запуск: uv run -q --with open_clip_torch --with numpy python metal.py → metal.json {"ours": {№: m}, "wb": {nm: m}, "src": …}"""
import json, re, numpy as np, torch, open_clip
from collections import Counter
MARGIN = 0.012
P = {"gold": ["a photo of gold jewelry", "gold-colored metal necklace and earrings", "yellow gold plated jewelry"],
     "silver": ["a photo of silver jewelry", "silver-colored metal necklace and earrings", "white metal rhodium plated jewelry"]}
m, _, _ = open_clip.create_model_and_transforms("ViT-B-32", pretrained="laion2b_s34b_b79k"); m.eval(); tok = open_clip.get_tokenizer("ViT-B-32")
with torch.no_grad():
    T = {k: (lambda e: (e / e.norm(dim=-1, keepdim=True)).mean(0).numpy())(m.encode_text(tok(v))) for k, v in P.items()}
E = np.load("analogs_emb.npz"); AW = json.load(open("analogs_wb.json")); s = json.load(open("scored.json"))
def clip(e):
    d = float(e @ T["gold"] - e @ T["silver"]); return ("gold" if d > 0 else "silver") if abs(d) >= MARGIN else "other", round(d, 4)
def by_text(t, ours):
    t = (t or "").lower()
    if ours: g, sv = len(re.findall(r"золот", t)), len(re.findall(r"серебр", t))
    else: g, sv = bool(re.search(r"золот|позолоч|gold", t)), bool(re.search(r"серебр|silver|родир", t))
    return "gold" if g > sv else "silver" if sv > g else None
out = {"ours": {}, "wb": {}, "src": {"ours": {}, "wb": {}}, "clip": {"ours": {}, "wb": {}}}
for i, r in enumerate(s):
    tm = by_text(" ".join(v or "" for v in (r.get("descr") or {}).values()), True); cm, d = clip(E["ours"][i])
    out["ours"][str(i + 1)] = tm or cm; out["src"]["ours"][str(i + 1)] = "описания" if tm else "CLIP"; out["clip"]["ours"][str(i + 1)] = d
for k, x in enumerate(AW):
    tm = by_text(x["name"], False); cm, d = clip(E["wb"][k])
    out["wb"][x["nm"]] = tm or cm; out["src"]["wb"][x["nm"]] = "название" if tm else "CLIP"; out["clip"]["wb"][x["nm"]] = d
# 30.10: жемчуг / без жемчуга — для групп бус и жемчуга (price_check_canon.py PEARL=1). Наши: основной стиль PEARL или PEARL среди стилей
# и «жемчуг» в описании Claude. WB: «жемчуг» в названии, иначе CLIP (отступ ≥ PMARGIN), иначе «?» (остаётся в обеих группах).
PMARGIN = 0.015
PP = {"pearl": ["a necklace made of white pearls", "pearl beads jewelry", "jewelry with many pearls"],
      "no": ["a necklace made of colorful stone beads", "metal chain jewelry without pearls", "crystal rhinestone jewelry"]}
with torch.no_grad():
    TP = {k: (lambda e: (e / e.norm(dim=-1, keepdim=True)).mean(0).numpy())(m.encode_text(tok(v))) for k, v in PP.items()}
con = json.load(open("стили/consensus.json"))
def pclip(e):
    d = float(e @ TP["pearl"] - e @ TP["no"]); return ("pearl" if d > 0 else "no") if abs(d) >= PMARGIN else "?"
out["pearl"] = {"ours": {}, "wb": {}}
for i, r in enumerate(s):
    c = con[str(i + 1)]; out["pearl"]["ours"][str(i + 1)] = c["основной"] == "PEARL" or ("PEARL" in c["стили"] and "жемчуг" in ((r.get("descr") or {}).get("claude") or "").lower())
for k, x in enumerate(AW):
    out["pearl"]["wb"][x["nm"]] = "pearl" if "жемчуг" in (x["name"] or "").lower() else pclip(E["wb"][k])
named = [(pclip(E["wb"][k])) for k, x in enumerate(AW) if "жемчуг" in (x["name"] or "").lower()]
print("жемчуг: наших", sum(out["pearl"]["ours"].values()), "| WB", Counter(out["pearl"]["wb"].values()), "| CLIP на карточках с «жемчуг» в названии", Counter(named))
json.dump(out, open("metal.json", "w"), ensure_ascii=False)
from collections import Counter
print("наши", Counter(out["ours"].values()), "| WB", Counter(out["wb"].values()))
# согласие CLIP с текстом там, где текст есть — оценка точности CLIP
for side in ("ours", "wb"):
    pairs = [(out[side][k], clip(E[side][j])[0]) for j, k in enumerate(out[side]) if out["src"][side][k] != "CLIP"]
    ok = sum(a == b for a, b in pairs); oth = sum(b == "other" for a, b in pairs)
    print(side, "CLIP против текста: совпало", ok, "из", len(pairs), "| CLIP «прочее»", oth, "| противоречит", len(pairs) - ok - oth)
