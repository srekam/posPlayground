import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../../core/theme/tokens.dart';
import 'providers/shift_provider.dart';
import '../../domain/models/shift.dart';

class ShiftScreen extends HookConsumerWidget {
  const ShiftScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final shiftState = ref.watch(shiftProvider);
    final shiftNotifier = ref.read(shiftProvider.notifier);

    return Scaffold(
      appBar: AppBar(title: const Text('Shift Management')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(Spacing.md),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Current Shift Status
            if (shiftState.currentShift != null) ...[
              _CurrentShiftCard(shift: shiftState.currentShift!),
              const SizedBox(height: Spacing.md),
            ],

            // Shift Actions
            if (shiftState.currentShift == null) ...[
              _OpenShiftCard(onOpenShift: shiftNotifier.openShift),
              const SizedBox(height: Spacing.md),
            ] else ...[
              _CloseShiftCard(
                shift: shiftState.currentShift!,
                onCloseShift: shiftNotifier.closeShift,
              ),
              const SizedBox(height: Spacing.md),
            ],

            // Today's Summary
            _TodaySummaryCard(shiftState: shiftState),
            const SizedBox(height: Spacing.md),

            // Shift History
            Text('Recent Shifts', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: Spacing.sm),
            ...shiftState.shiftHistory.take(5).map((shift) => 
              _ShiftHistoryCard(shift: shift),
            ),
          ],
        ),
      ),
    );
  }
}

class _CurrentShiftCard extends StatelessWidget {
  final Shift shift;

  const _CurrentShiftCard({required this.shift});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(Spacing.md),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.access_time, color: Theme.of(context).colorScheme.primary),
                const SizedBox(width: Spacing.xs),
                Text('Active Shift', style: Theme.of(context).textTheme.titleLarge),
                const Spacer(),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: Spacing.xs, vertical: Spacing.xxs),
                  decoration: BoxDecoration(
                    color: Colors.green,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: const Text(
                    'ACTIVE',
                    style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ),
            const SizedBox(height: Spacing.sm),
            Row(
              children: [
                Expanded(
                  child: _InfoItem(
                    label: 'Duration',
                    value: shift.durationText,
                  ),
                ),
                Expanded(
                  child: _InfoItem(
                    label: 'Cash Open',
                    value: shift.cashOpenText,
                  ),
                ),
              ],
            ),
            const SizedBox(height: Spacing.xs),
            Row(
              children: [
                Expanded(
                  child: _InfoItem(
                    label: 'Sales',
                    value: shift.counters.totalSalesAmountText,
                  ),
                ),
                Expanded(
                  child: _InfoItem(
                    label: 'Transactions',
                    value: '${shift.counters.totalSales}',
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _OpenShiftCard extends StatelessWidget {
  final Function(String userId, double cashOpen) onOpenShift;

  const _OpenShiftCard({required this.onOpenShift});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(Spacing.md),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Open New Shift', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: Spacing.sm),
            const Text('No active shift. Open a new shift to start transactions.'),
            const SizedBox(height: Spacing.md),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: () => _showOpenShiftDialog(context),
                icon: const Icon(Icons.play_arrow),
                label: const Text('Open Shift'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showOpenShiftDialog(BuildContext context) {
    final cashController = TextEditingController(text: '1000');
    
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Open Shift'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: cashController,
              decoration: const InputDecoration(
                labelText: 'Cash Opening Amount',
                prefixText: '฿',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.number,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              final cashOpen = double.tryParse(cashController.text) ?? 1000.0;
              onOpenShift('user-001', cashOpen);
              Navigator.of(context).pop();
            },
            child: const Text('Open'),
          ),
        ],
      ),
    );
  }
}

class _CloseShiftCard extends StatelessWidget {
  final Shift shift;
  final Function(double cashClose) onCloseShift;

  const _CloseShiftCard({
    required this.shift,
    required this.onCloseShift,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(Spacing.md),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Close Shift', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: Spacing.sm),
            Text('Current shift has been active for ${shift.durationText}'),
            const SizedBox(height: Spacing.md),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: () => _showCloseShiftDialog(context),
                icon: const Icon(Icons.stop),
                label: const Text('Close Shift'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.red,
                  foregroundColor: Colors.white,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showCloseShiftDialog(BuildContext context) {
    final cashController = TextEditingController(text: '1000');
    
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Close Shift'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('Enter the cash count to close the shift.'),
            const SizedBox(height: Spacing.md),
            TextField(
              controller: cashController,
              decoration: const InputDecoration(
                labelText: 'Cash Count',
                prefixText: '฿',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.number,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              final cashClose = double.tryParse(cashController.text) ?? 1000.0;
              onCloseShift(cashClose);
              Navigator.of(context).pop();
            },
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }
}

class _TodaySummaryCard extends StatelessWidget {
  final ShiftState shiftState;

  const _TodaySummaryCard({required this.shiftState});

  @override
  Widget build(BuildContext context) {
    final todayShifts = shiftState.shiftHistory.where((shift) {
      final today = DateTime.now();
      return shift.openedAt.day == today.day &&
          shift.openedAt.month == today.month &&
          shift.openedAt.year == today.year;
    }).toList();

    final todaySales = todayShifts.fold(0.0, (sum, shift) => sum + shift.counters.totalSalesAmount);
    final todayTransactions = todayShifts.fold(0, (sum, shift) => sum + shift.counters.totalSales);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(Spacing.md),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Today\'s Summary', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: Spacing.sm),
            Row(
              children: [
                Expanded(
                  child: _InfoItem(
                    label: 'Total Sales',
                    value: '฿${todaySales.toStringAsFixed(0)}',
                  ),
                ),
                Expanded(
                  child: _InfoItem(
                    label: 'Transactions',
                    value: '$todayTransactions',
                  ),
                ),
              ],
            ),
            const SizedBox(height: Spacing.xs),
            Row(
              children: [
                Expanded(
                  child: _InfoItem(
                    label: 'Shifts Today',
                    value: '${todayShifts.length}',
                  ),
                ),
                Expanded(
                  child: _InfoItem(
                    label: 'Status',
                    value: shiftState.currentShift != null ? 'Active' : 'Closed',
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _ShiftHistoryCard extends StatelessWidget {
  final Shift shift;

  const _ShiftHistoryCard({required this.shift});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: Spacing.xs),
      child: Padding(
        padding: const EdgeInsets.all(Spacing.md),
        child: Row(
          children: [
            Icon(
              shift.isActive ? Icons.access_time : Icons.check_circle,
              color: shift.isActive ? Colors.green : Colors.grey,
            ),
            const SizedBox(width: Spacing.sm),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Shift ${shift.id.substring(shift.id.length - 6)}',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  Text(
                    '${shift.durationText} • ${shift.counters.totalSalesAmountText}',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              ),
            ),
            if (shift.variance != null)
              Text(
                shift.varianceText,
                style: TextStyle(
                  color: shift.variance! >= 0 ? Colors.green : Colors.red,
                  fontWeight: FontWeight.bold,
                ),
              ),
          ],
        ),
      ),
    );
  }
}

class _InfoItem extends StatelessWidget {
  final String label;
  final String value;

  const _InfoItem({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: Theme.of(context).textTheme.labelSmall,
        ),
        const SizedBox(height: Spacing.xxs),
        Text(
          value,
          style: Theme.of(context).textTheme.titleMedium,
        ),
      ],
    );
  }
}
