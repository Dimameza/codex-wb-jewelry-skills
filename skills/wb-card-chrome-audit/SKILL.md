---
name: wb-card-chrome-audit
description: Use when Codex needs a safe visible Google Chrome audit of one Wildberries product card on macOS, including split preflight, screenshots, OCR, characteristics/description panel, seller, delivery, reviews/questions, and no product image downloads, WB API calls, headless scraping, or anti-bot bypass.
---

# WB Card Chrome Audit

## Overview

Use installed Google Chrome as a visible manual browser surface for one Wildberries product card. Collect only data a normal user can see on the card page and its native expandable UI. Do not download product images, call WB APIs, use background scraping, bypass anti-bot states, log in, add to cart, or submit forms.

For the full reusable specification, read `references/wb-card-data-collection-tz.md` before collecting data.

## Required Setup

Use split preflight.

### Input/path checks

Run before public-first or any browser/network action:

- Extract exactly one WB `nm_id` from the URL.
- Confirm the URL is a Wildberries card URL or can be normalized to one.
- Confirm WB output folders are writable.
- Confirm runtime/config/artifact paths do not point to `/Users/dmitrijmizinov/Documents/ATM Network`.

Visible OCR text from the current Chrome window is not a path-guard violation. Using ATM Network files, caches, configs, or artifact paths is a violation.

### Visible Chrome checks

Run only before the visible Chrome layer:

| Permission | Required check |
|---|---|
| Screen Recording | `screencapture` creates a PNG where Chrome/page is visible |
| Accessibility | `System Events` returns `UI elements enabled = true` |
| Input Monitoring | listen-only `CGEventTap` returns `true` |
| Automation: Chrome | active tab URL/title can be read |
| Chrome Apple Events JS | harmless `document.title` works |
| Automation: System Events | harmless process query works |
| Swift OCR runner | `swift -module-cache-path /private/tmp/wb_swift_module_cache src/ocr/vision_ocr.swift <png>` works |

If visible preflight fails, stop the visible layer and tell the user exactly which macOS settings pane or OCR dependency needs attention. In a hybrid flow, `public_only_degraded` is allowed only when visible data is not forced by the user.

## Safety Rules

- Work with exactly one requested card URL.
- Use visible installed Google Chrome, not headless browser.
- Prefer read-only visible viewport text to avoid unnecessary screenshots. OCR is not needed when no screenshot is captured.
- Every screenshot captured as evidence or source must immediately go through `capture_recognize_flush` before any next click, scroll, navigation, or read-after-state-change.
- Use adaptive pauses: `100-200 ms` for stable polling loops, at least `1s` for routine scroll/read/screenshot on stable UI, at least `3s` after navigation/reload/modal/loading click/retry/uncertain state, and `5-10s` for slow/error/anti-bot/captcha/site-limit states.
- Before every browser action, recompute missing required fields.
- Stop immediately when all required fields are collected or explicitly unavailable, unless a new user-requested gate is opened.
- Do not solve or bypass captcha, anti-bot, login, suspicious activity, or technical restrictions.
- Do not download product photos, videos, thumbnails, direct media URLs, or other media files.
- Separate official WB page data from extension overlays such as mkeeper/mpstats.
- Do not continue into recommendation zones after required fields are complete.

## Collection Workflow

1. Run `input_path_preflight`.
2. Create the run folder under `/Users/dmitrijmizinov/Documents/WB Data/08_metrics_reports/wb_card_<nm_id>/runs/<run_id>/`.
3. Decide whether the visible Chrome layer is needed. If it is not available and visible is not forced, record `public_only_degraded`.
4. Run `visible_chrome_preflight` only before the visible layer.
5. Warm or smoke-test the Swift OCR runner with `/private/tmp/wb_swift_module_cache`.
6. Open or focus the card URL in installed Google Chrome.
7. Capture `initial_page.png` through `capture_recognize_flush`.
8. Collect first-screen official WB data and extension overlays separately.
9. Recompute missing required fields before every next browser action.
10. Resolve the `Характеристики и описание` click target to the best visible clickable element.
11. Click via CoreGraphics mouse move/down/up.
12. Wait for `panel_state = "opened_stable"` before any panel screenshot.
13. Capture panel screenshots only through `capture_recognize_flush`; scroll only inside the panel container.
14. Open other native visible sections only while they close pending required fields.
15. Store unknown fields as `null`, `{}`, or `[]` with an explicit unavailable reason, never guesses.
16. Generate the final `card_report.md`, then run the latest-policy gate.

