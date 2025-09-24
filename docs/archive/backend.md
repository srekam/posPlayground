Awesome—here’s the fully-filled **spec pack (1–15)** for your **Loyverse-style backend + admin** tailored to  **coupon/ticket sales** . Per your note: we’ll deploy as **two Docker services** (Backend Web Admin + REST API on  **port 48080** ). **MongoDB runs in the same Docker network and is not port-forwarded** (internal only).

---

# 0) Deployment frame (high-level; no code)

* **Services:**
  * `api`: REST JSON service (listening on  **48080** )
  * `admin`: Web Admin (can reverse-proxy to `api` internally)
  * `mongo`: internal only, on the same Docker network, **no host port** exposed
* **Networking:**
  * `admin` ↔ `api` via internal DNS (`http://api:48080`)
  * `api` ↔ `mongo` via internal DNS (`mongodb://mongo:27017/app`)
* **Security:**
  * Only `admin` and `api` published to host; `mongo` stays private
  * ENV secrets via Docker secrets (JWT/HMAC keys, DB creds)

Acceptance:

* Hitting `http://localhost:48080/health` returns OK from API.
* Admin UI reachable on its exposed port; it can log in and read settings.
* Mongo not reachable from host network.

---

# 1) Tenants, Stores & Devices

**Purpose**

Multi-tenant isolation; per-store configuration; device enrollment for POS/Gate/Kiosk/Admin.

**Data schema (key fields)**

* **Tenant** : `tenant_id`, `name`, `legal_name`, `tz`, `currency=THB`, `billing_plan`, `status`, `created_at`
* **Store** : `store_id`, `tenant_id`, `name`, `address`, `tz`, `tax_id?`, `receipt_header/footer`, `logo_ref?`, `active`
* **Device** : `device_id`, `tenant_id`, `store_id`, `type ∈ {POS,GATE,KIOSK,ADMIN}`, `name`, `registered_at`, `registered_by`, `status ∈ {active,suspended,revoked}`, `device_token_hash`, `caps` (e.g., `can_sell`, `can_redeem`, `kiosk_mode`, `offline_cap`), `notes`

**Admin pages & fields**

* Tenants list → Tenant detail (basic info, billing plan, status)
* Stores list → Store detail (receipt header/footer/logo; time zone; paper width)
* Devices list → Device detail (type, capabilities, suspend/revoke, rotate token, notes)
* “Pair device” wizard: enter `SiteKey` (tenant/store scoped) → approve → issue token

**API contracts**

* `POST /auth/device/register` → input: `site_key`, device meta → output: `device_id`, `device_token`
* `POST /auth/device/login` → `device_id`, `device_token` → short-lived access token
* `GET /stores` (scoped)
* `GET /devices/me` (capabilities for current device)

**Workflows & edge cases**

* Rotating token invalidates all current sessions.
* Suspended device: requests return `E_DEVICE_SUSPENDED`.

**Guardrails**

* Device tokens hashed at rest; rate-limited register/login.
* Store scoping enforced on every request.

**Acceptance**

* A suspended device can’t call any business endpoint (gets 403 + code).
* Admin can rotate a token and see the last use timestamp update afterward.

---

# 2) Employees, Roles & Permissions (RBAC)

**Purpose**

Control sensitive actions (refund, reprint, manual discount, settings).

**Data schema**

* **Employee** : `employee_id`, `tenant_id`, `name`, `email`, `pin_hash`, `status`, `created_at`
* **Membership** : `employee_id`, `store_id`, `roles` (array), `active`
* **Role** : `role_id`, `name`, `permissions` (strings)
* **Permission set (examples)** : `sell`, `redeem`, `refund`, `reprint`, `manual_discount`, `shift_open`, `shift_close`, `settings_write`, `employee_manage`, `reports_view`

**Admin pages**

* Employees (CRUD, assign to stores, reset PIN, suspend)
* Roles (create/edit permissions), Permission matrix viewer
* Access logs (who logged in, where)

**API**

* `POST /employees/login` (email+PIN or device-mediated)
* `GET /employees/me` with `permissions`
* `POST /approvals/verify_pin` (for elevated actions)

**Workflows**

* Employee can have different roles by store.
* Elevation: reprint/refund/manual discount prompt for supervisor PIN.

**Guardrails**

* PIN retry lockout & audit.
* All role changes audited.

**Acceptance**

* User with no `manual_discount` cannot apply it (403).
* PIN failures logged with device and IP.

---

# 3) Catalog: Packages & Pricing

**Purpose**

