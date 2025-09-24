import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../../core/theme/tokens.dart';
import '../../domain/models/package.dart';
import '../../domain/models/cart.dart';
import 'providers/package_provider.dart';
import 'providers/cart_provider.dart';
import '../checkout/checkout_screen.dart';
import '../reports/shift_screen.dart';
import '../gate/gate_scan_screen.dart';
import '../reports/sale_list_screen.dart';
import '../settings/settings_screen.dart';
import '../settings/providers/settings_provider.dart';
import '../../widgets/sync_status_widget.dart';
import '../../widgets/adaptive_ui/adaptive_status_bar.dart';
import '../../widgets/adaptive_ui/adaptive_button.dart';
import '../../core/providers/adaptive_provider.dart';

class PosCatalogScreen extends HookConsumerWidget {
  const PosCatalogScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final packagesAsync = ref.watch(packagesProvider);
    final cart = ref.watch(cartProvider);
    final settings = ref.watch(settingsProvider);
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('POS • Catalog'),
        actions: [
          const AdaptiveStatusBar(),
          const SizedBox(width: 8),
          const SyncStatusWidget(),
          const SizedBox(width: 8),
          IconButton(
            onPressed: () => Navigator.of(context).push(
              MaterialPageRoute(builder: (_) => const SettingsScreen()),
            ),
            icon: const Icon(Icons.settings),
            tooltip: 'Settings',
          ),
          AdaptiveIconButton(
            icon: Icons.receipt_long,
            requiredCapability: 'can_access_reports',
            onPressed: () => Navigator.of(context).push(
              MaterialPageRoute(builder: (_) => const SaleListScreen()),
            ),
            tooltip: 'Sale List',
          ),
          AdaptiveIconButton(
            icon: Icons.qr_code_scanner,
            requiredCapability: 'can_redeem',
            onPressed: () => Navigator.of(context).push(
              MaterialPageRoute(builder: (_) => const GateScanScreen()),
            ),
            tooltip: 'Gate Scan',
          ),
          AdaptiveIconButton(
            icon: Icons.business_center,
            requiredCapability: 'can_access_reports',
            onPressed: () => Navigator.of(context).push(
              MaterialPageRoute(builder: (_) => const ShiftScreen()),
            ),
            tooltip: 'Shift Management',
          ),
        ],
      ),
      body: Stack(
        children: [
          // Background Image
          if (settings.showBackgroundImage)
            Positioned.fill(
              child: Image.asset(
                'background.png',
                fit: BoxFit.cover,
                opacity: const AlwaysStoppedAnimation(0.1),
              ),
            ),
          
          // Sync Progress Overlay
          const Positioned(
            top: 0,
            left: 0,
            right: 0,
            child: SyncProgressWidget(),
          ),
          
          // Main Content
          packagesAsync.when(
            data: (packages) => LayoutBuilder(
              builder: (context, constraints) {
                final wide = constraints.maxWidth >= 900;
                final grid = GridView.builder(
                  padding: const EdgeInsets.all(Spacing.md),
                  gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: wide ? 3 : 2,
                    mainAxisSpacing: Spacing.md,
                    crossAxisSpacing: Spacing.md,
                    childAspectRatio: 4 / 3,
                  ),
                  itemCount: packages.length,
                  itemBuilder: (_, i) {
                    final package = packages[i];
                    return _PackageCard(package: package);
                  },
                );

                if (!wide) return grid;

                return Row(
                  children: [
                    Expanded(child: grid),
                    const SizedBox(width: Spacing.md),
                    SizedBox(
                      width: 360,
                      child: _CartPanel(cart: cart),
                    ),
                  ],
                );
              },
            ),
            loading: () => const Center(child: CircularProgressIndicator()),
            error: (error, stack) => Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.error, size: 64),
                  const SizedBox(height: Spacing.md),
                  Text('Error loading packages: $error'),
                  const SizedBox(height: Spacing.md),
                  ElevatedButton(
                    onPressed: () => ref.invalidate(packagesProvider),
                    child: const Text('Retry'),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
      floatingActionButton: AdaptiveFloatingActionButton(
        requiredCapability: 'can_sell',
        onPressed: cart.isNotEmpty 
            ? () => Navigator.of(context).push(
                  MaterialPageRoute(builder: (_) => const CheckoutScreen()),
                )
            : null,
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.shopping_cart_checkout),
            const SizedBox(width: 8),
            Text(cart.isNotEmpty ? 'Checkout (${cart.totalItems})' : 'Empty Cart'),
          ],
        ),
      ),
    );
  }
}