Root `card_data.json` and `card_report.md` are latest only. Partial, failed, stale, or OCR-zero runs stay under `runs/<run_id>/` and must not overwrite root latest.

## `capture_recognize_flush`

Use this gate for every screenshot:

```text
capture_recognize_flush(name, expected_context, expected_fields):
    assert pending_ocr_jobs == []
    capture screenshot
    update screenshots_manifest.json with captured status
    run OCR immediately
    save OCR text to diagnostics/ocr/
    parse visible values
    update card_data.json, run_metrics.json, screenshots_manifest.json, action_log.jsonl
    rebuild card_report.md only on final or major checkpoint
    set screenshot status = recognized_and_flushed
    allow next browser action
```

Do not batch OCR at the end. Do not set `audit_status = "complete"` while any required screenshot is unrecognized.

## Interaction Notes

- Primary visible-click method on macOS is CoreGraphics mouse move/down/up. `System Events click at {x,y}` is allowed only as a fallback with timeout and diagnostics.
- Click the center point of the best clickable candidate. Prefer `button`, `tab`, `summary`, `a`, click handler, or `cursor:pointer` elements.
- Reject huge parent containers larger than 70% of viewport width or height. If only a parent text container matches, search inside it for a child clickable element.
- Allow at most one retry after rechecking coordinates and overlays.
- Use Chrome Apple Events JavaScript only for safe diagnostics or reading visible/current page state. Do not use it to call network endpoints, extract media URLs, download files, or mutate the page.
- If Chrome or Codex returns focus unexpectedly, verify by URL/title and screenshot before continuing.

## Data Schema

Use this structure for `card_data.json` and extend only when visible data requires it:

```json
{
  "audit_status": null,
  "run_id": null,
  "nm_id": null,
  "url": null,
  "final_url": null,
  "collected_at": null,
  "method": "manual_visible_chrome_audit",
  "browser": "Google Chrome",
  "page_status": null,
  "blocking_warnings": [],
  "non_blocking_warnings": [],
  "preflight": {
    "input_path_preflight": null,
    "visible_chrome_preflight": null
  },
  "screenshot_recognition": {
    "pending_jobs": [],
    "screenshots_total": 0,
    "ocr_runs_total": 0,
    "all_required_screenshots_recognized": false
  },
  "characteristics_description_panel": {
    "requested": false,
    "clicked": false,
    "state": null,
    "open_wait_ms": null,
    "screenshots": []
  },
  "latest_policy": {
    "eligible_for_latest": false,
    "latest_updated": false,
    "reason": null
  },
  "title": null,
  "brand": null,
  "seller": null,
  "shop": null,
  "price": null,
  "old_price": null,
  "discount": null,
  "vat_note": null,
  "rating": null,
  "reviews_count": null,
  "questions_count": null,
  "availability": null,
  "delivery": null,
  "warehouse": null,
  "return_conditions": null,
  "fitting": null,
  "colors": [],
  "selected_color": null,
  "sizes": [],
  "selected_size": null,
  "stock": null,
  "variants": [],
  "characteristics": {},
  "description": null,
  "materials": null,
  "composition": null,
  "package_contents": null,
  "country_of_origin": null,
  "dimensions": null,
  "weight": null,
  "warranty": null,
  "certificates": null,
  "seller_info": {},
  "badges": [],
  "browser_extension_overlays": {},
  "opened_sections": [],
  "unavailable_fields": [],
  "screenshots": [],
  "sources": {},
  "action_log": []
}
```

## Report Requirements

`card_report.md` must include:

- URL, `nm_id`, `run_id`, and collection timestamp.
- Split-preflight summary and OCR runner summary.
- Sequential action log.
- Opened sections, screenshots, and OCR statuses.
- Table of found official WB data with source for each value.
- Separate section for extension overlay data, if any.
- Unavailable fields and exact reason.
- `blocking_warnings`, `non_blocking_warnings`, and latest-policy result.
- Quality checklist: no guesses, no image downloads, no API use, no headless scraping, no bypass, no ATM Network runtime/config/artifact paths.

## Common Mistakes

| Mistake | Correct behavior |
|---|---|
| Mixing mpstats/mkeeper with WB data | Put it under `browser_extension_overlays` |
| Treating title-bar text as fully verified card data | Mark as `needs_manual_check` unless confirmed on page |
| Capturing screenshot and continuing before OCR | Stop until `capture_recognize_flush` completes |
| Capturing the characteristics panel before it is stable | Wait for `opened_stable` |
| Downloading images for OCR | Do not download; use visible screenshots only |
| Using old partial runs as latest | Keep them under `runs/<run_id>/`; stale or OCR-zero runs cannot be latest |