Define sellable items and their default behavior for tickets.

**Data schema**

* **Package** : `package_id`, `tenant_id`, `store_id`, `name`, `type ∈ {single,multi,timepass,credit,bundle}`, `price`, `tax_profile`, `quota_or_minutes`, `allowed_devices?`, `visible_on {POS,KIOSK}`, `active_window {from,to}?`, `active`
* **PricingRule** : `rule_id`, `scope {store|tenant}`, `kind ∈ {line_percent,line_amount,cart_percent,cart_amount,promo_code,bundle,time_of_day}`, `params`, `active_window`, `priority`

**Admin pages**

* Items list; Package editor; Pricing rules (with preview calculator)

**API**

* `GET /catalog/packages?store_id=`
* `GET /pricing/rules?store_id=`

**Workflows**

* Time-of-day rule overrides base price only within window.
* Bundle computes as a single package with internal mapping (for reporting).

**Guardrails**

* Do not allow negative totals.
* Rules have explicit priorities and cannot conflict silently.

**Acceptance**

* Preview calculator shows identical totals to POS for the same cart.
* Inactive package never appears in POS/Kiosk payloads.

---

# 4) Tickets & Redemptions (server truth)

**Purpose**

Authoritative ticket lifecycle and redemption tracking.

**Data schema**

* **Ticket** : `ticket_id (ULID)`, `tenant_id`, `store_id`, `sale_id`, `package_id`, `short_code`, `qr_token`, `sig`, `type`, `quota_or_minutes`, `used`, `valid_from`, `valid_to`, `status ∈ {active,cancelled,refunded,expired}`, `lot_no`, `shift_id`, `issued_by`, `price`, `payment_method`, `printed_count`
* **Redemption** : `redemption_id`, `ticket_id`, `device_id`, `ts`, `result ∈ {pass,fail}`, `reason ∈ {expired,duplicate_use,wrong_device,not_started,exhausted,invalid_sig}`, `metadata`

**Admin pages**

* Ticket search (by short code/QR/token)
* Ticket detail timeline (issue → prints → redemptions → refunds)

**API**

* `GET /tickets/{id}`
* `POST /tickets/redeem` → input: `qr_token`, `device_id` → output: `pass|fail`, `reason`, `remaining`
* `POST /tickets/reprint` (requires approval)
* `POST /tickets/refund` (requires approval)

**Workflows**

* On PASS: decrement quota or time; append a redemption record.
* Duplicate scan within validity → `fail: duplicate_use`.

**Guardrails**

* `sig` verified server-side only.
* Device binding enforced if `allowed_devices` present.

**Acceptance**

* Same ticket can’t PASS twice once quota exhausted.
* Expired tickets always fail with `expired`.

---

# 5) Sales, Payments & Shifts (Cash Drawer)

**Purpose**

Mirror POS sale lifecycle and shift reconciliation.

**Data schema**

* **Sale** : `sale_id`, `tenant_id`, `store_id`, `device_id`, `cashier_id`, `items[{package_id, qty, price, discounts[]}]`, `subtotal`, `discount_total`, `tax_total`, `grand_total`, `payment_method ∈ {cash,qr,card,other}`, `amount_tendered`, `change`, `ts`
* **Shift** : `shift_id`, `store_id`, `device_id`, `opened_by`, `open_at`, `cash_open`, `closed_by?`, `close_at?`, `cash_expected?`, `cash_counted?`, `cash_diff?`, `totals {sales, refunds, reprints}`

**Admin pages**

* Shift open/close viewer; edit counted cash; list of shifts with diffs
* Sales browser (filters by date/store/device/staff)

**API**

* `POST /shifts/open` / `POST /shifts/close`
* `POST /sales` (atomically creates sale + issues tickets)
* `GET /sales/{id}`

**Workflows**

* POS cannot sell if no open shift (config switch).
* Closing shift locks subsequent edits and recalculates expected cash.

**Guardrails**

* Idempotency key on `/sales`.
* Refunds adjust shift totals.

**Acceptance**

* Close shift produces a fixed summary snapshot.
* Cash difference computed and stored.

---

# 6) Reprints, Refunds & Audit Logs (Anti-fraud)

**Purpose**

Track sensitive actions and require approvals.

**Data schema**

* **Reprint** : `reprint_id`, `ticket_id`, `ts`, `requested_by`, `approved_by`, `reason_code`, `reason_text`
* **Refund** : `refund_id`, `sale_id`, `ticket_ids[]?`, `amount`, `method`, `requested_by`, `approved_by`, `reason_code`, `ts`, `status`
* **AuditLog** : `audit_id`, `ts`, `actor_id`, `device_id`, `event_type`, `payload`, `ip`, `store_id`

