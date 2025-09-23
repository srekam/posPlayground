import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../../core/theme/tokens.dart';
import '../../domain/models/cart.dart';
import '../../domain/models/payment.dart';
import '../pos/providers/cart_provider.dart';
import 'providers/payment_provider.dart';
import '../receipt/providers/ticket_provider.dart';
import '../receipt/receipt_screen.dart';

class CheckoutScreen extends HookConsumerWidget {
  const CheckoutScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final cart = ref.watch(cartProvider);
    final paymentState = ref.watch(paymentProvider);
    final paymentNotifier = ref.read(paymentProvider.notifier);
    
    return Scaffold(
      appBar: AppBar(title: const Text('Checkout')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(Spacing.md),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Order Summary
            Card(
              child: Padding(
                padding: const EdgeInsets.all(Spacing.md),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Order Summary', style: Theme.of(context).textTheme.titleLarge),
                    const SizedBox(height: Spacing.sm),
                    ...cart.lines.map((line) => Padding(
                      padding: const EdgeInsets.symmetric(vertical: Spacing.xs),
                      child: Row(
                        children: [
                          Expanded(child: Text('${line.package.name} x${line.qty}')),
                          Text(line.lineTotalText),
                        ],
                      ),
                    )),
                    const Divider(),
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
                        const Expanded(
                          child: Text('Total', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
                        ),
                        Text(
                          cart.grandTotalText,
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: Spacing.md),
            
            // Payment Method Selection
            Card(
              child: Padding(
                padding: const EdgeInsets.all(Spacing.md),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Payment Method', style: Theme.of(context).textTheme.titleLarge),
                    const SizedBox(height: Spacing.sm),
                    _PaymentMethodSelector(
                      selectedMethod: paymentState.selectedMethod,
                      onMethodSelected: paymentNotifier.selectPaymentMethod,
                    ),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: Spacing.md),
            
            // Cash Payment Fields (if cash selected)
            if (paymentState.selectedMethod == PaymentMethod.cash)
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(Spacing.md),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Cash Payment', style: Theme.of(context).textTheme.titleLarge),
                      const SizedBox(height: Spacing.sm),
                      _CashPaymentFields(
                        grandTotal: cart.grandTotal,
                        tenderedAmount: paymentState.tenderedAmount,
                        onTenderedChanged: paymentNotifier.setTenderedAmount,
                      ),
                    ],
                  ),
                ),
              ),
            
            const SizedBox(height: Spacing.xl),
            
            // Complete Payment Button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: paymentNotifier.canCompletePayment(cart.grandTotal)
                    ? () => _completePayment(context, ref, cart)
                    : null,
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: Spacing.md),
                ),
                child: Text(
                  'Complete Payment (${cart.grandTotalText})',
                  style: const TextStyle(fontSize: 18),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _completePayment(BuildContext context, WidgetRef ref, Cart cart) async {
    final paymentNotifier = ref.read(paymentProvider.notifier);
    final cartNotifier = ref.read(cartProvider.notifier);
    final ticketGenerator = ref.read(ticketGeneratorProvider);
    
    try {
      // Show loading
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (_) => const Center(child: CircularProgressIndicator()),
      );
      
      // Simulate payment processing
      await Future.delayed(const Duration(seconds: 2));
      
      // Process payment
      final payment = await paymentNotifier.processPayment(cart);
      
      // Generate tickets
      final tickets = ticketGenerator.generateTicketsFromCart(cart);
      
      // Clear cart
      cartNotifier.clearCart();
      
      // Close loading dialog
      Navigator.of(context).pop();
      
      // Navigate to receipt
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(
          builder: (_) => ReceiptScreen(payment: payment, tickets: tickets),
        ),
      );
    } catch (e) {
      // Close loading dialog
      Navigator.of(context).pop();
      
      // Show error
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Payment failed: $e')),
      );
    }
  }
}

class _PaymentMethodSelector extends StatelessWidget {
  final PaymentMethod selectedMethod;
  final Function(PaymentMethod) onMethodSelected;

  const _PaymentMethodSelector({
    required this.selectedMethod,
    required this.onMethodSelected,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: PaymentMethod.values.map((method) {
        return RadioListTile<PaymentMethod>(
          title: Text(_getMethodName(method)),
          subtitle: Text(_getMethodDescription(method)),
          value: method,
          groupValue: selectedMethod,
          onChanged: (value) => onMethodSelected(value!),
        );
      }).toList(),
    );
  }

  String _getMethodName(PaymentMethod method) {
    switch (method) {
      case PaymentMethod.cash:
        return 'Cash';
      case PaymentMethod.qrCode:
        return 'QR Code';
      case PaymentMethod.card:
        return 'Bank Card';
    }
  }

  String _getMethodDescription(PaymentMethod method) {
    switch (method) {
      case PaymentMethod.cash:
        return 'Pay with cash';
      case PaymentMethod.qrCode:
        return 'Scan QR code to pay';
      case PaymentMethod.card:
        return 'Insert or tap card';
    }
  }
}

class _CashPaymentFields extends StatelessWidget {
  final double grandTotal;
  final double tenderedAmount;
  final Function(double) onTenderedChanged;

  const _CashPaymentFields({
    required this.grandTotal,
    required this.tenderedAmount,
    required this.onTenderedChanged,
  });

  @override
  Widget build(BuildContext context) {
    final change = tenderedAmount - grandTotal;
    
    return Column(
      children: [
        TextField(
          decoration: InputDecoration(
            labelText: 'Amount Tendered',
            prefixText: '฿',
            border: const OutlineInputBorder(),
          ),
          keyboardType: TextInputType.number,
          onChanged: (value) {
            final amount = double.tryParse(value) ?? 0;
            onTenderedChanged(amount);
          },
        ),
        const SizedBox(height: Spacing.sm),
        if (tenderedAmount > 0) ...[
          Row(
            children: [
              const Expanded(child: Text('Grand Total:')),
              Text('฿${grandTotal.toStringAsFixed(0)}'),
            ],
          ),
          const SizedBox(height: Spacing.xs),
          Row(
            children: [
              const Expanded(child: Text('Amount Tendered:')),
              Text('฿${tenderedAmount.toStringAsFixed(0)}'),
            ],
          ),
          const SizedBox(height: Spacing.xs),
          Row(
            children: [
              const Expanded(
                child: Text('Change:', style: TextStyle(fontWeight: FontWeight.bold)),
              ),
              Text(
                '฿${change.toStringAsFixed(0)}',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: change >= 0 ? Colors.green : Colors.red,
                ),
              ),
            ],
          ),
        ],
      ],
    );
  }
}
