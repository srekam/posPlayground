ยอดเลย! ผมทำ “ชุดพรอมป์ภาษาอังกฤษ” ให้คุณเอาไปวางใน ChatGPT/Copilot เพื่อให้มันช่วยตั้งโปรเจ็กต์ Flutter (บน VS Code) และปั้น UI ก่อนฟีเจอร์ พร้อมคำแนะนำสั้นๆ เรื่อง “จะใช้ React ด้วยดีไหม?” และโฟลว์ทำ UI-first

---

# Should you also use React?

* ถ้าเป้าหมายหลักคือ “แอป Android/ iOS เดียวจบ” → ใช้ **Flutter เท่านั้น** จะตรงและเร็วกว่า (ลดงานซ้ำ)
* ถ้าอยากมี **เว็บแอดมิน** หรือ **เว็บเดโม UI** → ค่อยใช้ **React/Next.js** แยกโปรเจ็กต์ เพื่อทำ Back-office หรือ UI playground ก็ได้
  สรุป: เริ่ม Flutter สำหรับแอปก่อน แล้วถ้าต้องมีเว็บค่อยเพิ่ม React ภายหลัง

---

# Master Prompt (paste this in English)

**Title:** Build a Flutter playground-ticketing app (UI-first, Android focus)

**Role/Goal:**
You are my senior Flutter architect. Help me scaffold a production-ready Flutter app for an indoor playground ticketing system. I want to build **UI first** (screens, components, theming) before wiring backend. Target Android (phone/tablet). I’m using VS Code.

**Non-Goals for now:**
No real backend, just mock repositories & local models. No auth yet. Focus on screens and component library.

**Architecture & Tech choices:**

* Flutter 3.x (Material 3), Dart null-safe
* State management: Riverpod (hooks\_riverpod) or Bloc (either is fine; pick one and apply consistently)
* Navigation: go\_router
* Local store for mock data: simple in-memory repos (later replace with real API)
* QR: qr\_flutter (for generating), mobile\_scanner (for scanning)
* Printing (stub now): esc\_pos\_utils + platform channel placeholder (Bluetooth later)
* Lint: flutter\_lints + strict analysis
* Theming: design tokens (colors/typography/spacings) in one place

**App modules (packages or folders):**

```
lib/
  core/       (design tokens, theme, utils, router)
  domain/     (entities: Ticket, Package, Redemption, Shift)
  data/       (mock repos, adapters, sample JSON)
  features/
    pos/      (Catalog → Checkout → Receipt)
    gate/     (Scan → Result → Stats)
    kiosk/    (Full screen purchase flow; admin PIN)
    reports/  (Shift summary UI, simple charts)
  widgets/    (TicketCard, PriceChip, NumPad, AppButton, EmptyState)
```

**Screens to deliver (UI-only, with fake data):**

1. **POS**

* Catalog grid (packages with price, tags)
* Checkout panel (cart lines, subtotal, discount, cash quick-buttons)
* Receipt preview with QR + short code + lot number + time window
* Reprint/Refund dialogs (PIN input modal)

2. **Gate**

* Full-screen camera scanner (mobile\_scanner)
* PASS/FAIL result screen with large feedback, reason text, and remaining quota/time
* Small counter (per hour/shift), offline badge indicator

3. **Kiosk**

* Lock-task-like full screen, big buttons, minimal chrome
* Package → Payment method (mock) → Print stub (just show “Printing…”)
* Admin PIN to exit

4. **Reports**

* Shift summary list (total sales, refunds, reprints)
* Simple charts (mock data)

**Design tokens (seed):**

* Colors: primary #356DF3, secondary #5CC389, error #E5484D, surface #0B0F14 (dark-first), on-surface #E6EAF0
* Typography: Display/Headline/Title/Body scaled for tablet & phone
* Spacing scale: 4, 8, 12, 16, 24, 32

**Domain models (minimal now):**