class _PackageCard extends HookConsumerWidget {
  final Package package;
  const _PackageCard({required this.package});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final cs = Theme.of(context).colorScheme;
    final cartNotifier = ref.read(cartProvider.notifier);
    final cart = ref.watch(cartProvider);
    
    final existingLine = cartNotifier.getLineByPackageId(package.id);
    final qty = existingLine?.qty ?? 0;

    return Card(
      elevation: 0,
      child: Padding(
        padding: const EdgeInsets.all(Spacing.sm),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Row(
              children: [
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: Spacing.xs, vertical: 2),
                    decoration: BoxDecoration(
                      color: cs.secondaryContainer,
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Text(
                      package.type, 
                      style: TextStyle(
                        color: cs.onSecondaryContainer,
                        fontSize: 12,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ),
                const SizedBox(width: Spacing.xs),
                if (qty > 0) ...[
                  IconButton(
                    onPressed: () => cartNotifier.updateLineQty(package.id, qty - 1),
                    icon: const Icon(Icons.remove_circle_outline, size: 20),
                    constraints: const BoxConstraints(minWidth: 28, minHeight: 28),
                    padding: EdgeInsets.zero,
                  ),
                  Text('$qty', style: const TextStyle(fontSize: 14)),
                ],
                IconButton(
                  onPressed: () => cartNotifier.addPackage(package),
                  icon: const Icon(Icons.add_circle_outline, size: 20),
                  constraints: const BoxConstraints(minWidth: 28, minHeight: 28),
                  padding: EdgeInsets.zero,
                ),
              ],
            ),
            const SizedBox(height: Spacing.xs),
            Text(
              package.name, 
              style: Theme.of(context).textTheme.titleSmall,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 2),
            Text(
              package.priceText, 
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
      ),
    );
  }
}

class _CartPanel extends HookConsumerWidget {
  final Cart cart;
  const _CartPanel({required this.cart});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final cartNotifier = ref.read(cartProvider.notifier);
    
