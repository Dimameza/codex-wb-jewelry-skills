# Detailed Specification: Wildberries Card Data Collection

## Purpose

Perform a safe, reproducible visible audit of a single public Wildberries product card through installed Google Chrome on macOS. Collect visible official WB text data and native expandable UI data available to a normal user. Do not download product media, call WB APIs, use headless scraping, or bypass technical restrictions.

## Output Location

For a card with `nm_id`, create:

```text
/Users/dmitrijmizinov/Documents/WB Data/08_metrics_reports/wb_card_<nm_id>/
  card_data.json                  # root latest only
  card_report.md                  # root latest only
  screenshots/                    # latest evidence copy when latest-policy passes
  runs/<run_id>/
    card_data.json
    card_report.md
    run_metrics.json
    screenshots_manifest.json
    action_log.jsonl
    screenshots/
    diagnostics/
      ocr/
      viewport/
```

Partial, failed, stale, or OCR-zero runs must stay under `runs/<run_id>/` and must not overwrite root latest.

## Preflight

### `input_path_preflight`

Run before public-first and before any browser/network action:

| Check | Success criteria | On failure |
|---|---|---|
| WB URL / `nm_id` | exactly one `nm_id` extracted | stop |
| URL normalization | URL is a WB card URL or normalizes to one | stop |
| Output folders | WB Data output folders writable | stop |
| WB-only path guard | runtime/config/artifact paths do not point to `/Users/dmitrijmizinov/Documents/ATM Network` | stop |

Visible OCR text from the current Chrome window is not a path-guard violation. ATM Network files, caches, configs, scripts, or artifact paths are violations.

### `visible_chrome_preflight`

Run only before the visible Chrome layer:

| Check | Success criteria |
|---|---|
| Screen Recording | `screencapture` creates a visible screenshot |
| Accessibility | `System Events` returns `UI elements enabled = true` |
| Input Monitoring | listen-only `CGEventTap` returns `true` |
| Automation: Chrome | active tab URL/title can be read |
| Chrome Apple Events JS | harmless `document.title` returns title |
| Automation: System Events | harmless process query works |
| Swift OCR runner | OCR command below returns text/status |

Swift OCR command:

```bash
swift -module-cache-path /private/tmp/wb_swift_module_cache src/ocr/vision_ocr.swift <screenshot.png>
```

If visible preflight fails, stop the visible layer. In hybrid mode, continue only as `public_only_degraded` when the user has not requested `force_visible`.

## Core Safety Constraints

- Work with one card URL only.
- Use installed visible Google Chrome.
- Do not use headless browser for visible audit.
- Do not use WB APIs or endpoint calls.
- Do not download images, videos, thumbnails, media files, or direct media URLs.
- Do not log in, add to cart, submit forms, solve captcha, or bypass anti-bot states.
- Prefer read-only visible viewport text to avoid unnecessary screenshots.
- If no screenshot is captured, OCR is not required.
- If a screenshot is captured as evidence/source, run OCR immediately through `capture_recognize_flush`.
- Do not perform the next click, scroll, navigation, or read-after-state-change until the current screenshot has status `recognized_and_flushed`.
- Separate official WB fields from extension overlays under `browser_extension_overlays`.

Adaptive waits:

| Situation | Wait |
|---|---|
| stable polling | `100-200 ms` |
| routine scroll/read/screenshot on stable UI | at least `1s` |
| navigation/reload/modal/loading click/retry/uncertain state | at least `3s` |
| slow/error/anti-bot/captcha/site-limit state | `5-10s` |

## Swift OCR Runner

Before the first screenshot gate, run an OCR smoke-test with `/private/tmp/wb_swift_module_cache`. A warmed binary or persistent runner is allowed after the smoke-test, but fallback execution must keep the same module cache path.

Record OCR failures as `ocr_runner_unavailable` in `blocking_warnings`. Save OCR text for every screenshot in `diagnostics/ocr/`. Add `ocr_status` to `screenshots_manifest.json`.

