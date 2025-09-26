import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'package:go_router/go_router.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

import 'features/pos/pos_catalog_screen.dart';
import 'features/gate/gate_scan_screen.dart';
import 'features/checkout/checkout_screen.dart';
import 'features/reports/shift_screen.dart';
import 'features/settings/settings_screen.dart';
import 'features/enrollment/device_enrollment_screen.dart';
import 'core/theme/app_theme.dart';
import 'features/settings/providers/settings_provider.dart';
import 'data/database/database_helper.dart';
import 'widgets/adaptive_ui/adaptive_mode_banner.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize database only on non-web platforms
  if (!kIsWeb) {
    try {
      await DatabaseHelper.database;
    } catch (e) {
      print('Database initialization failed: $e');
    }
  }

  runApp(const ProviderScope(child: App()));
}

class App extends ConsumerWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settings = ref.watch(settingsProvider);

    final router = GoRouter(
      initialLocation: '/enrollment',
      routes: [
        GoRoute(
            path: '/enrollment',
            builder: (_, __) => const DeviceEnrollmentScreen()),
        GoRoute(path: '/pos', builder: (_, __) => const PosCatalogScreen()),
        GoRoute(path: '/checkout', builder: (_, __) => const CheckoutScreen()),
        GoRoute(path: '/gate/scan', builder: (_, __) => const GateScanScreen()),
        GoRoute(
            path: '/reports/shifts', builder: (_, __) => const ShiftScreen()),
        GoRoute(path: '/settings', builder: (_, __) => const SettingsScreen()),
      ],
    );

    return MaterialApp.router(
      title: 'PlayPark',
      routerConfig: router,
      theme: AppTheme.light(colorScheme: settings.colorScheme),
      darkTheme: AppTheme.dark(colorScheme: settings.colorScheme),
      themeMode: settings.themeMode,
      builder: (context, child) {
        return AdaptiveModeBanner(
          showBanner: true,
          child: child!,
        );
      },
    );
  }
}
