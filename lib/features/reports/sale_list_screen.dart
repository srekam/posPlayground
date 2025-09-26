import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../../core/theme/tokens.dart';
import '../../domain/models/payment.dart';
import '../../domain/models/ticket.dart';
import 'providers/sale_list_provider.dart';
import '../receipt/receipt_screen.dart';
import '../pos/pos_catalog_screen.dart';

class SaleListScreen extends HookConsumerWidget {
  const SaleListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final salesAsync = ref.watch(salesProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Sale List'),
        actions: [
          IconButton(
            onPressed: () => Navigator.of(context).pushReplacement(
              MaterialPageRoute(builder: (_) => const PosCatalogScreen()),
            ),
            icon: const Icon(Icons.home),
            tooltip: 'Back to POS',
          ),
        ],
      ),
      body: Column(
        children: [
          // Performance Dashboard
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(Spacing.md),
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.surfaceContainerHighest,
              borderRadius: const BorderRadius.only(
                bottomLeft: Radius.circular(16),
                bottomRight: Radius.circular(16),
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Shift Performance',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(height: Spacing.md),
                Row(
                  children: [
                    Expanded(
                      child: _PerformanceCard(
                        title: 'Total Sales',
                        value: '${salesAsync.length}',
                        subtitle: 'Transactions',
                        icon: Icons.receipt_long,
                        color: Colors.blue,
                      ),
                    ),
                    const SizedBox(width: Spacing.sm),
                    Expanded(
                      child: _PerformanceCard(
                        title: 'Revenue',
                        value:
                            '฿${_calculateTotalRevenue(salesAsync).toStringAsFixed(0)}',
                        subtitle: 'This Shift',
                        icon: Icons.attach_money,
                        color: Colors.green,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: Spacing.sm),
                Row(
                  children: [
                    Expanded(
                      child: _PerformanceCard(
                        title: 'Customers',
                        value: '${_calculateUniqueCustomers(salesAsync)}',
                        subtitle: 'Unique',
                        icon: Icons.people,
                        color: Colors.orange,
                      ),
                    ),
                    const SizedBox(width: Spacing.sm),
                    Expanded(
                      child: _PerformanceCard(
                        title: 'Avg Sale',
                        value:
                            '฿${_calculateAverageSale(salesAsync).toStringAsFixed(0)}',
                        subtitle: 'Per Transaction',
                        icon: Icons.trending_up,
                        color: Colors.purple,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),

          // Sale List
          Expanded(
            child: salesAsync.isEmpty
                ? const Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.receipt_long_outlined, size: 64),
                        SizedBox(height: Spacing.md),
                        Text('No sales found for this shift'),
                        SizedBox(height: Spacing.sm),
                        Text('Complete a transaction to see it here'),
                      ],
                    ),
                  )
                : ListView.builder(
                    padding: const EdgeInsets.all(Spacing.md),
                    itemCount: salesAsync.length,
                    itemBuilder: (context, index) {
                      final sale = salesAsync[index];
                      return _SaleCard(sale: sale);
                    },
                  ),
          ),
        ],
      ),
    );
  }

  // Calculation methods
  double _calculateTotalRevenue(List<SaleRecord> sales) {
    return sales.fold(0.0, (sum, sale) => sum + sale.payment.amount);
  }

  int _calculateUniqueCustomers(List<SaleRecord> sales) {
    // For now, we'll assume each sale is a unique customer
    // In a real app, you'd track customer IDs
    return sales.length;
  }

  double _calculateAverageSale(List<SaleRecord> sales) {
    if (sales.isEmpty) return 0.0;
    return _calculateTotalRevenue(sales) / sales.length;
  }
}

class _SaleCard extends StatelessWidget {
  final SaleRecord sale;

