"""Zero-shot CLIP по фото: мотивы, читаемость, коллаж/реклама. Пишет clip.json {id: {prompt_key: score}}."""
import json, torch, open_clip
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
items = json.load(open("items.json"))
PROMPTS = {
 "sculpt": "chunky sculptural gold jewelry with smooth organic irregular metal shapes",
 "pearl": "jewelry made of pearls combined with gold",
 "black": "gold jewelry with black enamel or black onyx stones",
 "gem": "jewelry with a big colored gemstone surrounded by a halo of small rhinestones",
 "bow": "bow-shaped jewelry", "heart": "heart-shaped jewelry",
 "snake": "flat gold snake chain or omega collar necklace",
 "rhine": "sparkling silver rhinestone crystal necklace and earrings set",
 "flower": "flower-shaped jewelry", "cross": "cross pendant necklace",
 "big": "close-up photo where one large piece of jewelry fills most of the frame",
 "small": "photo where small tiny jewelry occupies only a small part of the frame",
 "collage": "a grid collage of many different product photos",
 "ad": "advertising image with big chinese text banner",
 "single": "a clean single product photo of jewelry",
 "base": "a photo of jewelry",
}
m, _, pp = open_clip.create_model_and_transforms("ViT-B-32", pretrained="laion2b_s34b_b79k"); m.eval(); tok = open_clip.get_tokenizer("ViT-B-32")
with torch.no_grad():
    T = m.encode_text(tok(list(PROMPTS.values()))); T = T / T.norm(dim=-1, keepdim=True)
paths = sorted({p for i in items for p in i["imgs"]})
out = {}
with torch.no_grad():
    for k in range(0, len(paths), 64):
        ims = torch.stack([pp(Image.open(p).convert("RGB")) for p in paths[k:k + 64]])
        e = m.encode_image(ims); e = e / e.norm(dim=-1, keepdim=True)
        s = (e @ T.T).tolist()
        for p, row in zip(paths[k:k + 64], s):
            out[p] = dict(zip(PROMPTS, [round(x, 4) for x in row]))
json.dump(out, open("clip.json", "w")); print("фото", len(out))
