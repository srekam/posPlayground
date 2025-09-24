import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:qr_flutter/qr_flutter.dart';
import '../../core/theme/tokens.dart';
import '../../domain/models/payment.dart';
import '../../domain/models/ticket.dart';
import '../../domain/models/cart.dart';
import '../pos/providers/cart_provider.dart';
import '../pos/pos_catalog_screen.dart';
import 'providers/ticket_provider.dart';

class ReceiptScreen extends HookConsumerWidget {
  final Payment payment;
  final List<Ticket> tickets;
  
  const ReceiptScreen({
    super.key, 
    required this.payment,
    this.tickets = const [],
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Receipt'),
        actions: [
          IconButton(
            onPressed: () => _showReprintDialog(context),
            icon: const Icon(Icons.print),
            tooltip: 'Reprint',
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(Spacing.md),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Card(
              child: Padding(
                padding: const EdgeInsets.all(Spacing.md),
                child: Column(
                  children: [
                    Text(
                      'PlayPark',
                      style: Theme.of(context).textTheme.headlineMedium,
                    ),
                    const SizedBox(height: Spacing.xs),
                    Text(
                      'Indoor Playground',
                      style: Theme.of(context).textTheme.bodyLarge,
                    ),
                    const SizedBox(height: Spacing.xs),
                    Text(
                      'Receipt #${payment.reference ?? payment.id}',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                    Text(
                      _formatDateTime(payment.processedAt),
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: Spacing.md),
            
            // Payment Summary
            Card(
              child: Padding(
                padding: const EdgeInsets.all(Spacing.md),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Payment Summary', style: Theme.of(context).textTheme.titleLarge),
                    const SizedBox(height: Spacing.sm),
                    Row(
                      children: [
                        const Expanded(child: Text('Method:')),
                        Text(payment.methodName),
                      ],
                    ),
                    const SizedBox(height: Spacing.xs),
                    Row(
                      children: [
                        const Expanded(child: Text('Amount:')),
                        Text(payment.amountText, style: const TextStyle(fontWeight: FontWeight.bold)),
                      ],
                    ),
                    if (payment.tenderedAmount != null) ...[
                      const SizedBox(height: Spacing.xs),
                      Row(
                        children: [
                          const Expanded(child: Text('Tendered:')),
                          Text('฿${payment.tenderedAmount!.toStringAsFixed(0)}'),
                        ],
                      ),
                    ],
                    if (payment.changeAmount != null && payment.changeAmount! > 0) ...[
                      const SizedBox(height: Spacing.xs),
                      Row(
                        children: [
                          const Expanded(child: Text('Change:')),
                          Text(
                            payment.changeText,
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              color: Colors.green,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: Spacing.md),
            
            // Tickets
            if (tickets.isNotEmpty) ...[
              Text('Tickets Issued', style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: Spacing.sm),
              ...tickets.map((ticket) => _TicketCard(ticket: ticket)),
            ],
            
            const SizedBox(height: Spacing.xl),
            
            // Actions
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => _showReprintDialog(context),
                    icon: const Icon(Icons.print),
                    label: const Text('Reprint'),
                  ),
                ),
                const SizedBox(width: Spacing.md),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () => _navigateToHome(context, ref),
                    icon: const Icon(Icons.home),
                    label: const Text('New Sale'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  String _formatDateTime(DateTime dateTime) {
    return '${dateTime.day}/${dateTime.month}/${dateTime.year} ${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
  }

  void _showReprintDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Reprint Receipt'),
        content: const Text('This would trigger a reprint of the receipt.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Reprint requested')),
              );
            },
            child: const Text('Reprint'),
          ),
        ],
      ),
    );
  }

  void _navigateToHome(BuildContext context, WidgetRef ref) {
    // Show confirmation dialog before starting new sale
    showDialog(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('New Sale'),
        content: const Text('Do you need to make new sale?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(dialogContext).pop(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(dialogContext).pop(); // Close dialog first
              // Use Future.delayed to ensure dialog is fully closed before navigation
              Future.delayed(const Duration(milliseconds: 100), () {
                _confirmNewSale(context, ref);
              });
            },
            child: const Text('Yes, New Sale'),
          ),
        ],
      ),
    );
  }

  void _confirmNewSale(BuildContext context, WidgetRef ref) {
    // Clear the cart for a new sale
    ref.read(cartProvider.notifier).clearCart();
    
    // Navigate back to POS catalog using a simpler approach
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(builder: (_) => const PosCatalogScreen()),
    );
    
    // Show confirmation message
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('New sale started - Ready to add items'),
        duration: Duration(seconds: 2),
      ),
    );
  }
}

class _TicketCard extends StatelessWidget {
  final Ticket ticket;

  const _TicketCard({required this.ticket});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: Spacing.sm),
      child: Padding(
        padding: const EdgeInsets.all(Spacing.md),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                QrImageView(
                  data: ticket.qrPayload,
                  size: 80,
                ),
                const SizedBox(width: Spacing.md),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        ticket.shortCode,
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                      const SizedBox(height: Spacing.xs),
                      Text(
                        _getTicketTypeDisplay(ticket.type),
                        style: Theme.of(context).textTheme.bodyMedium,
                      ),
                      const SizedBox(height: Spacing.xs),
                      Text(
                        'Valid: ${_formatDateTime(ticket.validFrom)} - ${_formatDateTime(ticket.validTo)}',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  String _getTicketTypeDisplay(TicketType type) {
    switch (type) {
      case TicketType.single:
        return 'Single Entry';
      case TicketType.multi:
        return 'Multi Entry (${ticket.quotaOrMinutes} uses)';
      case TicketType.timepass:
        return 'Time Pass (${ticket.quotaOrMinutes} min)';
      case TicketType.credit:
        return 'Credit (${ticket.quotaOrMinutes} credits)';
    }
  }

  String _formatDateTime(DateTime dateTime) {
    return '${dateTime.day}/${dateTime.month} ${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
  }
}