import 'package:flutter/foundation.dart';

class AppConfig {
  // Backend Configuration
  static const String defaultBackendUrl = 'http://localhost:50080';
  static const String stagingBackendUrl =
      'http://staging.playpark.local:50080/v1';
  static const String productionBackendUrl = 'https://api.playpark.com/v1';

  // Device Configuration
  static const String defaultDeviceId = 'pos-device-001';
  static const String defaultDeviceToken = 'pos-token-1';
  static const String defaultSiteKey =
      'tenant_demo_01:store_demo_01:demo-secret-key';

  // Demo Credentials
  static const String demoEmployeeEmail = 'manager@playpark.demo';
  static const String demoEmployeePin = '1234';

  // Sync Configuration
  static const Duration syncInterval = Duration(minutes: 5);
  static const Duration offlineTimeout = Duration(seconds: 10);
  static const int maxRetryAttempts = 3;

  // Feature Flags
  static const bool enableOfflineMode = true;
  static const bool enableSyncStatus = true;
  static const bool enableBackendHealthCheck = true;
  static const bool enableAdaptiveUI = true;

  // UI Configuration
  static const Duration connectionStatusDisplayDuration = Duration(seconds: 3);
  static const Duration syncProgressTimeout = Duration(minutes: 2);

  // Development Configuration
  static bool get isDevelopment => kDebugMode;
  static bool get isProduction => kReleaseMode;

  // Backend URL based on environment
  static String get backendUrl {
    final url = isDevelopment ? defaultBackendUrl : productionBackendUrl;
    print('DEBUG: AppConfig.backendUrl = $url, isDevelopment = $isDevelopment');
    return url;
  }

  // Device capabilities based on app type
  static List<String> get deviceCapabilities => [
        'can_sell',
        'can_redeem',
        'offline_cap',
        'sync_cap',
      ];

  // Default store configuration
  static const String defaultStoreId = 'store_demo_01';
  static const String defaultTenantId = 'tenant_demo_01';

  // Receipt configuration
  static const String receiptHeader = 'PlayPark Entertainment';
  static const String receiptFooter = 'Thank you for visiting!';

  // Print configuration
  static const int receiptPaperWidth = 58; // ESC/POS paper width

  // Timeout configurations
  static const Duration apiTimeout = Duration(seconds: 30);
  static const Duration syncTimeout = Duration(minutes: 5);
  static const Duration healthCheckTimeout = Duration(seconds: 10);

  // Cache configurations
  static const Duration packageCacheDuration = Duration(hours: 1);
  static const Duration settingsCacheDuration = Duration(minutes: 30);
  static const Duration shiftCacheDuration = Duration(minutes: 5);

  // Validation rules
  static const int minPackagePrice = 0;
  static const int maxPackagePrice = 10000;
  static const int minQuantity = 1;
  static const int maxQuantity = 100;

  // Error handling
  static const int maxConsecutiveFailures = 5;
  static const Duration failureBackoffDuration = Duration(minutes: 1);

  // Logging
  static const bool enableApiLogging = true;
  static const bool enableSyncLogging = true;
  static const bool enablePerformanceLogging = true;
}

class EnvironmentConfig {
  static String? _backendUrl;
  static String? _deviceId;
  static String? _deviceToken;
  static String? _siteKey;

  // Getters with fallback to defaults
  static String get backendUrl => _backendUrl ?? AppConfig.backendUrl;
  static String get deviceId => _deviceId ?? AppConfig.defaultDeviceId;
  static String get deviceToken => _deviceToken ?? AppConfig.defaultDeviceToken;
  static String get siteKey => _siteKey ?? AppConfig.defaultSiteKey;

  // Setters for runtime configuration
  static void setBackendUrl(String url) => _backendUrl = url;
  static void setDeviceId(String id) => _deviceId = id;
  static void setDeviceToken(String token) => _deviceToken = token;
  static void setSiteKey(String key) => _siteKey = key;

  // Reset to defaults
  static void reset() {
    _backendUrl = null;
    _deviceId = null;
    _deviceToken = null;
    _siteKey = null;
  }

  // Check if using custom configuration
  static bool get isUsingDefaults =>
      _backendUrl == null &&
      _deviceId == null &&
      _deviceToken == null &&
      _siteKey == null;
}

class FeatureFlags {
  static bool _offlineMode = AppConfig.enableOfflineMode;
  static bool _syncStatus = AppConfig.enableSyncStatus;
  static bool _healthCheck = AppConfig.enableBackendHealthCheck;
  static bool _adaptiveUI = AppConfig.enableAdaptiveUI;

  static bool get offlineMode => _offlineMode;
  static bool get syncStatus => _syncStatus;
  static bool get healthCheck => _healthCheck;
  static bool get adaptiveUI => _adaptiveUI;

  static void setOfflineMode(bool enabled) => _offlineMode = enabled;
  static void setSyncStatus(bool enabled) => _syncStatus = enabled;
  static void setHealthCheck(bool enabled) => _healthCheck = enabled;
  static void setAdaptiveUI(bool enabled) => _adaptiveUI = enabled;

  static void resetToDefaults() {
    _offlineMode = AppConfig.enableOfflineMode;
    _syncStatus = AppConfig.enableSyncStatus;
    _healthCheck = AppConfig.enableBackendHealthCheck;
    _adaptiveUI = AppConfig.enableAdaptiveUI;
  }
}
