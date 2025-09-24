Prompt: “Design a Provider/Owner Console to oversee all customer sites (multi-tenant), no code yet”

**Role:** You are my solutions architect and product designer. I rent this POS/ticket system to many businesses (tenants). I need a **Provider/Owner Console** to monitor and operate  **all sites across all tenants** —separate from each tenant’s own admin. Deliver  **specs only (no code)** : pages, KPIs, data contracts, APIs, workflows, alerts, security, and acceptance criteria.

**Context/Tech:**

* Existing stack: PHP + MongoDB, REST JSON on port  **48080** .
* Multi-tenant: `Tenant → Store → Device`.
* Devices: POS, Gate, Kiosk, Admin.
* Mongo is private in Docker network (no host port).
* Timezone Asia/Bangkok, currency THB.

---

## 1) Personas & goals

* **Provider Owner/Exec:** top-level KPIs, growth, revenue, SLA.
* **NOC/Support Agent:** live health, incidents, impersonate tenant to assist.
* **Billing Ops:** subscriptions, usage, invoices, dunning.

**Acceptance:** All UX supports these three personas without mixing tenant-only settings.

---

## 2) Global navigation (provider scope)

* **Overview (Fleet Dashboard)**
* **Tenants** (directory + drill-downs)
* **Stores & Devices** (cross-tenant search)
* **Alerts** (issues queue)
* **Reports** (cross-tenant)
* **Billing** (plans, usage, invoices)
* **Operations** (webhooks, keys, releases/rollouts)
* **Security** (roles, SSO, impersonation policy)
* **Settings** (provider-wide config)

**Acceptance:** Provider nav is visually distinct from tenant admin; clear “Provider” badge.

---

## 3) Overview (Fleet Dashboard)

**Purpose:** One-page health + business snapshot.

**KPIs (cards):**

* Tenants total / active
* Stores total / active
* Devices online (last heartbeat ≤ 2 min) / offline
* Open incidents / critical alerts
* 24h sales THB (all tenants), redemptions, refund rate, reprint rate
* Sync lag p95 (POS & Gate)

**Visuals:**

* Sparklines 24h sales & redemptions
* Map / table of top stores by throughput
* “What changed” panel (new tenants, plan upgrades, churn risk)

**Data contracts:**

* `metrics.overview` → `{ tenants_active, stores_active, devices_online, devices_total, sales_24h, redemptions_24h, refund_rate, reprint_rate, sync_lag_p95 }`

**Acceptance:** Loads < 1s with cached aggregates; clicking any KPI opens the corresponding filtered view.

---

## 4) Tenants directory & drill-down

**Directory table columns:** Tenant, Plan, Stores, Devices, 24h Sales, Refund %, Reprint %, SLA %, Alerts count, Last activity.

**Tenant detail tabs:**

* **Summary:** mini-KPIs, plan, contacts, last 30d sales & uptime.
* **Stores:** list with status (online/offline, last sale, open shift).
* **Devices:** heartbeats, firmware/app version, capabilities.
* **Alerts:** current & history.
* **Usage/Billing:** plan limits vs usage (stores, devices, API calls).
* **Impersonate** (secured): “View tenant admin as…” with audit.

**APIs:**

* `GET /provider/tenants` (filters/sort/search)
* `GET /provider/tenants/{tenant_id}/summary|stores|devices|alerts|usage`

**Acceptance:** Switching tenant context updates breadcrumbs and scoping; impersonation requires approval & logs an audit event.

---

## 5) Stores & Devices (cross-tenant)

**Store table:** Tenant, Store, Status, Last Sale, Open Shift?, Today Sales, Alerts.

**Device table:** Device, Type, Tenant/Store, Status, Last Seen, App Version, Issues.

**Device drill-down:** heartbeats timeline, error rate, last 50 requests, configuration, rotate token, suspend.

**APIs:**

* `GET /provider/stores?filters`
* `GET /provider/devices?filters`
* `POST /provider/devices/{id}/suspend|resume|rotate_token`

**Acceptance:** Bulk actions on filtered sets (e.g., suspend outdated app versions).

---

## 6) Alerts & Incidents

**Alert types:** offline, sync_lag_high, reprint_spike, refund_spike, fail_rate_gate, after_hours_sales, webhook_failures.

**Queue:** severity, tenant/store/device, first_seen, last_seen, count, status (open/ack/resolved), assignee.

**Workflows:**

* Auto-rules (e.g., offline > 10m → open alert).
* Link to device/store/tenant; add notes; attach RCA; resolve with reason code.
* Maintenance window suppresses alerts.

**APIs:**

* `GET /provider/alerts`
* `POST /provider/alerts/{id}/ack|resolve`
* `POST /provider/alerts/rules` (thresholds)

**Acceptance:** New offline device appears in queue ≤ 2 min; resolution requires reason.

---

## 7) Reports (cross-tenant)

**Reports:**

