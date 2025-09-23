import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../../core/theme/tokens.dart';
import '../../domain/models/package.dart';
import '../../domain/models/cart.dart';
import 'providers/package_provider.dart';
import 'providers/cart_provider.dart';
import '../checkout/checkout_screen.dart';
import '../reports/shift_screen.dart';

class PosCatalogScreen extends HookConsumerWidget {
  const PosCatalogScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final packagesAsync = ref.watch(packagesProvider);
    final cart = ref.watch(cartProvider);
    return Scaffold(
      appBar: AppBar(
        title: const Text('POS • Catalog'),
        actions: [
          IconButton(
            onPressed: () => Navigator.of(context).push(
              MaterialPageRoute(builder: (_) => const ShiftScreen()),
            ),
            icon: const Icon(Icons.business_center),
            tooltip: 'Shift Management',
          ),
        ],
      ),
      body: packagesAsync.when(
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
      floatingActionButton: FloatingActionButton.extended(
        onPressed: cart.isNotEmpty 
            ? () => Navigator.of(context).push(
                  MaterialPageRoute(builder: (_) => const CheckoutScreen()),
                )
            : null,
        icon: const Icon(Icons.shopping_cart_checkout),
        label: Text(cart.isNotEmpty ? 'Checkout (${cart.totalItems})' : 'Empty Cart'),
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
        padding: const EdgeInsets.all(Spacing.md),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: Spacing.xs, vertical: Spacing.xxs),
                  decoration: BoxDecoration(
                    color: cs.secondaryContainer,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(package.type, style: TextStyle(color: cs.onSecondaryContainer)),
                ),
                const Spacer(),
                if (qty > 0) ...[
                  IconButton(
                    onPressed: () => cartNotifier.updateLineQty(package.id, qty - 1),
                    icon: const Icon(Icons.remove_circle_outline),
                  ),
                  Text('$qty'),
                ],
                IconButton(
                  onPressed: () => cartNotifier.addPackage(package),
                  icon: const Icon(Icons.add_circle_outline),
                ),
              ],
            ),
            const Spacer(),
            Text(package.name, style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: Spacing.xs),
            Text(package.priceText, style: Theme.of(context).textTheme.headlineSmall),
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
}



