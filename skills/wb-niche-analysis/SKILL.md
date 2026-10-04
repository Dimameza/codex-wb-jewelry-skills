---
name: wb-niche-analysis
description: Use when measuring a Wildberries niche — total monthly volume in units and rubles, seller ranking by revenue, growth dynamics, and whether our purchase economics fit. Covers MPSTATS category panel, catalog collection, category filtering, and the mandatory self-calibration against our own WB API data.
---

# WB Niche and Competitor Analysis

## Overview

Measure a WB niche end to end: how much money is in it, who takes it, who is growing, and where our purchase price fits. Built and validated on the Russian jewelry (bijouterie) niche on 2026-10-04.

Read `references/wb-niche-analysis-tz.md` before running. It carries the full spec, the traps, and the control figures from the validated run.

## Core sources

- MPSTATS panel in the owner's Chrome — per-subcategory orders for 30 days, and per-card orders printed under every card in search results.
- `basket-NN.wbbasket.ru/vol{nm//100000}/part{nm//1000}/{nm}/info/ru/card.json` — category (`subj_root_name`), creation date, `selling.supplier_id`.
- `feedbacks1|2.wb.ru/feedbacks/v1/{imt_id}` — reviews with dates, for growth proxy.
- Our own WB statistics API — the calibration baseline.

## Non-negotiable rules

- Never treat a silent source as a negative answer. Count unanswered cards as a separate line and retry with baskets 1..60 before concluding.
- Never use the MPSTATS "order dynamics %" field. Validated against our own sales: mean error 187 percentage points, sign correct 6 times out of 16.
- Always calibrate the method against our own seller account before publishing any figure.
- Always produce two independent estimates of the niche volume. A gap above 5 percent means the method is wrong.
- Catalog collection needs real scroll events. JavaScript scrollTo renders the panel but does not load the next batch.

## Output

Volume by subcategory, seller ranking filtered to the target root category, growth block, purchase-ceiling per subcategory, our own position and share.