**Admin pages**

* Audit explorer with filters & CSV export
* Reasons manager

**API**

* `POST /reprints` (requires `approvals/verify_pin`)
* `POST /refunds` (ditto)
* `GET /audits?filters…`

**Workflows**

* Risky actions emit webhooks (see §13).
* Reprint increments `printed_count` on ticket.

**Guardrails**

* Rate-limit reprints; daily cap per device/staff.
* All approvals require supervisor role + PIN.

**Acceptance**

* Reprint without approval returns `E_PERMISSION`.
* Audit stream shows complete story for any ticket.

---

# 7) Offline & Sync Contracts

**Purpose**

POS/Gate must function during outages with consistent reconciliation.

**Concepts**

* **Outbox** on device: batched ops: `sale`, `redemption`, `audit`, `shift_open/close`
* **Idempotency** : each op has `op_id` (ULID)
* **Allow-list** for Gate: list of “recently valid” tickets for quick PASS

**API**

* `POST /sync/batch` → array of ops; returns per-op status
* `GET /gate/bootstrap?window=minutes` → minimal allow-list + config

**Conflict rules**

* First PASS wins; later dup becomes `duplicate_use`.
* Server merges redemptions in ts order; returns authoritative remaining quota.

**Acceptance**

* Simulating offline on POS still allows sale→later sync with correct totals.
* No duplicate sales/redemptions after retries.

---

# 8) Settings (Loyverse-like)

**Purpose**

Central configuration per tenant/store.

**Sections & fields**

* **Features** : enable/disable `kiosk`, `gate_binding`, `multi_price`, `webhooks`
* **Billing & subscriptions** : plan, trial dates (display-only for now)
* **Payment types** : cash, QR, card, other; surcharges/fees
* **Taxes** : inclusive/exclusive, rates, default per package
* **Receipt** : header/footer text, logo, paper width, template blocks (ESC/POS text)
* **Ticket printers** : printer profiles, mapping by device
* **Access zones** : named areas (e.g., “Ball Pit”, “Trampoline A”) to tag packages and enforce device binding

**Admin pages**

* Settings overview with tabs; per-store override toggle

**Acceptance**

* Changing a setting is audited and effective on next bootstrap/payload fetch.
* Per-store overrides reflected in POS within one refresh.

---

# 9) Reports

**Purpose**

Owner visibility; fraud analytics.

**Reports & metrics**

* **Sales Report** : gross, discounts, net, taxes, per payment type
* **Shift Report** : per shift totals, cash open/close, diffs
* **Ticket Report** : issued vs redeemed, redemption rates by package/zone
* **Reprint/Refund Report** : counts, amount, reasons by staff/device
* **Gate Throughput** : scans/hour, PASS/FAIL ratios, failure reasons top list
* **Fraud Watch** : spikes (z-score) in reprints/refunds, after-hours sales, duplicate attempts

**Filters**

Date range, store, device, staff, package, zone.

**Outputs**

Tables + CSV export; charts in admin.

**Acceptance**

* Totals reconcile across Sales ↔ Shifts ↔ Tickets for same period.
* CSV export matches on-screen totals.

---

# 10) Public REST API (for Android apps)

**Purpose**

Stable, versioned contracts.

**Versioning & base**

* Base path: `/v1`
* Host/port: `http://<host>:48080` (internal admin calls use service DNS)

**Endpoints (summary)**

* Auth & bootstrap: `POST /auth/device/login`, `GET /gate/bootstrap`, `GET /catalog/packages`, `GET /pricing/rules`
* Shifts: `POST /shifts/open`, `POST /shifts/close`, `GET /shifts/current`
* Sales: `POST /sales`, `GET /sales/{id}`
* Tickets: `GET /tickets/{id}`, `POST /tickets/redeem`, `POST /tickets/reprint`, `POST /tickets/refund`
* Sync: `POST /sync/batch` (ops array with `op_id`)
* Health: `GET /health` (for readiness/liveness)

**Common response envelope**

* `server_time`, `request_id`, `data`, `error {code,message}`

**Error codes (examples)**

`E_DEVICE_SUSPENDED`, `E_PERMISSION`, `E_SHIFT_CLOSED`, `E_DUPLICATE_USE`, `E_EXPIRED`, `E_NOT_STARTED`, `E_EXHAUSTED`, `E_INVALID_SIG`, `E_RULE_CONFLICT`