* `Ticket { id, shortCode, qrToken, sig, type: single|multi|timepass|credit, quota, used, validFrom, validTo, lotNo, price, status }`
* `Package { id, name, price, type, quotaOrMinutes, bindDeviceIds? }`
* `Redemption { id, ticketId, deviceId, ts, result, reason? }`
* `Shift { id, user, openedAt, closedAt?, cashOpen, cashClose?, totals }`

**Components to implement:**

* `TicketCard` (QR preview + details)
* `PriceChip` (price + strikethrough for discount)
* `NumPad` (0–9, C, OK)
* `ScanFrame` overlay for camera view
* `AppDialogPIN` (PIN keypad modal with callback)

**Navigation map (go\_router):**

* `/pos`, `/pos/checkout`, `/pos/receipt/:id`
* `/gate/scan`, `/gate/result`
* `/kiosk`, `/kiosk/admin`
* `/reports/shifts`

**Mock flows:**

* Selling creates a mock `Ticket` with ULID & QR payload: `{ v:1, tid, t:qrToken, s:sig, lf:lotNo, tp:type }`
* Gate scanning parses QR, calls a mock validator that returns PASS/FAIL with remaining quota/time

**Deliverables:**

1. A fresh Flutter project with the folders above
2. `pubspec.yaml` with dependencies (go\_router, hooks\_riverpod or flutter\_bloc, qr\_flutter, mobile\_scanner, intl, flutter\_lints)
3. Full theming (Material 3) + dark theme default
4. Implement all screens with **beautiful, touch-friendly UI**, responsive for 6–10" screens
5. Reusable widgets with docs comments
6. Dummy data generators and fixtures
7. One end-to-end demo path: POS → Checkout → Receipt (QR) → Gate → PASS screen

**Coding style:**

* Clean architecture separation (domain/data/ui)
* Keep widgets small and composable
* Prefer const constructors, SizedBox for spacing, LayoutBuilder/MediaQuery for responsiveness
* Unit tests for model serialization and the mock validator

**Finally:**
Please output:

* the folder tree,
* the `pubspec.yaml`,
* the main `main.dart` with `GoRouter`,
* one example feature screen (POS Catalog),
* one reusable widget (`TicketCard`),
* one scanner screen (GateScanScreen with `mobile_scanner`).
  Use placeholder images/icons and mock data. No backend calls yet.

---

# “UI-first sprint” prompt (shorter, for each screen)

**Title:** POS Catalog screen (UI-only, Flutter/Compose-style)

**Goal:**
Design a tablet-friendly POS catalog screen that shows 2–4 columns of package cards, a sticky checkout panel at the right (or bottom on phones), and a floating scan button (for quick redeem). No business logic; just fake data and callbacks.

**Details:**

* Cards: name, price, type badge, quick “+” add button
* Sticky checkout: list of cart items, qty +/−, subtotal, discount field, big “Checkout” button
* Theme: use tokens above. Minimum 48dp touch targets, readable typography
* Responsiveness: on width ≥ 900dp: 3–4 columns + right panel; on small screens collapse to bottom sheet

**Output:**

* `PosCatalogScreen` widget, `CartPanel` widget, a `PackageCard` widget, and mock data provider

---

# Template to spec any component (you can reuse)

**Component Spec Template (English):**

* **Name:** TicketCard
* **Purpose:** Show a ticket snapshot with QR preview, short code, validity window, and type badge
* **Inputs:** `Ticket ticket`, `VoidCallback? onTap`, `bool dense = false`
* **Layout:** Card with leading QR (qr\_flutter), title (shortCode), subtitle (type + validity), trailing chevron
* **States:** default, disabled (expired/cancelled)
* **Accessibility:** min 48dp, semantic labels for screen readers
* **Test:** golden test for dense/regular, snapshot with long codes

---

# pubspec.yaml (core deps you can start with)

