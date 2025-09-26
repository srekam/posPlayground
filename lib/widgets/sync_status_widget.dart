import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

import '../features/core/providers/sync_provider.dart';
import '../data/services/sync_service.dart';

class SyncStatusWidget extends HookConsumerWidget {
  const SyncStatusWidget({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final syncStatusAsync = ref.watch(syncStatusProvider);
    final syncNotifier = ref.read(syncProvider.notifier);

    return syncStatusAsync.when(
      data: (syncStatus) => _buildSyncStatus(context, syncStatus, syncNotifier),
      loading: () => const _SyncStatusIndicator(
        icon: Icons.sync,
        color: Colors.blue,
        text: 'Checking sync status...',
      ),
      error: (error, stack) => _SyncStatusIndicator(
        icon: Icons.error,
        color: Colors.red,
        text: 'Sync error: $error',
      ),
    );
  }

  Widget _buildSyncStatus(
      BuildContext context, SyncStatus syncStatus, SyncNotifier syncNotifier) {
    if (!syncStatus.hasUnsyncedData) {
      return const _SyncStatusIndicator(
        icon: Icons.cloud_done,
        color: Colors.green,
        text: 'All synced',
      );
    }

    return InkWell(
      onTap: () => _showSyncDialog(context, syncStatus, syncNotifier),
      child: _SyncStatusIndicator(
        icon: Icons.sync_problem,
        color: Colors.orange,
        text: '${syncStatus.totalUnsynced} items need sync',
      ),
    );
  }

  void _showSyncDialog(
      BuildContext context, SyncStatus syncStatus, SyncNotifier syncNotifier) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Sync Status'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (syncStatus.queuedEvents > 0)
              _SyncStatusItem(
                icon: Icons.queue,
                text: '${syncStatus.queuedEvents} events queued',
              ),
            if (syncStatus.failedEvents > 0)
              _SyncStatusItem(
                icon: Icons.error,
                text: '${syncStatus.failedEvents} events failed',
                color: Colors.red,
              ),
            if (syncStatus.unsyncedPackages > 0)
              _SyncStatusItem(
                icon: Icons.inventory,
                text: '${syncStatus.unsyncedPackages} packages unsynced',
              ),
            if (syncStatus.unsyncedTickets > 0)
              _SyncStatusItem(
                icon: Icons.confirmation_number,
                text: '${syncStatus.unsyncedTickets} tickets unsynced',
              ),
            if (syncStatus.unsyncedSales > 0)
              _SyncStatusItem(
                icon: Icons.receipt,
                text: '${syncStatus.unsyncedSales} sales unsynced',
              ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Close'),
          ),
          if (syncStatus.failedEvents > 0)
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
                syncNotifier.retryFailedEvents();
              },
              child: const Text('Retry Failed'),
            ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
              syncNotifier.fullSync();
            },
            child: const Text('Sync All'),
          ),
        ],
      ),
    );
  }
}

class _SyncStatusIndicator extends StatelessWidget {
  final IconData icon;
  final Color color;
  final String text;

  const _SyncStatusIndicator({
    required this.icon,
    required this.color,
    required this.text,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16, color: color),
          const SizedBox(width: 4),
          Text(
            text,
            style: TextStyle(
              color: color,
              fontSize: 12,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }
}

class _SyncStatusItem extends StatelessWidget {
  final IconData icon;
  final String text;
  final Color? color;

  const _SyncStatusItem({
    required this.icon,
    required this.text,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Icon(
            icon,
            size: 16,
            color: color ?? Theme.of(context).primaryColor,
          ),
          const SizedBox(width: 8),
          Text(text),
        ],
      ),
    );
  }
}

class SyncProgressWidget extends HookConsumerWidget {
  const SyncProgressWidget({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final syncState = ref.watch(syncProvider);

    if (!syncState.isLoading) {
      return const SizedBox.shrink();
    }

    return Container(
      padding: const EdgeInsets.all(16),
      margin: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(8),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const CircularProgressIndicator(),
          const SizedBox(height: 16),
          Text(
            syncState.message,
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.bodyMedium,
          ),
        ],
      ),
    );
  }
}
