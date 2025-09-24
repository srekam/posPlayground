import 'package:flutter/foundation.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../services/connectivity_service.dart';
import '../services/device_auth_service.dart';

// Connectivity providers
final connectivityServiceProvider = Provider<ConnectivityService>((ref) {
  return ConnectivityService();
});

final connectionStatusProvider = StreamProvider<ConnectionStatus>((ref) {
  final connectivityService = ref.read(connectivityServiceProvider);
  return connectivityService.connectionStream;
});

final backendStatusProvider = StreamProvider<BackendStatus>((ref) {
  final connectivityService = ref.read(connectivityServiceProvider);
  return connectivityService.backendStream;
});

// Device authentication providers
final deviceAuthServiceProvider = Provider<DeviceAuthService>((ref) {
  return DeviceAuthService();
});

final deviceAuthStatusProvider = FutureProvider<Map<String, dynamic>>((ref) {
  final deviceAuthService = ref.read(deviceAuthServiceProvider);
  return Future.value(deviceAuthService.getAuthStatus());
});

// Adaptive mode provider
final adaptiveProvider = StateNotifierProvider<AdaptiveModeNotifier, AdaptiveState>((ref) {
  return AdaptiveModeNotifier(ref);
});

class AdaptiveModeNotifier extends StateNotifier<AdaptiveState> {
  final Ref _ref;
  final ConnectivityService _connectivityService;
  final DeviceAuthService _deviceAuthService;

  AdaptiveModeNotifier(this._ref)
      : _connectivityService = _ref.read(connectivityServiceProvider),
        _deviceAuthService = _ref.read(deviceAuthServiceProvider),
        super(AdaptiveState(mode: AdaptiveMode.initializing())) {
    // Initialize asynchronously without blocking UI
    _initializeAsync();
  }

  void _initializeAsync() {
    // Initialize asynchronously without blocking UI
    Future.microtask(() async {
      try {
        await _initialize();
      } catch (e) {
        // If initialization fails, set to offline mode
        state = AdaptiveState(mode: AdaptiveMode.offline());
      }
    });
  }

  Future<void> _initialize() async {
    // On web, skip heavy initialization and set to offline mode
    if (kIsWeb) {
      state = AdaptiveState(mode: AdaptiveMode.offline());
      return;
    }

    // Initialize connectivity service
    await _connectivityService.initialize();

    // Initialize device auth service
    await _deviceAuthService.initialize();

    // Listen to connectivity changes
    _connectivityService.connectionStream.listen(_onConnectionChanged);
    _connectivityService.backendStream.listen(_onBackendChanged);

    // Update initial state
    _updateAdaptiveMode();
  }

  void _onConnectionChanged(ConnectionStatus status) {
    _updateAdaptiveMode();
  }

  void _onBackendChanged(BackendStatus status) {
    _updateAdaptiveMode();
  }

  void _updateAdaptiveMode() {
    final connectionStatus = _connectivityService.currentConnectionStatus;
    final backendStatus = _connectivityService.currentBackendStatus;
    final isAuthenticated = _deviceAuthService.isAuthenticated;
    final isDeviceRegistered = _deviceAuthService.isDeviceRegistered;

    AdaptiveMode newMode;

    if (connectionStatus == ConnectionStatus.disconnected) {
      newMode = const AdaptiveMode.offline();
    } else if (backendStatus == BackendStatus.unhealthy) {
      newMode = const AdaptiveMode.degraded();
    } else if (!isDeviceRegistered) {
      newMode = const AdaptiveMode.unregistered();
    } else if (!isAuthenticated) {
      newMode = const AdaptiveMode.unauthenticated();
    } else {
      newMode = const AdaptiveMode.online();
    }

    final newState = AdaptiveState(mode: newMode);
    if (state.mode != newMode) {
      state = newState;
    }
  }

  // Force update adaptive mode
  void forceUpdate() {
    _updateAdaptiveMode();
  }

  // Switch to offline mode manually
  void switchToOffline() {
    state = AdaptiveState(mode: AdaptiveMode.offline());
  }

  // Switch to online mode manually
  void switchToOnline() {
    _updateAdaptiveMode();
  }
}

class AdaptiveState {
  final AdaptiveMode mode;
  final DateTime lastUpdated;

  AdaptiveState({
    required this.mode,
    DateTime? lastUpdated,
  }) : lastUpdated = lastUpdated ?? DateTime.now();

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is AdaptiveState && other.mode == mode;
  }

  @override
  int get hashCode => mode.hashCode;
}

class AdaptiveMode {
  final AdaptiveModeType type;
  final String message;
  final Map<String, dynamic> capabilities;

  const AdaptiveMode({
    required this.type,
    required this.message,
    this.capabilities = const {},
  });

