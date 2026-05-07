---
name: wb-card-chrome-audit
description: Use when Codex needs to collect visible text data from one Wildberries product card through installed Google Chrome on macOS, especially WB/Wildberries карточка товара audits, screenshots, OCR, characteristics, seller, delivery, reviews/questions, and no product image downloads.
---

# WB Card Chrome Audit

## Overview

Use installed Google Chrome as a visible manual browser surface for one Wildberries product card. Collect only data a normal user can see on the card page and its native expandable UI. Do not download product images, call WB APIs, use background scraping, bypass anti-bot states, log in, add to cart, or submit forms.

For the full reusable specification, read `references/wb-card-data-collection-tz.md` before collecting data.

## Required Setup

Before collecting, verify macOS permissions:

| Permission | Required check |
|---|---|
| Screen Recording | `screencapture` creates a PNG where Chrome/page is visible |
| Accessibility | `System Events` returns `UI elements enabled = true` |
| Input Monitoring | listen-only `CGEventTap` returns `true` |
| Automation: Chrome | active tab URL/title can be read |
| Chrome Apple Events JS | harmless `document.title` works |
| Automation: System Events | harmless process query works |

If a permission fails, stop and tell the user exactly which macOS settings pane to open. Do not continue the card audit with partial permissions unless the user explicitly changes the task scope.

## Safety Rules

- Work with exactly one requested card URL.
- Use visible installed Google Chrome, not headless browser.
- Use sequential actions with at least 3 seconds between navigation, clicks, scrolls, section opens, modal closes, and retries.
- Increase to 5-10 seconds on slow loading, error states, or site limits.
- Do not solve or bypass captcha, anti-bot, login, suspicious activity, or technical restrictions.
- Do not download product photos, videos, thumbnails, or media files.
- Screenshots are allowed only as visible-state evidence and OCR source.
- Separate official WB page data from extension overlays such as mkeeper/mpstats.

## Collection Workflow

1. Create output folders:
   - `/Users/dmitrijmizinov/Documents/WB Data/08_metrics_reports/wb_card_<nm_id>/`
   - `screenshots/`
   - `/private/tmp/wb_card_<nm_id>/diagnostics/`
2. Open the card URL in installed Google Chrome.
3. Wait at least 3 seconds.
4. Capture `screenshots/initial_page.png`.
5. Record collection time, final URL, Chrome title, and page status.
6. Close cookie banner only by clicking a visible accept button; wait 3 seconds and screenshot.
7. Collect visible first-screen text: title, brand, price, old price, rating, questions/reviews, selected color/size, stock, delivery, badges.
8. Scroll sequentially with `PageDown` or visible mouse/trackpad events; wait 3 seconds after each scroll.
9. Open native visible sections only: characteristics, description, seller, delivery, returns, reviews/questions, modals/tooltips.
10. Screenshot every important state and record the source of every value.
11. Store unknown fields as `null`, never guesses.
12. Write `card_data.json` and `card_report.md`.

## Interaction Notes

- `System Events click at {x,y}` may hang in this environment. Prefer keyboard navigation for scroll and CoreGraphics mouse events for visible clicks.
- Use Chrome Apple Events JavaScript only for safe diagnostics or reading the current page state. Do not use it to call network endpoints, extract media URLs, download files, or mutate the page.
- If Chrome or Codex returns focus unexpectedly, verify by URL/title and screenshot before continuing.

## Data Schema

Use this structure for `card_data.json` and extend only when visible data requires it:

```json
{
  "nm_id": null,
  "url": null,
  "final_url": null,
  "collected_at": null,
  "method": "manual_visible_chrome_audit",
  "browser": "Google Chrome",
  "page_status": null,
  "title": null,
  "brand": null,
  "seller": null,
  "shop": null,
  "price": null,
  "old_price": null,
  "discount": null,
  "rating": null,
  "reviews_count": null,
  "questions_count": null,
  "availability": null,
  "delivery": null,
  "colors": [],
  "selected_color": null,
  "sizes": [],
  "selected_size": null,
  "stock": null,
  "characteristics": {},
  "description": null,
  "return_conditions": null,
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

- URL and collection timestamp.
- Permission diagnostics summary.
- Sequential action log.
- Opened sections and screenshots.
- Table of found official WB data with source for each value.
- Separate section for extension overlay data, if any.
- Unavailable fields and exact reason.
- Quality checklist: no guesses, no image downloads, no API use, no bypass.

## Common Mistakes

| Mistake | Correct behavior |
|---|---|
| Mixing mpstats/mkeeper with WB data | Put it under `browser_extension_overlays` |
| Treating title-bar text as fully verified card data | Mark as `needs_manual_check` unless confirmed on page |
| Continuing after captcha/anti-bot | Screenshot, wait if allowed, then stop if unavailable |
| Downloading images for OCR | Do not download; use screenshots only |
| Parallel opening tabs or requests | Keep one visible Chrome tab and sequential actions |
