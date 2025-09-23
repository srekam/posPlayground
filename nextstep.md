**Role:** You are my senior Flutter product engineer. I already have a POS *Catalog* UI. I want you to list **exactly what to add** (features, data, flows) so the app becomes usable—**without giving implementation code**. For each item, describe the purpose, inputs/outputs, UX states, and acceptance criteria. Keep everything Flutter-appropriate (phone/tablet), but explain in framework-agnostic terms.

## 1) Cart logic & subtotal (foundational)

* **Goal:** Turn my Catalog into a working cart.
* **What to add:** cart state, add/increase/decrease/remove, clear, persistent across navigation until checkout, currency formatting.
* **Inputs/Outputs:** package selection → cart lines; output = line totals + **Subtotal**.
* **States:** empty cart, single item, multiple items, max qty guard.
* **Acceptance:** Subtotal updates instantly; removing last line shows empty state message.

## 2) Discounts & pricing rules

* **Goal:** Support common price scenarios.
* **What to add:** per-line manual discount (%/amount), cart-level discount, coupon/voucher field (validate locally for now), automatic bundle price (e.g., “Adult + Kid”).
* **Constraints:** never negative totals; permissions required for manual discount.
* **Acceptance:** Clearly shows original vs discounted price; subtotal reflects discount; error states for invalid coupons.

## 3) Checkout flow (mock payments)

* **Goal:** A guided flow to confirm and take payment.
* **What to add:** review screen (items, discount, tax if any), payment method selection (cash/QR/bank card, mock), amount tendered & change for cash.
* **States:** success, cancelled, insufficient amount, offline warning.
* **Acceptance:** Completing checkout transitions to Receipt screen and locks the cart (no accidental edits).

## 4) Ticket issuance model (no backend yet)

* **Goal:** Define what a “ticket” is at creation time.
* **What to add:** ticket ID (ULID/UUID), short human code (e.g., ABC-7F3Q), type (single/multi/timepass/credit), **quota/minutes**, validity window, lot/shift numbers, issue timestamp.
* **Security stub:** mention **HMAC signature** for later (server-side truth), but keep it conceptual for now.
* **Acceptance:** After checkout, a ticket object is produced for each sellable unit and passed to receipt.

## 5) Receipt view + “ready-to-print” payload

* **Goal:** Show a printable receipt/ticket.
* **What to add:** receipt layout spec (logo, items, totals, payment method, short code, QR payload, validity times, terms), a “Reprint” button, and a print payload (ESC/POS-ready text blocks; stub now).
* **States:** first print vs reprint badge; print error state placeholder.
* **Acceptance:** Receipt shows a scannable QR preview and a short code; reprint shows a clear **REPRINT** watermark/label.

## 6) QR encode/decode contract

* **Goal:** Define the QR content format (no code).
* **What to add:** JSON fields: `{ v, tid, t (token), s (sig placeholder), lf (lot), tp (type), valid_from, valid_to, quota_or_minutes }`.
* **Rules:** keep it compact; short code printed outside QR; future server will verify **sig**.
* **Acceptance:** The Gate screen can read the QR string and parse these fields in memory (mock).

## 7) Gate scan → PASS/FAIL decision (mock validator)

* **Goal:** Turn the scanner UI into a decision flow.
* **What to add:** a local “mock validator” that checks ticket status/expiry/quota (in memory), decrements quota on PASS, and returns **reason codes** on FAIL (expired, quota\_exhausted, not\_started, invalid\_signature\_stub, wrong\_device if binding used later).
* **UX:** big PASS/FAIL feedback, remaining uses/time, sound/vibration hint; a small counter for scans this shift.
* **Acceptance:** Same ticket scanned repeatedly will PASS then FAIL with **duplicate\_use** mock reason.

## 8) Offline awareness & outbox (lightweight, conceptual)

* **Goal:** Make the app resilient without a server.
* **What to add:** an **Outbox** concept that records events to sync later (`sale`, `redemption`, `reprint`, `refund`), a status badge (Online/Offline), and a minimal “allow-list” concept for Gate (tickets considered valid in the last X minutes).
* **Rules:** When offline, cap kiosk/POS sells per shift; show toast when queueing events.
* **Acceptance:** Toggling “simulate offline” still allows actions and stores events for future sync.

## 9) Reprint & refund with approval gates

* **Goal:** Reduce staff fraud opportunities.
* **What to add:** role model (Cashier/Supervisor/Admin), PIN dialog for risky actions (reprint, refund, manual discount), reason picker with free-text.
* **Audit:** each action produces an **audit event** (who/when/what/why).
* **Acceptance:** Attempting reprint/refund without proper role prompts for supervisor PIN and logs an audit record.

## 10) Shifts & cash drawer basics

* **Goal:** Track per-shift accountability.
* **What to add:** *Open Shift* (cash float), per-shift counters (sales, refunds, reprints), *Close Shift* with expected vs counted cash and difference.
* **Reports:** a simple shift summary view (list with totals).
* **Acceptance:** Actions are blocked when no shift is open (POS/Kiosk), and the summary view reflects today’s activity.

---

### Nice-to-have (if time allows—still no code, just specs)

11. **Device registration & roles**

* First-run device registration (POS/Gate/Kiosk), permanent `device_id`, feature flags per device type.

12. **Kiosk mode UX**

* Full-screen locked flow (no app chrome), admin PIN to exit, offline sell cap, simple payment stub.

13. **Design tokens & accessibility pass**

* Central color/typography/spacing tokens, large touch targets (≥48dp), high-contrast dark theme by default, Thai/English number formatting.

14. **Testable contracts**

* Describe unit-test intentions for: pricing rules, mock validator, cart math, and QR contract encode/decode (no code—just what to test).

---

## Output format I want from you

For each numbered item above, provide:

* **Purpose** (1–2 sentences)
* **Data contract** (fields in/out; example values)
* **User flows & states** (happy path + errors)
* **Guardrails** (permissions, limits, fraud controls)
* **Acceptance criteria** (bulleted; testable)