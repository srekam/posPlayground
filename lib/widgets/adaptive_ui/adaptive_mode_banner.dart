import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/providers/adaptive_provider.dart';

class AdaptiveModeBanner extends ConsumerWidget {
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

    if (!showBanner) {
      return child;
    }

    return Banner(
      message: _getBannerMessage(adaptiveState),
      location: BannerLocation.topStart,
      color: _getBannerColor(adaptiveState),
      textStyle: const TextStyle(
        color: Colors.white,
        fontSize: 12,
        fontWeight: FontWeight.bold,
      ),
      child: child,
    );
  }

  String _getBannerMessage(AdaptiveState state) {
    switch (state.mode.type) {
      case AdaptiveModeType.online:
        return 'ONLINE';
      case AdaptiveModeType.offline:
        return 'OFFLINE';
      case AdaptiveModeType.degraded:
        return 'DEGRADED';
      case AdaptiveModeType.initializing:
        return 'INITIALIZING';
      case AdaptiveModeType.unregistered:
        return 'UNREGISTERED';
      case AdaptiveModeType.unauthenticated:
        return 'UNAUTHENTICATED';
    }
  }

  Color _getBannerColor(AdaptiveState state) {
    switch (state.mode.type) {
      case AdaptiveModeType.online:
        return Colors.green;
      case AdaptiveModeType.offline:
        return Colors.red;
      case AdaptiveModeType.degraded:
        return Colors.orange;
      case AdaptiveModeType.initializing:
        return Colors.blue;
      case AdaptiveModeType.unregistered:
        return Colors.purple;
      case AdaptiveModeType.unauthenticated:
        return Colors.amber;
    }
  }
}
