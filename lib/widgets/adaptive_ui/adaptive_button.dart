import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

import '../../core/providers/adaptive_provider.dart';

class AdaptiveButton extends HookConsumerWidget {
  final Widget child;
  final VoidCallback? onPressed;
  final String? requiredCapability;
  final String? tooltip;
  final ButtonStyle? style;
  final bool showOfflineIndicator;

  const AdaptiveButton({
    super.key,
    required this.child,
    this.onPressed,
    this.requiredCapability,
    this.tooltip,
    this.style,
    this.showOfflineIndicator = true,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final adaptiveMode = ref.watch(adaptiveProvider);
    final canExecute = _canExecute(adaptiveMode);

    return Tooltip(
      message: tooltip ?? _getTooltipMessage(adaptiveMode),
      child: Opacity(
        opacity: canExecute ? 1.0 : 0.6,
        child: ElevatedButton(
          onPressed: canExecute ? onPressed : null,
          style: style,
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              child,
              if (!canExecute && showOfflineIndicator) ...[
                const SizedBox(width: 4),
                Icon(
                  Icons.cloud_off,
                  size: 16,
                  color: Theme.of(context).colorScheme.onSurface.withOpacity(0.6),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  bool _canExecute(AdaptiveState state) {
    if (onPressed == null) return false;
    
    if (requiredCapability != null) {
      return state.mode.capabilities[requiredCapability] ?? false;
    }
    
    return true;
  }

  String _getTooltipMessage(AdaptiveState state) {
    if (requiredCapability != null) {
      final canExecute = state.mode.capabilities[requiredCapability] ?? false;
      if (!canExecute) {
        switch (requiredCapability) {
          case 'can_sync':
            return 'Sync not available in ${state.mode.message}';
          case 'can_sell':
            return 'Sales not available in ${state.mode.message}';
          case 'can_redeem':
            return 'Redemption not available in ${state.mode.message}';
          case 'can_refresh_data':
            return 'Data refresh not available in ${state.mode.message}';
          case 'can_access_reports':
            return 'Reports not available in ${state.mode.message}';
          default:
            return 'Feature not available in ${state.mode.message}';
        }
      }
    }
    
    return tooltip ?? '';
  }
}

class AdaptiveIconButton extends HookConsumerWidget {
  final IconData icon;
  final VoidCallback? onPressed;
  final String? requiredCapability;
  final String? tooltip;
  final Color? color;
  final double? iconSize;
  final bool showOfflineIndicator;

  const AdaptiveIconButton({
    super.key,
    required this.icon,
    this.onPressed,
    this.requiredCapability,
    this.tooltip,
    this.color,
    this.iconSize,
    this.showOfflineIndicator = true,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final adaptiveMode = ref.watch(adaptiveProvider);
    final canExecute = _canExecute(adaptiveMode);

    return Tooltip(
      message: tooltip ?? _getTooltipMessage(adaptiveMode),
      child: Opacity(
        opacity: canExecute ? 1.0 : 0.6,
        child: IconButton(
          onPressed: canExecute ? onPressed : null,
          icon: Icon(
            icon,
            color: canExecute ? color : color?.withOpacity(0.6),
            size: iconSize,
          ),
        ),
      ),
    );
  }

  bool _canExecute(AdaptiveState state) {
    if (onPressed == null) return false;
    
    if (requiredCapability != null) {
      return state.mode.capabilities[requiredCapability] ?? false;
    }
    
    return true;
  }

  String _getTooltipMessage(AdaptiveState state) {
    if (requiredCapability != null) {
      final canExecute = state.mode.capabilities[requiredCapability] ?? false;
      if (!canExecute) {
        switch (requiredCapability) {
          case 'can_sync':
            return 'Sync not available in ${state.mode.message}';
          case 'can_sell':
            return 'Sales not available in ${state.mode.message}';
          case 'can_redeem':
            return 'Redemption not available in ${state.mode.message}';
          case 'can_refresh_data':
            return 'Data refresh not available in ${state.mode.message}';
          case 'can_access_reports':
            return 'Reports not available in ${state.mode.message}';
          default:
            return 'Feature not available in ${state.mode.message}';
        }
      }
    }
    
    return tooltip ?? '';
  }
}

class AdaptiveFloatingActionButton extends HookConsumerWidget {
  final Widget child;
  final VoidCallback? onPressed;
  final String? requiredCapability;
  final String? tooltip;
  final Color? backgroundColor;
  final Color? foregroundColor;
  final bool showOfflineIndicator;

  const AdaptiveFloatingActionButton({
    super.key,
    required this.child,
    this.onPressed,
    this.requiredCapability,
    this.tooltip,
    this.backgroundColor,
    this.foregroundColor,
    this.showOfflineIndicator = true,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final adaptiveMode = ref.watch(adaptiveProvider);
    final canExecute = _canExecute(adaptiveMode);

    return Tooltip(
      message: tooltip ?? _getTooltipMessage(adaptiveMode),
      child: Opacity(
        opacity: canExecute ? 1.0 : 0.6,
        child: FloatingActionButton(
          onPressed: canExecute ? onPressed : null,
          backgroundColor: canExecute ? backgroundColor : backgroundColor?.withOpacity(0.6),
          foregroundColor: canExecute ? foregroundColor : foregroundColor?.withOpacity(0.6),
          child: Stack(
            children: [
              child,
              if (!canExecute && showOfflineIndicator)
                Positioned(
                  top: 0,
                  right: 0,
                  child: Container(
                    width: 16,
                    height: 16,
                    decoration: BoxDecoration(
                      color: Colors.red,
                      shape: BoxShape.circle,
                      border: Border.all(color: Colors.white, width: 2),
                    ),
                    child: const Icon(
                      Icons.cloud_off,
                      size: 8,
                      color: Colors.white,
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }

  bool _canExecute(AdaptiveState state) {
    if (onPressed == null) return false;
    
    if (requiredCapability != null) {
      return state.mode.capabilities[requiredCapability] ?? false;
    }
    
    return true;
  }

  String _getTooltipMessage(AdaptiveState state) {
    if (requiredCapability != null) {
      final canExecute = state.mode.capabilities[requiredCapability] ?? false;
      if (!canExecute) {
        switch (requiredCapability) {
          case 'can_sync':
            return 'Sync not available in ${state.mode.message}';
          case 'can_sell':
            return 'Sales not available in ${state.mode.message}';
          case 'can_redeem':
            return 'Redemption not available in ${state.mode.message}';
          case 'can_refresh_data':
            return 'Data refresh not available in ${state.mode.message}';
          case 'can_access_reports':
            return 'Reports not available in ${state.mode.message}';
          default:
            return 'Feature not available in ${state.mode.message}';
        }
      }
    }
    
    return tooltip ?? '';
  }
}
