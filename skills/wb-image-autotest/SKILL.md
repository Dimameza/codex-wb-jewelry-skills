---
name: wb-image-autotest
description: Use this skill when evaluating jewelry product images, generated images, edited images, or full Wildberries card series with strict acceptance tests, scoring, and concrete correction recommendations.
---

# WB Image Autotest

## Purpose

This skill is for strict visual acceptance testing of marketplace jewelry images.

Use it after generation or editing.

It should not be polite or soft.
It should identify real commercial weaknesses.

---

## Evaluation mindset

Evaluate as:
- marketplace buyer;
- WB shelf competitor analyst;
- product card designer;
- image QA inspector.

Focus on:
- CTR;
- product clarity;
- product preservation;
- premium perception;
- mobile thumbnail readability;
- absence of AI defects.

---

## Mandatory tests

### 1. Product identity

Check:
- Is the product the same as the source?
- Is the item count correct?
- Is the necklace shape preserved?
- Are earrings the same type?
- Is bracelet/ring preserved?
- Are stones/pearls consistent?
- No invented elements?

Score: /10

---

### 2. Product visibility

Check:
- Is the hero item visible?
- Is the product large enough?
- Is the set understandable?
- Is bracelet visible if included?
- Are earrings visible if included?
- Is necklace contour readable?
- Is nothing critical cropped?

Score: /10

---

### 3. CTR potential

Check:
- Does image stop attention?
- Does it look better than average competitors?
- Is the product clear in 0.5 seconds?
- Is there contrast?
- Is there emotional premium value?
- Is the image not overloaded?

Score: /10

---

### 4. Premium perception

Check:
- Does it look expensive?
- Is lighting controlled?
- Is background premium?
- Is skin tone calm?
- Are highlights realistic?
- Is there no cheap catalog feel?

Score: /10

---

### 5. Thumbnail readability

Check:
- Would the user understand the product on a phone?
- Is text readable if present?
- Is jewelry visible when small?
- Is the silhouette clear?
- Does the face overpower the item?

Score: /10

---

### 6. Anatomy and realism

Check:
- No broken fingers.
- No broken wrists.
- No distorted ears.
- No broken neck.
- No impossible jewelry attachment.
- No floating items.
- No duplicated product fragments.

Score: /10

---

### 7. Text and infographic

If text exists:
- readable;
- not too small;
- not too much;
- does not overlap jewelry;
- premium style;
- no unsupported claims.

Score: /10

If no text:
- mark as not applicable.

---

### 8. Marketplace readiness

Check:
- ready for main photo or support slide?
- does it need correction?
- would it hurt trust?
- does it look like real product photo?

Score: /10

---

## Critical fail conditions

Automatic fail if:
- product changed;
- item missing;
- bracelet missing when required;
- earrings transformed;
- necklace distorted;
- face dominates main image;
- product too small;
- AI anatomy is visibly broken;
- text overlaps jewelry;
- image looks fake/cheap;
- unsupported material claims are present.

---

## Final rating logic

Use weighted score:

- Product identity: 25%
- Product visibility: 20%
- CTR potential: 20%
- Premium perception: 15%
- Thumbnail readability: 10%
- Anatomy/realism: 10%

Final score:
- 9.5–10: excellent
- 9.0–9.4: ready
- 8.0–8.9: usable but improve
- 7.0–7.9: weak
- below 7: reject

---

## Output format

Return:

## Autotest Result

### Scores
- Product identity:
- Product visibility:
- CTR potential:
- Premium perception:
- Thumbnail readability:
- Anatomy/realism:
- Text/infographic:
- Marketplace readiness:

### Critical failures
- ...

### What is strong
- ...

### What must be fixed
- ...

### Final score
X/10

### Verdict
READY / REVISE / REJECT

### Correction prompt
Give a concise correction prompt for the next edit.
