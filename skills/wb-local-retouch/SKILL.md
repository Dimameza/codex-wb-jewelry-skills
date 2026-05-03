---
name: wb-local-retouch
description: Use this skill when the user asks for precise local image corrections without full regeneration: fix bracelet visibility, jewelry clarity, crop, background, skin tone, lighting, or artifacts while preserving all successful areas.
---

# WB Local Retouch

## Purpose

This skill is for targeted image retouching.

Use it when:
- most of the image is already good;
- the user wants to fix only one or several details;
- full regeneration would risk damaging successful areas.

---

## Prime directive

Do not touch what is already good.

If necklace and earrings are ideal:
- lock them;
- do not alter them;
- do not change their shape, sparkle, size, or position.

If only bracelet needs correction:
- fix bracelet only.

---

## Local edit types

Supported local corrections:

### Bracelet visibility
- reveal full bracelet;
- adjust wrist/hand position;
- improve crop;
- increase contrast;
- sharpen bracelet;
- remove obstruction.

Do not:
- replace bracelet with different design;
- add fake stones;
- change bracelet type.

---

### Necklace clarity
- increase contrast;
- sharpen contour;
- improve highlights;
- remove hair/clothing obstruction;
- correct crop.

Do not:
- change necklace shape;
- add rows;
- change pearl size;
- invent pendant.

---

### Earrings clarity
- reveal earring from hair/shadow;
- improve separation;
- restore hanging structure;
- sharpen stones.

Do not:
- turn long earrings into studs;
- change length;
- add extra chains.

---

### Face distraction reduction
- crop face partially;
- reduce facial contrast;
- shift visual emphasis to jewelry;
- turn head slightly right if needed.

Do not:
- beautify face at the expense of product;
- make eyes the center;
- change model identity unnecessarily.

---

### Background improvement
- darken background;
- remove clutter;
- create premium neutral tone;
- improve separation.

Do not:
- change product lighting in an inconsistent way;
- add props unless requested.

---

### Skin tone correction
- reduce orange/red tone;
- calm warmth;
- keep realistic texture;
- avoid plastic smoothing.

Do not:
- over-retouch;
- make skin gray/dead;
- destroy natural shadows.

---

### Artifact correction
- fix broken fingers;
- fix warped jewelry;
- remove duplicate fragments;
- repair distorted chains;
- correct floating objects.

Do not:
- solve artifacts by changing product design.

---

## Protected zones

Before editing, define protected zones:
- product elements already correct;
- model pose already correct;
- good face/crop areas if relevant;
- good background if relevant.

Protected zones must not be changed.

---

## Editing loop

Maximum cycles: 5.

For each cycle:
1. Identify exact defect.
2. Define protected zones.
3. Apply smallest sufficient correction.
4. Run local QA.
5. Stop if corrected.
6. Continue only if defect remains.

---

## Local QA checklist

Check:

1. Requested defect fixed.
2. No successful area damaged.
3. Product identity preserved.
4. No new artifacts.
5. Lighting still coherent.
6. Crop still good.
7. Thumbnail readability improved or unchanged.
8. Premium feel improved or unchanged.

---

## Fail conditions

Fail if:
- correction changes the product;
- necklace/earrings damaged while fixing bracelet;
- new anatomy defects appear;
- crop becomes worse;
- image becomes less premium;
- correction looks like patchwork.

---

## Output format

Return:

- Target defect:
- Protected zones:
- Local changes:
- Autotest:
- Score before:
- Score after:
- Remaining issue:
- Decision:
