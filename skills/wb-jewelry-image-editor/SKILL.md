---
name: wb-jewelry-image-editor
description: Use this skill when editing jewelry product images for Wildberries or marketplace cards: preserve exact product identity, improve premium look, increase CTR potential, and run strict visual checks before finalizing.
---

# WB Jewelry Image Editor

## Purpose

This skill is for editing jewelry product images for marketplace cards, especially Wildberries.

Main goals:
- preserve exact jewelry identity;
- improve commercial attractiveness;
- make the image premium and clean;
- improve CTR potential;
- avoid unnecessary full regeneration;
- run strict visual QA before final delivery.

---

## Core principle

The product is more important than the model, background, mood, props, or artistic style.

Never improve the image by changing the product into a different product.

---

## Always preserve

Preserve:
- exact product type;
- number of items in the set;
- shape and proportions;
- pearl / stone / chain structure;
- earring type;
- bracelet shape;
- necklace contour;
- pendant shape if present;
- clasp logic if visible;
- material finish;
- scale relationships between items.

Do not silently replace:
- pearls with random beads;
- stone chains with generic jewelry;
- long earrings with studs;
- bracelet with cuff;
- necklace with a different necklace;
- original set with invented extra items.

---

## Editing strategy

Use the smallest sufficient edit.

If only one issue is mentioned:
- fix only that issue;
- protect all successful areas;
- do not regenerate the full image.

Examples:
- If bracelet is not visible, improve bracelet visibility only.
- If face distracts, reduce face prominence without changing jewelry.
- If background is weak, improve background without altering product.
- If skin tone is too warm, calm the tone without destroying realism.

---

## Preferred visual style

Target:
- premium;
- editorial;
- clean;
- expensive;
- restrained;
- product-first;
- high jewelry readability.

Preferred:
- dark or neutral background;
- calm skin tone;
- clean neckline;
- soft directional light;
- crisp jewelry highlights;
- no visual noise.

Avoid:
- orange skin;
- plastic AI skin;
- excessive sparkle;
- cluttered props;
- full face dominance;
- fashion portrait where product becomes secondary.

---

## Composition rules

For main marketplace image:
- product must be understood in 0.5 seconds;
- jewelry should be large enough;
- face should not dominate;
- necklace should be the hero if present;
- earrings should support the look;
- bracelet/ring must be visible if included in the set;
- no awkward crop through important jewelry parts.

Preferred framing:
- lower half of face;
- neck;
- collarbones;
- shoulders;
- jewelry zone close-up.

If head direction matters and no other instruction overrides it:
- prefer slight turn to the right.

---

## Text rules

For main image:
- avoid text unless requested;
- if text is requested, keep it short and large;
- never overlap jewelry;
- never overlap critical body/jewelry boundaries.

For supporting slides:
- use restrained premium typography;
- keep text readable on mobile;
- use no more than 1–2 key messages per slide.

---

## Mandatory autotests

Before finalizing, check:

1. Product identity preserved.
2. Correct number of items.
3. Necklace shape preserved.
4. Earrings shape preserved.
5. Bracelet/ring shape preserved if present.
6. No invented jewelry.
7. Main product clearly visible.
8. Product readable in thumbnail.
9. Face does not distract.
10. Background does not distract.
11. Jewelry has premium highlights.
12. Skin tone is calm.
13. No broken hands/fingers/ears/neck.
14. No warped jewelry geometry.
15. No AI artifacts.
16. Marketplace-ready.

---

## Scoring

Score the result from 1 to 10.

- 9.5–10: excellent
- 9.0–9.4: strong and ready
- 8.0–8.9: good but can be improved
- 7.0–7.9: weak for main image
- below 7: unacceptable

If score is below 9:
- list concrete fixes;
- correct only failed areas;
- repeat QA.

Maximum cycles: 5.

---

## Output format

Return:

- Changed:
- Preserved:
- Autotest results:
- Score:
- Next fix:
- Decision:
