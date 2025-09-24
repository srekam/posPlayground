import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

import '../../core/services/connectivity_service.dart';
import '../../core/services/device_auth_service.dart';
import '../../core/providers/adaptive_provider.dart';
import '../../core/config/app_config.dart';

class BackendHealthScreen extends HookConsumerWidget {
  const BackendHealthScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final adaptiveState = ref.watch(adaptiveProvider);
    final connectionSummary = ref.watch(connectionSummaryProvider);
    final connectionStatus = ref.watch(connectionStatusProvider);
    final backendStatus = ref.watch(backendStatusProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Backend Health'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        actions: [
          IconButton(
            onPressed: () => _refreshHealth(context, ref),
            icon: const Icon(Icons.refresh),
            tooltip: 'Refresh Health Status',
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Overall Status Card
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(
                          _getStatusIcon(adaptiveState.mode.type),
                          color: _getStatusColor(adaptiveState.mode.type),
                          size: 32,
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Overall Status',
                                style: Theme.of(context).textTheme.titleLarge,
                              ),
                              Text(
                                adaptiveState.mode.message,
                                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                                  color: _getStatusColor(adaptiveState.mode.type),
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 16),

            // Connection Status
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Connection Status',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 8),
                    connectionStatus.when(
                      data: (status) => _buildStatusRow('Network', status.name, _getConnectionColor(status)),
                      loading: () => const _LoadingRow('Network'),
                      error: (error, _) => _buildStatusRow('Network', 'Error: $error', Colors.red),
                    ),
                    const SizedBox(height: 8),
                    backendStatus.when(
                      data: (status) => _buildStatusRow('Backend', status.name, _getBackendColor(status)),
                      loading: () => const _LoadingRow('Backend'),
                      error: (error, _) => _buildStatusRow('Backend', 'Error: $error', Colors.red),
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 16),

            // Configuration Info
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Configuration',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 8),
                    _buildConfigRow('Backend URL', AppConfig.backendUrl),
                    _buildConfigRow('Device ID', AppConfig.defaultDeviceId),
                    _buildConfigRow('Store ID', AppConfig.defaultStoreId),
                    _buildConfigRow('Tenant ID', AppConfig.defaultTenantId),
                    _buildConfigRow('Offline Mode', AppConfig.enableOfflineMode ? 'Enabled' : 'Disabled'),
                    _buildConfigRow('Health Check', AppConfig.enableBackendHealthCheck ? 'Enabled' : 'Disabled'),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 16),

            // Capabilities
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Current Capabilities',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 8),
                    ...adaptiveState.mode.capabilities.entries.map(
                      (entry) => _buildCapabilityRow(entry.key, entry.value),
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 16),

            // Actions
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Actions',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        Expanded(
                          child: ElevatedButton.icon(
                            onPressed: () => _testConnection(context, ref),
                            icon: const Icon(Icons.network_check),
                            label: const Text('Test Connection'),
                          ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: ElevatedButton.icon(
                            onPressed: () => _forceSync(context, ref),
                            icon: const Icon(Icons.sync),
                            label: const Text('Force Sync'),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    SizedBox(
                      width: double.infinity,
                      child: OutlinedButton.icon(
                        onPressed: () => _showDetailedInfo(context, connectionSummary),
                        icon: const Icon(Icons.info_outline),
                        label: const Text('Detailed Info'),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusRow(String label, String value, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Container(
            width: 12,
            height: 12,
            decoration: BoxDecoration(
              color: color,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 12),
          SizedBox(
            width: 80,
            child: Text(
              '$label:',
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
          ),
          Expanded(
            child: Text(
              value.toUpperCase(),
              style: TextStyle(
                color: color,
                fontWeight: FontWeight.w500,
                fontFamily: 'monospace',
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildConfigRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 100,
            child: Text(
              '$label:',
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(fontFamily: 'monospace'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCapabilityRow(String capability, dynamic enabled) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        children: [
          Icon(
            enabled ? Icons.check_circle : Icons.cancel,
            color: enabled ? Colors.green : Colors.red,
            size: 16,
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              capability.replaceAll('_', ' ').toUpperCase(),
              style: TextStyle(
                color: enabled ? Colors.green : Colors.red,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Color _getStatusColor(AdaptiveModeType type) {
    switch (type) {
      case AdaptiveModeType.online:
        return Colors.green;
      case AdaptiveModeType.offline:
        return Colors.orange;
      case AdaptiveModeType.degraded:
        return Colors.yellow.shade700;
      case AdaptiveModeType.unregistered:
      case AdaptiveModeType.unauthenticated:
        return Colors.red;
      case AdaptiveModeType.initializing:
        return Colors.blue;
    }
  }

  IconData _getStatusIcon(AdaptiveModeType type) {
    switch (type) {
      case AdaptiveModeType.online:
        return Icons.cloud_done;
      case AdaptiveModeType.offline:
        return Icons.cloud_off;
      case AdaptiveModeType.degraded:
        return Icons.warning;
      case AdaptiveModeType.unregistered:
        return Icons.device_unknown;
      case AdaptiveModeType.unauthenticated:
        return Icons.lock;
      case AdaptiveModeType.initializing:
        return Icons.hourglass_empty;
    }
  }

  Color _getConnectionColor(ConnectionStatus status) {
    switch (status) {
      case ConnectionStatus.connected:
        return Colors.green;
      case ConnectionStatus.disconnected:
        return Colors.red;
      case ConnectionStatus.unknown:
        return Colors.grey;
    }
  }

  Color _getBackendColor(BackendStatus status) {
    switch (status) {
      case BackendStatus.healthy:
        return Colors.green;
      case BackendStatus.unhealthy:
        return Colors.red;
      case BackendStatus.unknown:
        return Colors.grey;
      case BackendStatus.checking:
        return Colors.blue;
    }
  }

  void _refreshHealth(BuildContext context, WidgetRef ref) {
    final connectivityService = ref.read(connectivityServiceProvider);
    connectivityService.forceBackendHealthCheck();
    
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Refreshing health status...'),
        duration: Duration(seconds: 2),
      ),
    );
  }

  void _testConnection(BuildContext context, WidgetRef ref) async {
    final connectivityService = ref.read(connectivityServiceProvider);
    await connectivityService.forceBackendHealthCheck();
    
    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Connection test completed'),
          duration: Duration(seconds: 2),
        ),
      );
    }
  }

  void _forceSync(BuildContext context, WidgetRef ref) {
    // This would trigger a manual sync
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Sync initiated...'),
        duration: Duration(seconds: 2),
      ),
    );
  }

  void _showDetailedInfo(BuildContext context, Map<String, dynamic> summary) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Detailed Connection Info'),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: summary.entries.map(
              (entry) => Padding(
                padding: const EdgeInsets.symmetric(vertical: 4),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    SizedBox(
                      width: 120,
                      child: Text(
                        '${entry.key}:',
                        style: const TextStyle(fontWeight: FontWeight.w500),
                      ),
                    ),
                    Expanded(
                      child: Text(
                        entry.value.toString(),
                        style: const TextStyle(fontFamily: 'monospace'),
                      ),
                    ),
                  ],
                ),
              ),
            ).toList(),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }
}

class _LoadingRow extends StatelessWidget {
  final String label;

  const _LoadingRow(this.label);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          const SizedBox(
            width: 12,
            height: 12,
            child: CircularProgressIndicator(strokeWidth: 2),
          ),
          const SizedBox(width: 12),
          SizedBox(
            width: 80,
            child: Text(
              '$label:',
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
          ),
          const Expanded(
            child: Text('Checking...'),
          ),
        ],
      ),
    );
  }
}