**Acceptance**

* Each endpoint documents required headers (auth, idempotency key).
* 4xx for client errors, 5xx only for unexpected failures.

---

# 11) Security & Compliance

**Purpose**

Money & fraud protection.

**Controls**

* **HMAC** signing for `qr_token` + server verification only (secret rotated)
* JWT or signed device tokens; rotation supported
* Per-device & per-employee rate limits for risky endpoints
* IP/device fingerprint logging
* **Audit chain** : optional daily hash chain over audit entries to detect tampering
* Backups (daily), retention policy (e.g., 90 days raw audit, 365 days summaries)

**Acceptance**

* Rotating HMAC secret invalidates new issuance only; old tickets remain verifiable via versioned secret store.
* Requests from suspended devices/users are blocked and audited.

---

# 12) Admin UI Sitemap (mapped to your screenshot style)

**Sidebar groups**

* **Dashboard** : Today’s sales, redemptions, FAIL reasons, open shifts, alerts
* **Reports** : Sales, Shifts, Tickets, Reprint/Refund, Throughput, Fraud Watch
* **Items** : Packages, Pricing rules, Access zones
* **Employees** : Users, Roles, Access logs
* **Integrations** : Payments, Webhooks, Printers
* **Settings** : Features, Billing & subscriptions, Payment types, Taxes, Receipt, Ticket printers, Access zones
* **Stores** : Stores, POS devices (pair/suspend/rotate)

**Acceptance**

* Navigation mirrors sections 1–11; each page has filters, CSV export where relevant.

---

# 13) Eventing & Webhooks

**Purpose**

Cameras/BI/alerts integration.

**Events**

`sale.created`, `ticket.issued`, `ticket.redeemed.pass`, `ticket.redeemed.fail`, `reprint.created`, `refund.created`, `shift.closed`

**Delivery**

* Secret-signed header (`X-Signature`), retries with exponential backoff, dead-letter log

**Admin pages**

* Webhook endpoints (CRUD), test delivery, delivery logs & status

**Acceptance**

* Admin can send a test payload and see success/latency.
* Failed deliveries recorded with next retry schedule.

---

# 14) Mongo Collections & Indexes (high-level)

**Collections**

`tenants`, `stores`, `devices`, `employees`, `roles`, `memberships`, `packages`, `pricing_rules`, `sales`, `tickets`, `redemptions`, `shifts`, `refunds`, `reprints`, `audits`, `settings`, `webhooks`, `secrets (for HMAC versions)`

**Index suggestions**

* Time-series: `(store_id, ts)` on `sales`, `redemptions`, `audits`
* Lookup: `(ticket_id)` unique on `tickets`; `(qr_token)` unique
* Text: `short_code` text/unique
* Admin fast filters: `(employee_id, ts)`, `(device_id, ts)`, `(event_type, ts)`

**Acceptance**

* Query plans for common reports stay under p95 < 300ms with realistic volumes.
* Unique constraints prevent duplicate issuance for same `qr_token`.

---

# 15) Non-functional Requirements

**Performance**

* Common reads: <150 ms (catalog, bootstrap)
* Sale create (issue tickets): <500 ms p95 under normal load

**Reliability**

* At-least-once sync; idempotent writes across `/sales` and `/sync/batch`
* Graceful degradation when settings or pricing rules unavailable (cached)

**Observability**

* Structured logs with `request_id` and `device_id`
* Metrics: QPS, error rate by code, p50/p95 latency, reprint/refund rates
* Health endpoints: `/health` (liveness/readiness detail)

**Rollout**

* Separate **staging** and **production** stacks
* Versioned API (`/v1`) with deprecation policy
* Data migration plan documented for evolving schemas

**Acceptance**

* Synthetic checks (admin + api) pass health and basic workflows.
* Metrics dashboards show live rates and latencies.

---

## Final notes (dev next steps—no code)

* Create **ENV spec** (API_PORT=48080, DB_URI, JWT_SECRET, HMAC_KEY_V1, TZ, etc.).
* Decide **auth flavor** (JWT device tokens + role claims) and **idempotency header** naming.
* Prepare **sample payloads** for each endpoint for contract tests (Postman collections).
* Add **“Simulate offline”** switches in Admin for QA (force allow-list bootstrap & outbox replay).

If you want, I can now generate a **contract document** for the API (endpoint by endpoint with request/response JSON examples and error codes) or a  **checklist for Docker env variables and health checks** —still without code.
