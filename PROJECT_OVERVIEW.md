# ERPNext Hospitality Core - Project Overview

## 1. Purpose and Scope

Hospitality Core is a native ERPNext/Frappe hospitality application that implements hotel PMS operations directly inside ERPNext.

Core goals:
- Manage reservations, rooms, check-in/check-out, and guest history.
- Maintain a live folio ledger for each stay.
- Support corporate city-ledger billing and group billing.
- Integrate POS, payment, accounting, stock, and reporting in one system.
- Provide front-desk and housekeeping operational views.

Primary package/app name: `hospitality_core`

## 2. Technology Stack

- Framework: Frappe Framework (v14+), ERPNext integration
- Language: Python 3.10+
- Packaging: flit (`pyproject.toml`)
- Lint/format configuration: Ruff configured in `pyproject.toml`
- Frontend custom behavior: JS assets under `hospitality_core/public/js`

## 3. Repository Layout

### Root
- `README.md`: Full product and architecture narrative.
- `pyproject.toml`: Python package metadata and lint config.
- `COMPOSITE_ITEM_SETUP.md`: Setup/testing guide for recipe-based stock deduction.
- Utility scripts: `check_night_audit.py`, `verify_filters.py`, `verify_folio_balance.py`, `run_test_pos.py`, etc.

### App package root (`hospitality_core/`)
- `hooks.py`: Event hooks, scheduler, static assets, install hook.
- `setup/`: Installation/bootstrap scripts.
- `api/`: Extra API modules (notably composite item utilities).
- Many diagnostic and verification scripts (`verify_*.py`, `debug_*.py`, `check_*.py`).

### Main business module (`hospitality_core/hospitality_core/`)
- `doctype/`: Domain models (Guest, Reservation, Folio, Room, Group Booking, Expense, etc.).
- `api/`: Core server-side business logic.
- `page/`: Front-desk, tape chart, guest 360, housekeeping pages.
- `report/`: Script reports for operations and finance.
- `workflow/`: Workflow definitions (expense approval).
- `dashboard_data.py`: KPI data source methods.

## 4. Domain Model (Core DocTypes)

Main operational entities:
- `Hotel Reservation`: Stay lifecycle, room assignment, billing flags.
- `Guest Folio`: Financial ledger per reservation (or company master folio).
- `Folio Transaction` (child table): Atomic charge/payment/discount rows.
- `Hotel Room`, `Hotel Room Type`, `Room Rate Plan`: Inventory and pricing.
- `Guest`: Guest profile and customer linkage.
- `Hotel Group Booking` + `Hotel Group Booking Room`: Group reservation container.
- `Hotel Maintenance Request`: Maintenance and room status control.
- `Hospitality Expense`, `Expense Category`, `Hospitality Expense Tax`: Expense tracking.
- `Hospitality Accounting Settings`: Accounting integration settings.
- `Allowance Reason Code`: Void/allowance governance.
- `Item Recipe`, `Recipe Ingredient`: Composite item/ingredient logic.

## 5. Business Workflows

### Reservation lifecycle
- Reservation starts in `Reserved`.
- Check-in transitions to `Checked In`, room status becomes `Occupied`, folio opens.
- Check-out transitions to `Checked Out`, room becomes `Dirty`, folio closes after rule checks.
- Cancellation supported from `Reserved`/`Checked In` paths.

### Folio and transaction model
- Every financial movement is a `Folio Transaction`.
- Folio totals are recomputed from transactions:
  - `total_charges`
  - `total_payments`
  - `total_discounts`
  - `outstanding_balance`
  - `excess_payment`

### Corporate (city ledger) billing
- Company guest reservations can mirror company-liable transactions to a company master folio.
- Company folios remain open for debt tracking and post-stay settlement.

### Group billing
- Group reservations can route/mirror liabilities to a group master folio.
- Group checkout logic enforces financial constraints on master folio settlement.

### Night audit
- Scheduled daily via cron in hooks (`0 14 * * *`).
- Charges room rent for in-house reservations.
- Handles discounts/complimentary stays.
- Prevents duplicate daily rent posting.
- Handles overstays by extending departure date and tagging records.

## 6. Integrations and Event Hooks

Configured in `hospitality_core/hooks.py`.

Document event highlights:
- `Guest Folio.on_update` -> folio sync.
- `Folio Transaction.after_save` -> folio sync + accounting GL entries.
- `Folio Transaction.on_trash` -> folio sync.
- `POS Invoice.on_submit` -> room charge posting + accounting redirection + tax reclass + composite item processing.
- `POS Invoice.on_cancel` -> room charge reversal + accounting/tax reversal + composite item reversal.
- `Payment Entry.on_submit/on_cancel` -> folio payment posting/reversal.
- `Sales Invoice.on_submit/on_cancel` -> composite item processing.

Install hook:
- `after_install = hospitality_core.setup.after_install`

Assets injected globally:
- JS: analytics, POS room selection, POS auto-print, payment auto-print.
- CSS: print format styles.

## 7. Accounting Behavior

Core accounting logic in `hospitality_core/hospitality_core/api/accounting.py`:
- Creates GL entries for folio charges.
- Splits inclusive totals into net + Consumption Tax + VAT + Service Charge.
- Defers POS room-charge income into suspense.
- Realizes net income on payment posting.
- Uses `Hospitality Accounting Settings` for account configuration.

Bootstrap helper:
- `hospitality_core/init_accounting.py` can initialize default account settings.

## 8. POS and Payment Bridges

