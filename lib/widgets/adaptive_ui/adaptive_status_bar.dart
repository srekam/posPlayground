import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

import '../../core/providers/adaptive_provider.dart';

class AdaptiveStatusBar extends HookConsumerWidget {
  final bool showDetailedInfo;
  final VoidCallback? onTap;

  const AdaptiveStatusBar({
    super.key,
    this.showDetailedInfo = false,
    this.onTap,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final adaptiveState = ref.watch(adaptiveProvider);
    final connectionSummary = ref.watch(connectionSummaryProvider);

    return InkWell(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: _getBackgroundColor(adaptiveState.mode.type),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: _getBorderColor(adaptiveState.mode.type),
            width: 1,
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              _getIcon(adaptiveState.mode.type),
              size: 16,
              color: _getIconColor(adaptiveState.mode.type),
            ),
            const SizedBox(width: 8),
            Text(
              adaptiveState.mode.message,
              style: TextStyle(
                color: _getTextColor(adaptiveState.mode.type),
                fontSize: 12,
                fontWeight: FontWeight.w500,
              ),
            ),
            if (showDetailedInfo) ...[
              const SizedBox(width: 8),
              Text(
                '• ${connectionSummary['connection_status']} • ${connectionSummary['backend_status']}',
                style: TextStyle(
                  color: _getTextColor(adaptiveState.mode.type).withOpacity(0.7),
                  fontSize: 10,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Color _getBackgroundColor(AdaptiveModeType type) {
    switch (type) {
      case AdaptiveModeType.online:
        return Colors.green.withOpacity(0.1);
      case AdaptiveModeType.offline:
        return Colors.orange.withOpacity(0.1);
      case AdaptiveModeType.degraded:
        return Colors.yellow.withOpacity(0.1);
      case AdaptiveModeType.unregistered:
      case AdaptiveModeType.unauthenticated:
        return Colors.red.withOpacity(0.1);
      case AdaptiveModeType.initializing:
        return Colors.blue.withOpacity(0.1);
    }
  }

  Color _getBorderColor(AdaptiveModeType type) {
    switch (type) {
      case AdaptiveModeType.online:
        return Colors.green.withOpacity(0.3);
      case AdaptiveModeType.offline:
        return Colors.orange.withOpacity(0.3);
      case AdaptiveModeType.degraded:
        return Colors.yellow.withOpacity(0.3);
      case AdaptiveModeType.unregistered:
      case AdaptiveModeType.unauthenticated:
        return Colors.red.withOpacity(0.3);
      case AdaptiveModeType.initializing:
        return Colors.blue.withOpacity(0.3);
    }
  }

  Color _getIconColor(AdaptiveModeType type) {
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

  Color _getTextColor(AdaptiveModeType type) {
    switch (type) {
      case AdaptiveModeType.online:
        return Colors.green.shade700;
      case AdaptiveModeType.offline:
        return Colors.orange.shade700;
      case AdaptiveModeType.degraded:
        return Colors.yellow.shade800;
      case AdaptiveModeType.unregistered:
      case AdaptiveModeType.unauthenticated:
        return Colors.red.shade700;
      case AdaptiveModeType.initializing:
        return Colors.blue.shade700;
    }
  }

  IconData _getIcon(AdaptiveModeType type) {
    switch (type) {
      case AdaptiveModeType.online:
        return Icons.cloud_done;
      case AdaptiveModeType.offline:
        return Icons.cloud_off;
      case AdaptiveModeType.degraded:
        return Icons.cloud_sync;
      case AdaptiveModeType.unregistered:
        return Icons.device_unknown;
      case AdaptiveModeType.unauthenticated:
        return Icons.lock;
      case AdaptiveModeType.initializing:
        return Icons.hourglass_empty;
    }
  }
}

class AdaptiveModeBanner extends HookConsumerWidget {
  final Widget child;
  final bool showBanner;

  const AdaptiveModeBanner({
    super.key,
    required this.child,
    this.showBanner = true,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final adaptiveState = ref.watch(adaptiveProvider);

    if (!showBanner || adaptiveState.mode.type == AdaptiveModeType.online) {
      return child;
    }

    return Column(
      children: [
        Container(
          width: double.infinity,
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          color: _getBannerColor(adaptiveState.mode.type),
          child: Row(
            children: [
              Icon(
                _getBannerIcon(adaptiveState.mode.type),
                color: Colors.white,
                size: 20,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  _getBannerMessage(adaptiveState),
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
              if (adaptiveState.mode.canRetryConnection)
                TextButton(
                  onPressed: () => _handleRetry(context, ref),
                  child: const Text(
                    'Retry',
                    style: TextStyle(color: Colors.white),
                  ),
                ),
            ],
          ),
        ),
        child,
      ],
    );
  }

  Color _getBannerColor(AdaptiveModeType type) {
    switch (type) {
      case AdaptiveModeType.offline:
        return Colors.orange;
      case AdaptiveModeType.degraded:
        return Colors.yellow.shade700;
      case AdaptiveModeType.unregistered:
      case AdaptiveModeType.unauthenticated:
        return Colors.red;
      case AdaptiveModeType.initializing:
        return Colors.blue;
      case AdaptiveModeType.online:
        return Colors.green;
    }
  }

  IconData _getBannerIcon(AdaptiveModeType type) {
    switch (type) {
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
      case AdaptiveModeType.online:
        return Icons.cloud_done;
    }
  }


  String _getBannerMessage(AdaptiveState state) {
    switch (state.mode.type) {
      case AdaptiveModeType.offline:
        return 'Offline Mode - Limited functionality';
      case AdaptiveModeType.degraded:
        return 'Limited Connectivity - Some features unavailable';
      case AdaptiveModeType.unregistered:
        return 'Device Not Registered - Please register your device';
      case AdaptiveModeType.unauthenticated:
        return 'Authentication Required - Please login';
      case AdaptiveModeType.initializing:
        return 'Initializing connection...';
      case AdaptiveModeType.online:
        return 'Connected';
    }
  }

  void _handleRetry(BuildContext context, WidgetRef ref) {
    final connectivityService = ref.read(connectivityServiceProvider);
    connectivityService.forceBackendHealthCheck();
    
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Retrying connection...'),
        duration: Duration(seconds: 2),
      ),
    );
  }
}