## `capture_recognize_flush`

All screenshots must use this sequence:

```text
capture_recognize_flush(name, expected_context, expected_fields):
    assert pending_ocr_jobs == []
    capture screenshot
    write screenshots_manifest.json status = captured
    append action_log.jsonl: screenshot_captured
    run OCR immediately
    save OCR text to diagnostics/ocr/
    append action_log.jsonl: ocr_started, ocr_completed
    parse official WB data and extension overlay data separately
    update card_data.json sources and unavailable_fields
    update run_metrics.json
    write screenshots_manifest.json status = recognized_and_flushed
    append action_log.jsonl: parsed, flushed, next_action_allowed
    rebuild card_report.md only on final or major checkpoint
```

Blocking failures:

- `blocked_by_unrecognized_screenshot`
- `ocr_runner_unavailable`
- `required_screenshot_missing_ocr`

Do not batch screenshots for final OCR. Do not close a panel before all required panel screenshots are recognized. Do not set `audit_status = "complete"` while any required screenshot is unrecognized.

## Official WB Data To Collect

- `nm_id`
- source URL and final URL
- title
- brand
- seller/shop
- price, old price, discount, VAT note if visible
- rating, reviews count, questions count
- badges such as original, promotion, discount, buyer choice, bestseller
- selected color and all visible colors
- selected size and all visible sizes
- stock and availability
- delivery time, warehouse, region if visible
- return conditions and fitting availability
- all characteristics and description
- materials, composition, package contents
- country of origin, dimensions, weight
- warranty/certificates if visible
- seller legal info if accessible through native UI
- reviews/questions summary and visible public text when requested and safe

Use `null`, `{}`, or `[]` for unknown fields and add an exact unavailable reason. Never guess.

## Browser Extension Overlays

If extension overlays are visible, record them separately under `browser_extension_overlays`.

Examples:

- mkeeper
- mpstats
- sales in 30 days
- revenue in 30 days
- visibility graphs
- commission/buyout metrics

Never mix extension overlay metrics with official WB card fields.

## Sequential Browser Procedure

1. Run `input_path_preflight`.
2. Create run folder and draft `card_data.json`, `run_metrics.json`, `screenshots_manifest.json`, and `action_log.jsonl`.
3. Decide if visible Chrome is needed. If visible is unavailable and not forced, record `public_only_degraded`.
4. Run `visible_chrome_preflight` only before visible Chrome actions.
5. Open the card URL in Google Chrome.
6. Wait at least `3s` after navigation, or `1s` if an already loaded tab was only focused.
7. Capture `initial_page.png` through `capture_recognize_flush`.
8. If cookie banner is visible, click only a visible accept button, then screenshot through `capture_recognize_flush`.
9. Collect first-screen official WB data and extension overlays separately.
10. Recompute missing required fields.
11. Open native sections only while they close required fields: characteristics/description, seller, delivery/returns/fitting, reviews/questions, visible tooltips/modals.
12. Stop before recommendation zones: `Продавец рекомендует`, `Смотрите также`, `Похожие товары`, `Вы недавно смотрели`.
13. If a site restriction appears, screenshot through `capture_recognize_flush`, record exact text, wait `5-10s` only if automatic retry is offered, then stop if access is not restored.

## Click Candidate Resolver

For `Характеристики и описание`, choose the best visible clickable candidate:

| Signal | Rule |
|---|---|
| text | exact or close match to `Характеристики и описание` |
| role | prefer `button`, `tab`, `summary`, `a`, click handler, or `cursor:pointer` |
| size | reject containers larger than 70% viewport width or height |
| visibility | click point inside viewport |
| overlap | click point is not covered by another element |
| context | product card area, not header/footer/recommendations |

If only a large parent container matches, search inside it for a child clickable element. If no safe candidate exists, stop panel collection with `characteristics_button_not_clickable`.