```yaml
name: playpark
description: UI-first playground ticketing app (Flutter)
environment:
  sdk: ">=3.4.0 <4.0.0"

dependencies:
  flutter:
    sdk: flutter
  flutter_hooks: ^0.20.5
  hooks_riverpod: ^2.5.1
  go_router: ^14.2.0
  qr_flutter: ^4.1.0
  mobile_scanner: ^5.1.1
  intl: ^0.19.0

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^4.0.0
```

---

# Example snippets (drop-in)

**main.dart (router skeleton)**

```dart
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'features/pos/pos_catalog_screen.dart';
import 'features/gate/gate_scan_screen.dart';

void main() => runApp(const App());

class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) {
    final router = GoRouter(
      initialLocation: '/pos',
      routes: [
        GoRoute(path: '/pos', builder: (_, __) => const PosCatalogScreen()),
        GoRoute(path: '/gate/scan', builder: (_, __) => const GateScanScreen()),
      ],
    );

    final theme = ThemeData(
      colorSchemeSeed: const Color(0xFF356DF3),
      useMaterial3: true,
      brightness: Brightness.dark,
    );

    return MaterialApp.router(
      title: 'PlayPark',
      routerConfig: router,
      theme: theme,
    );
  }
}
```

**TicketCard.dart**

```dart
import 'package:flutter/material.dart';
import 'package:qr_flutter/qr_flutter.dart';

class TicketCard extends StatelessWidget {
  final String shortCode;
  final String qrPayload;
  final String subtitle;
  final bool disabled;
  final VoidCallback? onTap;

  const TicketCard({
    super.key,
    required this.shortCode,
    required this.qrPayload,
    required this.subtitle,
    this.disabled = false,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return InkWell(
      onTap: disabled ? null : onTap,
      child: Card(
        elevation: 0,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              QrImageView(data: qrPayload, size: 72),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(shortCode,
                        style: Theme.of(context).textTheme.titleLarge),
                    const SizedBox(height: 6),
                    Text(subtitle,
                        style: Theme.of(context).textTheme.bodyMedium
                          ?.copyWith(color: cs.onSurfaceVariant)),
                  ],
                ),
              ),
              Icon(Icons.chevron_right,
                  color: disabled ? cs.onSurfaceVariant : cs.onSurface),
            ],
          ),
        ),
      ),
    );
  }
}
```

**GateScanScreen.dart (camera + scan callback)**

```dart
import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';

class GateScanScreen extends StatefulWidget {
  const GateScanScreen({super.key});

  @override
  State<GateScanScreen> createState() => _GateScanScreenState();
}

class _GateScanScreenState extends State<GateScanScreen> {
  bool _handled = false;

  void _onDetect(BarcodeCapture cap) {
    if (_handled) return;
    final code = cap.barcodes.firstOrNull?.rawValue;
    if (code == null) return;
    setState(() => _handled = true);

    // TODO: call mock validator → show PASS/FAIL
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Scanned'),
        content: Text(code),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('OK'),
          )
        ],
      ),
    ).then((_) => setState(() => _handled = false));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Gate • Scan')),
      body: Stack(
        alignment: Alignment.center,
        children: [
          MobileScanner(onDetect: _onDetect),
          IgnorePointer(
            child: Container(
              decoration: BoxDecoration(
                border: Border.all(width: 3),
                borderRadius: BorderRadius.circular(16),
              ),
              width: 260, height: 260,
            ),
          ),
        ],
      ),
    );
  }
}

extension _FirstOrNull<T> on List<T> {
  T? get firstOrNull => isEmpty ? null : first;
}
```

---

# How to work UI-first in VS Code (quick checklist)

1. `flutter create playpark` → add deps in pubspec → `flutter pub get`
2. Set **design tokens & theme** first (colors, typography, spacing)
3. Build **reusable widgets** (TicketCard, NumPad, AppDialogPIN)
4. Layout **POS Catalog** → **Checkout** → **Receipt** → **Gate Scan**
5. Add **dummy repos** (fake JSON) and **navigation** between screens
6. Only after UI is stable, add simple validators/mock printing stubs