    return Card(
      elevation: 0,
      margin: const EdgeInsets.all(Spacing.md),
      child: Padding(
        padding: const EdgeInsets.all(Spacing.md),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Text('Cart', style: Theme.of(context).textTheme.titleLarge),
                const Spacer(),
                if (cart.isNotEmpty)
                  TextButton(
                    onPressed: () => cartNotifier.clearCart(),
                    child: const Text('Clear'),
                  ),
              ],
            ),
            const SizedBox(height: Spacing.sm),
            Expanded(
              child: cart.isEmpty
                  ? const Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.shopping_cart_outlined, size: 48),
                          SizedBox(height: Spacing.xs),
                          Text('Cart is empty'),
                        ],
                      ),
                    )
                  : ListView.separated(
                      itemCount: cart.lines.length,
                      separatorBuilder: (_, __) => const Divider(),
                      itemBuilder: (_, i) {
                        final line = cart.lines[i];
                        return Row(
                          children: [
                            Expanded(child: Text(line.package.name)),
                            IconButton(
                              onPressed: () => cartNotifier.updateLineQty(line.package.id, line.qty - 1),
                              icon: const Icon(Icons.remove_circle_outline),
                            ),
                            Text('${line.qty}'),
                            IconButton(
                              onPressed: () => cartNotifier.updateLineQty(line.package.id, line.qty + 1),
                              icon: const Icon(Icons.add_circle_outline),
                            ),
                            const SizedBox(width: Spacing.xs),
                            Text(line.lineTotalText),
                          ],
                        );
                      },
                    ),
            ),
            if (cart.isNotEmpty) ...[
              const SizedBox(height: Spacing.sm),
              
              // Discount Controls
              Card(
                color: Theme.of(context).colorScheme.surfaceVariant,
                child: Padding(
                  padding: const EdgeInsets.all(Spacing.sm),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Discounts', style: Theme.of(context).textTheme.titleSmall),
                      const SizedBox(height: Spacing.xs),
                      Row(
                        children: [
                          Expanded(
                            child: OutlinedButton.icon(
                              onPressed: () => _showDiscountDialog(context, ref),
                              icon: const Icon(Icons.percent, size: 16),
                              label: const Text('Apply %'),
                              style: OutlinedButton.styleFrom(
                                padding: const EdgeInsets.symmetric(horizontal: Spacing.xs),
                              ),
                            ),
                          ),
                          const SizedBox(width: Spacing.xs),
                          Expanded(
                            child: OutlinedButton.icon(
                              onPressed: () => _showCouponDialog(context, ref),
                              icon: const Icon(Icons.local_offer, size: 16),
                              label: const Text('Coupon'),
                              style: OutlinedButton.styleFrom(
                                padding: const EdgeInsets.symmetric(horizontal: Spacing.xs),
                              ),
                            ),
                          ),
                        ],
                      ),
                      if (cart.cartLevelDiscount > 0) ...[
                        const SizedBox(height: Spacing.xs),
                        Row(
                          children: [
                            const Expanded(child: Text('Applied Discount')),
                            Text('-${cart.cartLevelDiscountText}'),
                            const SizedBox(width: Spacing.xs),
                            IconButton(
                              onPressed: () => cartNotifier.applyCartLevelDiscount(),
                              icon: const Icon(Icons.close, size: 16),
                              constraints: const BoxConstraints(minWidth: 24, minHeight: 24),
                            ),
                          ],
                        ),
                      ],
                    ],
                  ),
                ),
              ),
              
              const SizedBox(height: Spacing.sm),
              Row(
                children: [
                  const Expanded(child: Text('Subtotal')),
                  Text(cart.subtotalText),
                ],
              ),
              if (cart.cartLevelDiscount > 0) ...[
                const SizedBox(height: Spacing.xs),
                Row(
                  children: [
                    const Expanded(child: Text('Discount')),
                    Text('-${cart.cartLevelDiscountText}'),
                  ],
                ),
              ],
              const SizedBox(height: Spacing.xs),
              Row(
                children: [
                  const Expanded(child: Text('Total', style: TextStyle(fontWeight: FontWeight.bold))),
                  Text(cart.grandTotalText, style: const TextStyle(fontWeight: FontWeight.bold)),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }

  void _showDiscountDialog(BuildContext context, WidgetRef ref) {
    final cartNotifier = ref.read(cartProvider.notifier);
    final cart = ref.read(cartProvider);
    
    showDialog(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Apply Discount'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('Current Subtotal: ${cart.subtotalText}'),
            const SizedBox(height: Spacing.md),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: () {
                      Navigator.of(dialogContext).pop();
                      cartNotifier.applyCartLevelDiscount(percent: 10);
                    },
                    child: const Text('10%'),
                  ),
                ),
                const SizedBox(width: Spacing.sm),
                Expanded(
                  child: OutlinedButton(
                    onPressed: () {
                      Navigator.of(dialogContext).pop();
                      cartNotifier.applyCartLevelDiscount(percent: 15);
                    },
                    child: const Text('15%'),
                  ),
                ),
                const SizedBox(width: Spacing.sm),
                Expanded(
                  child: OutlinedButton(
                    onPressed: () {
                      Navigator.of(dialogContext).pop();
                      cartNotifier.applyCartLevelDiscount(percent: 20);
                    },
                    child: const Text('20%'),
                  ),
                ),
              ],
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(dialogContext).pop(),
            child: const Text('Cancel'),
          ),
        ],
      ),
    );
  }

  void _showCouponDialog(BuildContext context, WidgetRef ref) {
    final cartNotifier = ref.read(cartProvider.notifier);
    final cart = ref.read(cartProvider);
    
    showDialog(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Apply Coupon'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('Current Subtotal: ${cart.subtotalText}'),
            const SizedBox(height: Spacing.md),
            const Text('Sample Coupons:'),
            const SizedBox(height: Spacing.sm),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: () {
                      Navigator.of(dialogContext).pop();
                      cartNotifier.setCouponCode('SAVE50');
                      cartNotifier.applyCartLevelDiscount(amount: 50);
                    },
                    child: const Text('SAVE50\n-฿50'),
                  ),
                ),
                const SizedBox(width: Spacing.sm),
                Expanded(
                  child: OutlinedButton(
                    onPressed: () {
                      Navigator.of(dialogContext).pop();
                      cartNotifier.setCouponCode('WELCOME');
                      cartNotifier.applyCartLevelDiscount(percent: 25);
                    },
                    child: const Text('WELCOME\n-25%'),
                  ),
                ),
              ],
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(dialogContext).pop(),
            child: const Text('Cancel'),
          ),
        ],
      ),
    );
  }
}