  const _SaleCard({required this.sale});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: Spacing.md),
      child: Padding(
        padding: const EdgeInsets.all(Spacing.md),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Receipt #${sale.payment.reference ?? sale.payment.id}',
                        style: Theme.of(context).textTheme.titleMedium,
                      ),
                      const SizedBox(height: Spacing.xs),
                      Text(
                        _formatDateTime(sale.payment.processedAt),
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ],
                  ),
                ),
                Text(
                  sale.payment.amountText,
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: Theme.of(context).colorScheme.primary,
                      ),
                ),
              ],
            ),
            const SizedBox(height: Spacing.sm),
            Row(
              children: [
                Expanded(
                  child: Text(
                    '${sale.payment.methodName} • ${sale.tickets.length} ticket(s)',
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                ),
                const SizedBox(width: Spacing.sm),
                OutlinedButton.icon(
                  onPressed: () => _showRefundDialog(context, sale),
                  icon: const Icon(Icons.undo, size: 16),
                  label: const Text('Refund'),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: Colors.red,
                    side: const BorderSide(color: Colors.red),
                  ),
                ),
                const SizedBox(width: Spacing.xs),
                OutlinedButton.icon(
                  onPressed: () => _viewReceipt(context, sale),
                  icon: const Icon(Icons.receipt, size: 16),
                  label: const Text('View'),
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

  void _viewReceipt(BuildContext context, SaleRecord sale) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => ReceiptScreen(
          payment: sale.payment,
          tickets: sale.tickets,
        ),
      ),
    );
  }

  void _showRefundDialog(BuildContext context, SaleRecord sale) {
    showDialog(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Process Refund'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
                'Refund Receipt #${sale.payment.reference ?? sale.payment.id}'),
            const SizedBox(height: Spacing.xs),
            Text('Amount: ${sale.payment.amountText}'),
            const SizedBox(height: Spacing.xs),
            Text('Tickets: ${sale.tickets.length}'),
            const SizedBox(height: Spacing.md),
            const Text('Manager approval required:'),
            const SizedBox(height: Spacing.sm),
            const TextField(
              decoration: InputDecoration(
                labelText: 'Manager PIN',
                hintText: 'Enter 4-digit PIN',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.number,
              obscureText: true,
              maxLength: 4,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(dialogContext).pop(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(dialogContext).pop();
              _processRefund(context, sale);
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
              foregroundColor: Colors.white,
            ),
            child: const Text('Process Refund'),
          ),
        ],
      ),
    );
  }

  void _processRefund(BuildContext context, SaleRecord sale) {
    // Show loading dialog
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const AlertDialog(
        content: Row(
          children: [
            CircularProgressIndicator(),
            SizedBox(width: Spacing.md),
            Text('Processing refund...'),
          ],
        ),
      ),
    );

    // Simulate refund processing
    Future.delayed(const Duration(seconds: 2), () {
      Navigator.of(context).pop(); // Close loading dialog

      // Show success message
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
              'Refund processed for Receipt #${sale.payment.reference ?? sale.payment.id}'),
          backgroundColor: Colors.green,
          duration: const Duration(seconds: 3),
        ),
      );

      // Refresh the sale list
      // Note: In a real app, you'd invalidate the provider here
    });
  }
}

class _PerformanceCard extends StatelessWidget {
  final String title;
  final String value;
  final String subtitle;
  final IconData icon;
  final Color color;

  const _PerformanceCard({
    required this.title,
    required this.value,
    required this.subtitle,
    required this.icon,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(Spacing.md),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  icon,
                  color: color,
                  size: 20,
                ),
                const SizedBox(width: Spacing.xs),
                Expanded(
                  child: Text(
                    title,
                    style: Theme.of(context).textTheme.bodySmall,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
            const SizedBox(height: Spacing.xs),
            Text(
              value,
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: color,
                  ),
            ),
            Text(
              subtitle,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
            ),
          ],
        ),
      ),
    );
  }
}

// Data model for sale records
class SaleRecord {
  final Payment payment;
  final List<Ticket> tickets;
  final DateTime createdAt;

  const SaleRecord({
    required this.payment,
    required this.tickets,
    required this.createdAt,
  });
}
