# Detailed Specification: Wildberries Card Data Collection

## Purpose

Perform a safe, reproducible manual audit of a single public Wildberries product card through installed Google Chrome on macOS. Collect all visible text data available to a normal user on the product card and its native expandable sections. Do not download product media, call WB APIs, or bypass technical restrictions.

## Output Location

For a card with `nm_id`, create:

```text
/Users/dmitrijmizinov/Documents/WB Data/08_metrics_reports/wb_card_<nm_id>/
```

Required files:

```text
card_data.json
card_report.md
screenshots/
```

Diagnostics may be stored in:

```text
/private/tmp/wb_card_<nm_id>/diagnostics/
```

## macOS Permission Checks

Before collection, verify:

1. Screen Recording: `screencapture` creates a visible screenshot.
2. Accessibility: `System Events` returns `UI elements enabled = true`.
3. Input Monitoring: listen-only `CGEventTap` returns `true`.
4. Automation for Google Chrome: active tab URL/title can be read.
5. Chrome JavaScript from Apple Events: harmless `document.title` returns the title.
6. Automation for System Events: harmless process query works.

If a check fails:

- Stop collection.
- Record exact error.
- Tell the user which settings pane to open:
  - `Системные настройки > Конфиденциальность и безопасность > Запись экрана и системного звука`
  - `Системные настройки > Конфиденциальность и безопасность > Универсальный доступ`
  - `Системные настройки > Конфиденциальность и безопасность > Мониторинг ввода`
  - `Системные настройки > Конфиденциальность и безопасность > Автоматизация`
  - Chrome: `Вид > Разработчикам > Разрешить JavaScript из событий Apple`

## Core Safety Constraints

- Work with one card URL only.
- Use installed visible Google Chrome.
- Do not use headless browser for the audit.
- Do not use WB APIs or endpoint calls.
- Do not download images, videos, thumbnails, or media files.
- Do not extract direct media URLs.
- Do not log in.
- Do not add to cart.
- Do not submit forms.
- Do not solve captcha or bypass anti-bot states.
- Use adaptive pauses: at least 1 second between routine visible actions when the page is stable; at least 3 seconds after navigation, page reloads, opening or closing modals, clicks that trigger loading, retries, or uncertain page state.
- Increase pause to 5-10 seconds for slow loading, errors, anti-bot/captcha states, automatic retries, or site limits.

## Data To Collect

### Official WB Product Data

- `nm_id`
- source URL and final URL
- title
- brand
- seller/shop
- price
- old price
- discount
- VAT note if visible
- rating
- reviews count
- questions count
- badges such as original, promotion, discount, buyer choice, bestseller
- selected color and all visible colors
- selected size and all visible sizes
- stock and availability
- delivery time, warehouse, region if visible
- return conditions
- fitting availability
- all characteristics
- description
- materials/composition
- package contents
- country of origin
- dimensions and weight
- warranty/certificates if visible
- seller legal info if accessible through native UI
- reviews/questions summary and visible public text

### Browser Extension Overlays

If extension overlays are visible, record them separately under `browser_extension_overlays`. Examples:

- mkeeper
- mpstats
- sales in 30 days
- revenue in 30 days
- visibility graphs
- commission/buyout metrics

Never mix extension overlay metrics with official WB card fields.

## Sequential Browser Procedure

1. Create output and diagnostics folders.
2. Open the card URL in Google Chrome.
3. Wait at least 3 seconds after opening the URL. If the tab was already fully loaded and no navigation occurred, wait at least 1 second.
4. Capture `screenshots/initial_page.png`.
5. Record:
   - timestamp
   - requested URL
   - final URL
   - Chrome title
   - page status
6. If cookie banner is visible:
   - screenshot before click
   - click visible accept button
   - wait at least 1 second, or 3 seconds if the banner triggers reload/layout changes
   - verify it disappeared
   - screenshot after click
7. Collect first-screen visible official WB data.
8. Record extension overlay data separately if visible.
9. Scroll sequentially with keyboard or visible mouse events.
10. Open native sections one by one:
    - characteristics and description
    - seller/shop/brand links or modal
    - delivery/returns/fitting
    - reviews/questions
    - visible tooltips/modals
11. After each action:
    - wait at least 1 second for routine scrolls and screenshots; use at least 3 seconds when the action triggers loading, modal state changes, or page state is uncertain
    - screenshot current state
    - record visible text
    - add action to log
12. For modals:
    - open only through native visible UI
    - wait at least 3 seconds after opening a modal that loads content; for already-rendered modal scrolls, wait at least 1 second
    - screenshot
    - record visible text
    - close
    - wait at least 1 second, or 3 seconds if the page relayouts/reloads
13. If a site restriction appears:
    - screenshot
    - record exact text
    - wait 5-10 seconds if automatic retry is offered
    - stop if access is not restored

## JSON Output

Use `null` for unknown fields.

```json
{
  "nm_id": "944359159",
  "url": "https://www.wildberries.ru/catalog/944359159/detail.aspx",
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

## Screenshot Naming

Recommended names:

```text
initial_page.png
cookie_before_click.png
cookie_after_click.png
first_visible_state.png
characteristics_opened.png
characteristics_expanded.png
description_opened.png
description_expanded.png
seller_info_opened.png
delivery_opened.png
reviews_questions_summary.png
modal_<short_name>.png
unavailable_or_error_state.png
```

## Acceptance Criteria

The audit is complete when:

- `card_data.json` exists.
- `card_report.md` exists.
- `screenshots/` exists.
- All safe native visible sections were checked.
- Each important value has a source.
- Unknown fields are `null`.
- Extension data is separated.
- No product media was downloaded.
- No WB API or background scraping was used.
- Any access limitation is documented with screenshot and exact text.
