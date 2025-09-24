import 'dart:async';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import '../config/app_config.dart';

enum ConnectionStatus {
  connected,
  disconnected,
  unknown,
}

enum BackendStatus {
  healthy,
  unhealthy,
  unknown,
  checking,
}

class ConnectivityService {
  static final ConnectivityService _instance = ConnectivityService._internal();
  factory ConnectivityService() => _instance;
  ConnectivityService._internal();

  final Connectivity _connectivity = Connectivity();
  final StreamController<ConnectionStatus> _connectionController = 
      StreamController<ConnectionStatus>.broadcast();
  final StreamController<BackendStatus> _backendController = 
      StreamController<BackendStatus>.broadcast();

  StreamSubscription<ConnectivityResult>? _connectivitySubscription;
  Timer? _healthCheckTimer;
  Timer? _backendCheckTimer;

  ConnectionStatus _currentConnectionStatus = ConnectionStatus.unknown;
  BackendStatus _currentBackendStatus = BackendStatus.unknown;
  int _consecutiveFailures = 0;
  DateTime? _lastSuccessfulCheck;

  // Getters
  Stream<ConnectionStatus> get connectionStream => _connectionController.stream;
  Stream<BackendStatus> get backendStream => _backendController.stream;
  ConnectionStatus get currentConnectionStatus => _currentConnectionStatus;
  BackendStatus get currentBackendStatus => _currentBackendStatus;
  bool get isConnected => _currentConnectionStatus == ConnectionStatus.connected;
  bool get isBackendHealthy => _currentBackendStatus == BackendStatus.healthy;
  bool get isBackendChecking => _currentBackendStatus == BackendStatus.checking;

  // Initialize the service
  Future<void> initialize() async {
    // On web, skip heavy initialization
    if (kIsWeb) {
      _updateConnectionStatus(ConnectionStatus.connected);
      _updateBackendStatus(BackendStatus.healthy);
      return;
    }
    
    await _startConnectivityMonitoring();
    if (FeatureFlags.healthCheck) {
      await _startBackendHealthMonitoring();
    }
  }

  // Start monitoring network connectivity
  Future<void> _startConnectivityMonitoring() async {
    // Check initial connectivity
    await _checkConnectivity();
    
    // Listen to connectivity changes
    _connectivitySubscription = _connectivity.onConnectivityChanged.listen(
      (ConnectivityResult result) => _onConnectivityChanged(result),
      onError: (error) {
        _updateConnectionStatus(ConnectionStatus.unknown);
      },
    );
  }

  // Start monitoring backend health
  Future<void> _startBackendHealthMonitoring() async {
    // Initial health check
    await _checkBackendHealth();
    
    // Schedule periodic health checks
    _backendCheckTimer = Timer.periodic(
      AppConfig.syncInterval,
      (_) => _checkBackendHealth(),
    );
  }

  // Check network connectivity
  Future<void> _checkConnectivity() async {
    try {
      final connectivityResult = await _connectivity.checkConnectivity();
      final hasConnection = connectivityResult != ConnectivityResult.none;
      
      if (hasConnection) {
        // Additional check with actual network request
        final hasInternet = await _hasInternetConnection();
        _updateConnectionStatus(
          hasInternet ? ConnectionStatus.connected : ConnectionStatus.disconnected,
        );
      } else {
        _updateConnectionStatus(ConnectionStatus.disconnected);
      }
    } catch (e) {
      _updateConnectionStatus(ConnectionStatus.unknown);
    }
  }

  // Check if we have actual internet connectivity
  Future<bool> _hasInternetConnection() async {
    try {
      final result = await InternetAddress.lookup('google.com')
          .timeout(AppConfig.offlineTimeout);
      return result.isNotEmpty && result[0].rawAddress.isNotEmpty;
    } catch (e) {
      return false;
    }
  }

  // Handle connectivity changes
  void _onConnectivityChanged(ConnectivityResult result) {
    _checkConnectivity();
  }

  // Check backend health
  Future<void> _checkBackendHealth() async {
    if (_currentBackendStatus == BackendStatus.checking) return;
    
    _updateBackendStatus(BackendStatus.checking);
    
    try {
      final client = HttpClient();
      client.connectionTimeout = AppConfig.healthCheckTimeout;
      
      final request = await client.getUrl(
        Uri.parse('${EnvironmentConfig.backendUrl}/health'),
      );
      
      final response = await request.close().timeout(
        AppConfig.healthCheckTimeout,
      );
      
      client.close();
      
      if (response.statusCode == 200) {
        _consecutiveFailures = 0;
        _lastSuccessfulCheck = DateTime.now();
        _updateBackendStatus(BackendStatus.healthy);
      } else {
        _handleBackendFailure();
      }
    } catch (e) {
      _handleBackendFailure();
    }
  }

  // Handle backend failure
  void _handleBackendFailure() {
    _consecutiveFailures++;
    
    if (_consecutiveFailures >= AppConfig.maxConsecutiveFailures) {
      _updateBackendStatus(BackendStatus.unhealthy);
    } else {
      // Still checking, but with increasing delays
      final delay = Duration(
        milliseconds: _consecutiveFailures * 1000,
      );
      Future.delayed(delay, _checkBackendHealth);
    }
  }

  // Update connection status
  void _updateConnectionStatus(ConnectionStatus status) {
    if (_currentConnectionStatus != status) {
      _currentConnectionStatus = status;
      _connectionController.add(status);
      
      // Reset backend failures when connection is restored
      if (status == ConnectionStatus.connected) {
        _consecutiveFailures = 0;
        if (_currentBackendStatus == BackendStatus.unhealthy) {
          _checkBackendHealth();
        }
      }
    }
  }

  // Update backend status
  void _updateBackendStatus(BackendStatus status) {
    if (_currentBackendStatus != status) {
      _currentBackendStatus = status;
      _backendController.add(status);
    }
  }

  // Force a backend health check
  Future<void> forceBackendHealthCheck() async {
    _consecutiveFailures = 0;
    await _checkBackendHealth();
  }

  // Get connection quality info
  Map<String, dynamic> getConnectionInfo() {
    return {
      'connection_status': _currentConnectionStatus.name,
      'backend_status': _currentBackendStatus.name,
      'consecutive_failures': _consecutiveFailures,
      'last_successful_check': _lastSuccessfulCheck?.toIso8601String(),
      'backend_url': EnvironmentConfig.backendUrl,
    };
  }

  // Check if we should use offline mode
  bool shouldUseOfflineMode() {
    if (!FeatureFlags.offlineMode) return false;
    
    return _currentConnectionStatus == ConnectionStatus.disconnected ||
           _currentBackendStatus == BackendStatus.unhealthy ||
           _consecutiveFailures >= AppConfig.maxConsecutiveFailures;
  }

  // Check if we should attempt sync
  bool shouldAttemptSync() {
    return _currentConnectionStatus == ConnectionStatus.connected &&
           _currentBackendStatus == BackendStatus.healthy;
  }

  // Dispose resources
  void dispose() {
    _connectivitySubscription?.cancel();
    _healthCheckTimer?.cancel();
    _backendCheckTimer?.cancel();
    _connectionController.close();
    _backendController.close();
  }
}