Primary click method: CoreGraphics mouse move/down/up at the candidate center point.

`System Events click at {x,y}` is allowed only as fallback with timeout and diagnostics. Allow at most one retry after revalidating coordinates and overlays.

## Characteristics And Description Panel

After the click:

1. Append `clicked_characteristics_description`.
2. Wait `300-500 ms` for animation start.
3. Poll every `100-200 ms` for up to `8s`.
4. Confirm:
   - heading or marker `Характеристики и описание` is visible;
   - right panel, native modal, or drawer appeared;
   - bounds are stable for at least two polling cycles;
   - visible panel text is non-empty;
   - active scroll container belongs to the panel.
5. Only when `panel_state = "opened_stable"`, call `capture_recognize_flush("characteristics_description_panel_top", ...)`.

If panel opening fails:

- capture diagnostic screenshot through OCR gate;
- record `panel_open_failed`;
- do not scroll the page as if the panel opened;
- do not write background page text into panel data.

Panel scroll rules:

- Scroll only inside the panel container.
- Before every scroll, require previous screenshot status `recognized_and_flushed`.
- After each scroll, call `capture_recognize_flush`.
- Stop when OCR text no longer changes or panel bottom is reached.
- Main page scroll is forbidden while the panel is open.

## JSON Output

Use this schema as the baseline:

```json
{
  "audit_status": "complete | partial | failed | public_only_degraded",
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

## Source Labels

Use source labels:

- `visible_text`
- `screenshot_ocr`
- `chrome_title`
- `chrome_current_tab_text`
- `extension_overlay`

Add `needs_manual_check` for uncertain OCR, ambiguous title-derived data, or extension-derived values.

## Latest Policy And Stale Runs

Root latest may be updated only when:

```json
{
  "audit_status": "complete",
  "pending_ocr_jobs": [],
  "all_required_screenshots_recognized": true,
  "panel_state": "opened_stable",
  "blocking_warnings": []
}
```

`non_blocking_warnings` do not block latest. Example: `extension_overlay_visible` is non-blocking when overlay data is separated from official WB data.

Do not treat stale runs as success evidence. A previous run with `ocr_runs_total = 0`, old artifact schema, missing screenshot manifest, or incomplete latest-policy gate cannot be resumed as successful. On `--resume`, validate the last completed gate; otherwise start a new run and mark the old run as `superseded_partial_run`.

## Report Requirements

`card_report.md` must include:

- URL, `nm_id`, run_id, and collection timestamp.
- Split-preflight summary and OCR runner summary.
- Sequential action log.
- Opened sections and screenshots with OCR statuses.
- Table of found official WB data with source for each value.
- Separate section for extension overlay data, if any.
- Unavailable fields and exact reason.
- `blocking_warnings`, `non_blocking_warnings`, and latest-policy result.
- Quality checklist: no guesses, no image downloads, no API use, no headless browser, no bypass, no ATM Network runtime/config/artifact paths.

Full Markdown rebuild is required on final or major checkpoint only. Gate checkpoints must update JSON, metrics, manifest, and action log.

## Acceptance Criteria

The audit is complete only when:

- `input_path_preflight` passed.
- Visible checks passed, or visible layer is explicitly documented as `public_only_degraded`.
- Every required screenshot has OCR text and status `recognized_and_flushed`.
- `pending_ocr_jobs = []` before every browser action.
- `panel_state = "opened_stable"` before panel screenshot.
- Successful click method is `coregraphics`, or fallback is documented with timeout diagnostics.
- Latest-policy uses `blocking_warnings`, not general warnings.
- Partial, failed, stale, and OCR-zero runs do not overwrite root latest.
- Extension data is separated.
- No product media was downloaded.
- No WB API, background scraping, headless browser, or bypass was used.
- No ATM Network runtime/config/artifact paths were used.