* **Sales (provider-wide):** by tenant/store; gross, net, discounts, taxes; payment mix.
* **Throughput:** redemptions/hour, PASS/FAIL %, reasons.
* **Risk & Fraud:** reprint/refund spikes, duplicate scans, abnormal after-hours.
* **Uptime/SLA:** per tenant/store/device online %, mean time to recover.
* **Growth:** new tenants, store expansion, device growth, ARPU.

**Filters:** date range, tenant, store, device, package, payment type.

**Outputs:** tables, charts, CSV export, scheduled email.

**APIs:**

* `GET /provider/reports/{report_id}?filters`

**Acceptance:** Totals reconcile with tenant-level reports; export matches on-screen.

---

## 8) Billing (provider view)

**Pages:** Plans & limits; Subscriptions per tenant; Usage (stores count, devices, API calls); Invoices & dunning; Trial tracking.

**Data:**

* `subscription { plan, start, renew_on, status }`
* `usage { stores, devices, api_calls, webhooks, storage_gb }`

**APIs:**

* `GET /provider/billing/tenants`
* `POST /provider/billing/tenants/{id}/plan` (change plan)
* `GET /provider/billing/usage?range=…`

**Acceptance:** Over-limit tenants raise soft alerts; plan changes audited.

---

## 9) Operations (webhooks, releases, maintenance)

**Webhooks (provider-managed):** configure destinations for provider-level events (e.g., alert.created).

**Releases:** staged rollout flags for API/app versions; track adoption.

**Maintenance:** schedule windows per tenant/store.

**APIs:**

* `GET/POST /provider/webhooks`
* `GET/POST /provider/releases` (feature flags, min app version)
* `POST /provider/maintenance` (window, scope)

**Acceptance:** Feature flag toggles reflect within 5 min in device bootstraps.

---

## 10) Security (provider RBAC & impersonation)

**Roles:** Provider-Admin, NOC, Billing-Ops, Read-Only.

**Policies:**

* Impersonation requires ticket+reason; time-boxed session; clear banner; full audit trail.
* IP allow-list for admin console (optional).
* 2FA for provider accounts.

**APIs:**

* `POST /provider/impersonate/start` → `tenant_token`
* `POST /provider/impersonate/stop`
* `GET /provider/audit` (actor, action, scope)

**Acceptance:** All impersonations visible in audit; tenants can see when provider accessed.

---

## 11) Data & telemetry model (additions)

**New collections:**

* `provider_metrics_daily` (per tenant/store/device aggregates)
* `device_heartbeats` (time-series)
* `provider_alerts`
* `provider_audits`
* `subscriptions`, `usage_counters`

**Indexes:**

* `(tenant_id, date)` on metrics; `(device_id, ts)` on heartbeats; `(status,severity,last_seen)` on alerts.

**Ingestion:**

* API emits internal events; background jobs roll up minute→hour→day aggregates.

**Acceptance:** Daily aggregates available by 01:10 local; dashboard uses cached minute aggregates.

---

## 12) Health signals & SLAs

**Signals per device:** last_heartbeat, error_rate_5m, request_latency_p95, sync_lag_sec, app_version.

**Store SLA:** %online per day; average checkout latency; gate FAIL rate.

**Thresholds (defaults):**

* Offline if no heartbeat > 120s.
* Sync lag high if > 90s.
* Reprint spike if > 3× weekly median in 1h.

**Acceptance:** SLA report calculates correctly over the selected period with timezone handling.

---

## 13) Provider-level APIs (summary)

* `GET /provider/overview` → metrics cards
* `GET /provider/tenants`, `/stores`, `/devices`
* `GET /provider/alerts`, `POST /provider/alerts/{id}/ack|resolve`
* `GET /provider/reports/*`
* `GET /provider/billing/*`, `POST /provider/billing/tenants/{id}/plan`
* `POST /provider/impersonate/*`
* All responses include `server_time`, `request_id`, `data`, `error{code,msg}`.

**Acceptance:** All list endpoints support pagination, sorting, and server-side filters.

---

## 14) Guardrails & privacy

* Strict tenant isolation; provider views read-only unless explicitly elevated.
* PII minimization in provider views (masking unless impersonated).
* Rate limiting & audit on sensitive actions (suspend device, rotate tokens).
* Change history on plan/limits/flags.

**Acceptance:** Attempt to edit tenant data without elevation returns `403 E_PERMISSION`.

---

## 15) UX patterns & empty states

* Every table has quick filters (status, tenant, version).
* Empty states with how-to-fix (e.g., “No heartbeats in 24h—check device time”).
* Toasts for background refresh; banner when impersonating.
* CSV export buttons on Reports and Alerts.

**Acceptance:** NOC can triage a new outage from Overview → Alerts → Device within three clicks.

---

### Deliverables

* Wireframe descriptions per page (layout zones, key widgets).
* Data contracts & sample payloads for `/provider/overview`, `/provider/alerts`, `/provider/tenants/{id}/summary`.
* Acceptance criteria checklists per page.
* Background jobs list (metrics rollups, alerting cron).
* Security checklist (RBAC matrix, impersonation flow).

---