  const AdaptiveMode.initializing()
      : type = AdaptiveModeType.initializing,
        message = 'Initializing...',
        capabilities = const {};

  const AdaptiveMode.online()
      : type = AdaptiveModeType.online,
        message = 'Online',
        capabilities = const {
          'can_sync': true,
          'can_sell': true,
          'can_redeem': true,
          'can_refresh_data': true,
          'can_access_reports': true,
        };

  const AdaptiveMode.offline()
      : type = AdaptiveModeType.offline,
        message = 'Offline Mode',
        capabilities = const {
          'can_sync': false,
          'can_sell': true,
          'can_redeem': true,  // Allow QR scanning in offline mode
          'can_refresh_data': false,
          'can_access_reports': true,  // Allow reports in offline mode
          'can_use_cached_data': true,
        };

  const AdaptiveMode.degraded()
      : type = AdaptiveModeType.degraded,
        message = 'Limited Connectivity',
        capabilities = const {
          'can_sync': false,
          'can_sell': true,
          'can_redeem': true,  // Allow QR scanning in degraded mode
          'can_refresh_data': false,
          'can_access_reports': true,  // Allow reports in degraded mode
          'can_use_cached_data': true,
          'can_retry_connection': true,
        };

  const AdaptiveMode.unregistered()
      : type = AdaptiveModeType.unregistered,
        message = 'Device Not Registered',
        capabilities = const {
          'can_sync': false,
          'can_sell': false,
          'can_redeem': false,
          'can_refresh_data': false,
          'can_access_reports': false,
          'can_register_device': true,
        };

  const AdaptiveMode.unauthenticated()
      : type = AdaptiveModeType.unauthenticated,
        message = 'Authentication Required',
        capabilities = const {
          'can_sync': false,
          'can_sell': false,
          'can_redeem': false,
          'can_refresh_data': false,
          'can_access_reports': false,
          'can_login': true,
        };

  bool get canSync => capabilities['can_sync'] ?? false;
  bool get canSell => capabilities['can_sell'] ?? false;
  bool get canRedeem => capabilities['can_redeem'] ?? false;
  bool get canRefreshData => capabilities['can_refresh_data'] ?? false;
  bool get canAccessReports => capabilities['can_access_reports'] ?? false;
  bool get canUseCachedData => capabilities['can_use_cached_data'] ?? false;
  bool get canRetryConnection => capabilities['can_retry_connection'] ?? false;
  bool get canRegisterDevice => capabilities['can_register_device'] ?? false;
  bool get canLogin => capabilities['can_login'] ?? false;

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is AdaptiveMode && other.type == type;
  }

  @override
  int get hashCode => type.hashCode;

  @override
  String toString() => 'AdaptiveMode(${type.name}: $message)';
}

enum AdaptiveModeType {
  initializing,
  online,
  offline,
  degraded,
  unregistered,
  unauthenticated,
}

// Feature availability providers
final canSyncProvider = Provider<bool>((ref) {
  final adaptiveState = ref.watch(adaptiveProvider);
  return adaptiveState.mode.canSync;
});

final canSellProvider = Provider<bool>((ref) {
  final adaptiveState = ref.watch(adaptiveProvider);
  return adaptiveState.mode.canSell;
});

final canRedeemProvider = Provider<bool>((ref) {
  final adaptiveState = ref.watch(adaptiveProvider);
  return adaptiveState.mode.canRedeem;
});

final canRefreshDataProvider = Provider<bool>((ref) {
  final adaptiveState = ref.watch(adaptiveProvider);
  return adaptiveState.mode.canRefreshData;
});

final canAccessReportsProvider = Provider<bool>((ref) {
  final adaptiveState = ref.watch(adaptiveProvider);
  return adaptiveState.mode.canAccessReports;
});

final canUseCachedDataProvider = Provider<bool>((ref) {
  final adaptiveState = ref.watch(adaptiveProvider);
  return adaptiveState.mode.canUseCachedData;
});

// Connection status summary provider
final connectionSummaryProvider = Provider<Map<String, dynamic>>((ref) {
  final adaptiveState = ref.watch(adaptiveProvider);
  final connectionStatus = ref.watch(connectionStatusProvider).whenOrNull(
    data: (status) => status.name,
    loading: () => 'checking',
    error: (_, __) => 'error',
  );
  final backendStatus = ref.watch(backendStatusProvider).whenOrNull(
    data: (status) => status.name,
    loading: () => 'checking',
    error: (_, __) => 'error',
  );

  return {
    'adaptive_mode': adaptiveState.mode.type.name,
    'message': adaptiveState.mode.message,
    'connection_status': connectionStatus,
    'backend_status': backendStatus,
    'capabilities': adaptiveState.mode.capabilities,
    'timestamp': DateTime.now().toIso8601String(),
  };
});
