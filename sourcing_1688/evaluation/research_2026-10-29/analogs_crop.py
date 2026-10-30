"""30.10: фото WB в выдаче обрезаны до 3:4 (c516x688), поэтому настоящие копии дают по CLIP лишь 0,86–0,90.
Считает эмбеддинги наших фото, обрезанных по центру до 3:4, — для поиска копий. Пишет ours34 в analogs_emb.npz."""
import json, os, numpy as np, torch, open_clip
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
s = json.load(open("scored.json")); E = dict(np.load("analogs_emb.npz"))
m, _, pp = open_clip.create_model_and_transforms("ViT-B-32", pretrained="laion2b_s34b_b79k"); m.eval()
def c34(p):
    im = Image.open(p).convert("RGB"); w, h = im.size
    if w / h > 0.75: nw = int(h * 0.75); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    return pp(im)
paths = [next(p for p in r["imgs"] if os.path.exists(p)) for r in s]; out = []
with torch.no_grad():
    for k in range(0, len(paths), 64):
        e = m.encode_image(torch.stack([c34(p) for p in paths[k:k + 64]])); out.append((e / e.norm(dim=-1, keepdim=True)).numpy())
E["ours34"] = np.concatenate(out); np.savez("analogs_emb.npz", **E); print("ok", E["ours34"].shape)