### POS bridge (`api/pos_bridge.py`)
- Detects amount paid via `Room Charge` mode of payment.
- Finds open folio for room/customer context.
- Posts each POS line item into folio transactions.
- Supports company mirroring for corporate guests.
- On POS cancel, removes linked folio rows (and mirrored rows).

### Payment bridge (`api/payment_bridge.py`)
- If `Payment Entry.reference_no` matches folio ID, posts payment credit transaction.
- Reverses linked folio transaction on cancellation.
- Calls accounting realization logic.

## 9. Composite Item Recipe System

Located primarily in `hospitality_core/api/composite_item_utils.py`:
- Detects composite items on POS/Sales invoices.
- Resolves active BOM/recipe.
- Validates ingredient stock.
- Creates Material Consumption stock entries for ingredient deduction.
- Reverses related stock entries on invoice cancellation.
- Exposes `get_available_to_make` utility.

Related setup guide:
- `COMPOSITE_ITEM_SETUP.md`

## 10. Frontend and Operations UI

Pages in `hospitality_core/hospitality_core/page/`:
- `front_desk_console`: arrivals/departures/availability snapshot.
- `tape_chart`: room-date occupancy grid.
- `guest_360`: profile + stay + spend history.
- `housekeeping_view`: room status board and status updates.

Client-side scripts:
- `public/js/pos_room_selection.js`: POS room selector and customer auto-lookup.
- `public/js/pos_invoice_auto_print.js`: Auto-print on POS submission.
- `public/js/payment_entry_auto_print.js`: Auto-print on payment submission.
- `hospitality_core/hospitality_core/api/auto_print.py` serves print settings.

## 11. Reporting and Analytics

Script reports under `hospitality_core/hospitality_core/report/` include:
- Daily arrivals/departures.
- House list.
- Guest ledger and city ledger.
- Folio balance summary.
- Daily sales consumption.
- Gross revenue.
- End-of-day report.
- Taxes and charges.
- Void and allowance report.
- Hospitality expense report.
- Hotel performance analytics (Occupancy, ADR, RevPAR).

Dashboard/KPI source:
- `hospitality_core/hospitality_core/dashboard_data.py`
- Setup utility: `hospitality_core/setup_dashboard.py`

## 12. Workflow and Governance

Defined workflow:
- `Hospitality Expense Approval` on `Hospitality Expense`.
- States: Draft -> Pending Approval -> Approved/Rejected.
- Roles: Hospitality User submits, Hospitality Manager approves/rejects.

Workflow file:
- `hospitality_core/hospitality_core/workflow/hospitality_expense_approval/hospitality_expense_approval.json`

## 13. Security and Permissions

Role strategy includes:
- `Hospitality User`
- `Hospitality Manager`
- `Housekeeping Staff`
- `System Manager`

Special permission behavior:
- `GuestFolio.has_permission` allows broad folio visibility for hospitality users to avoid owner-bound visibility issues in desk operations.

## 14. Setup and Initialization

Installation path (bench-based, from README):
1. `bench get-app ...`
2. `bench --site <site> install-app hospitality_core`
3. `bench --site <site> migrate`
4. `bench restart`

`after_install` bootstrap creates:
- Roles
- `Room Charge` mode of payment
- POS custom field (`hotel_room`)
- Default allowance reason codes
- Service items (`ROOM-RENT`, `POS-CHARGE`, `PAYMENT`)

## 15. Testing and Diagnostics Footprint

Automated and semi-automated tests exist at several layers:
- DocType tests (guest, reservation, folio, recipes).
- Report tests (`end_of_day_report`, analytics).
- Integration-focused scripts for POS cancellation, permissions, and auto-print.

Examples:
- `hospitality_core/hospitality_core/doctype/hotel_reservation/test_hotel_reservation.py`
- `hospitality_core/hospitality_core/doctype/hotel_reservation/test_hospitality_day.py`
- `hospitality_core/hospitality_core/report/end_of_day_report/test_eod_report.py`
- `hospitality_core/hospitality_core/report/hotel_performance_analytics/test_analytics.py`

There is also a large collection of operational verification scripts (`verify_*.py`, `check_*.py`, `debug_*.py`) intended for staged troubleshooting and data validation.

## 16. Operational Characteristics

Strengths:
- Strong event-driven automation with direct ERP accounting/stock integration.
- Real-time folio balancing and broad reporting coverage.
- Corporate/group billing patterns handled in-core.
- Multiple operational consoles and helper scripts for production support.

Complexity notes:
- Business logic spans many hooks and helper scripts, so execution order matters.
- Some behavior is environment-specific (bench restart, printer/browser behavior).
- Diagnostics and migration scripts are extensive; use cautiously on production data.

## 17. Suggested Reading Order for New Contributors

1. `README.md`
2. `hospitality_core/hooks.py`
3. `hospitality_core/hospitality_core/doctype/hotel_reservation/hotel_reservation.py`
4. `hospitality_core/hospitality_core/api/folio.py`
5. `hospitality_core/hospitality_core/api/night_audit.py`
6. `hospitality_core/hospitality_core/api/pos_bridge.py`
7. `hospitality_core/hospitality_core/api/accounting.py`
8. `hospitality_core/hospitality_core/report/hotel_performance_analytics/hotel_performance_analytics.py`

## 18. Document Metadata

- Generated on: 2026-05-17
- Scope: Codebase-level structural and functional overview
- File: `PROJECT_OVERVIEW.md`
