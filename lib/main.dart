import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

import 'features/pos/pos_catalog_screen.dart';
import 'features/gate/gate_scan_screen.dart';
import 'features/checkout/checkout_screen.dart';
import 'features/receipt/receipt_screen.dart';
import 'features/reports/shift_screen.dart';
import 'core/theme/app_theme.dart';

void main() => runApp(const ProviderScope(child: App()));

class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) {
            final router = GoRouter(
              initialLocation: '/pos',
              routes: [
                GoRoute(path: '/pos', builder: (_, __) => const PosCatalogScreen()),
                GoRoute(path: '/checkout', builder: (_, __) => const CheckoutScreen()),
                GoRoute(path: '/gate/scan', builder: (_, __) => const GateScanScreen()),
                GoRoute(path: '/reports/shifts', builder: (_, __) => const ShiftScreen()),
              ],
            );

    return MaterialApp.router(
      title: 'PlayPark',
      routerConfig: router,
      theme: AppTheme.dark(),
    );
  }
}


