import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/server_config.dart';

class ServerConfigService {
  static const String _configKey = 'server_config';
  static const String _apiKeyKey = 'api_key_info';

  static ServerConfig? _cachedConfig;
  static ApiKeyInfo? _cachedApiKey;

  // Get current server configuration
  static Future<ServerConfig> getCurrentConfig() async {
    if (_cachedConfig != null) return _cachedConfig!;

    final prefs = await SharedPreferences.getInstance();
    final configJson = prefs.getString(_configKey);

    if (configJson != null) {
      _cachedConfig = ServerConfig.fromJson(jsonDecode(configJson));
    } else {
      _cachedConfig = const ServerConfig(
        host: '127.0.0.1',
        port: 48080,
        protocol: 'http',
      );
    }

    return _cachedConfig!;
  }

  // Save server configuration
  static Future<void> saveConfig(ServerConfig config) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_configKey, jsonEncode(config.toJson()));
    _cachedConfig = config;
  }

  // Get current API key
  static Future<ApiKeyInfo?> getCurrentApiKey() async {
    if (_cachedApiKey != null) return _cachedApiKey;

    final prefs = await SharedPreferences.getInstance();
    final apiKeyJson = prefs.getString(_apiKeyKey);

    if (apiKeyJson != null) {
      _cachedApiKey = ApiKeyInfo.fromJson(jsonDecode(apiKeyJson));
    }

    return _cachedApiKey;
  }

  // Save API key
  static Future<void> saveApiKey(ApiKeyInfo apiKey) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_apiKeyKey, jsonEncode(apiKey.toJson()));
    _cachedApiKey = apiKey;
  }

  // Clear API key
  static Future<void> clearApiKey() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_apiKeyKey);
    _cachedApiKey = null;
  }

  // Test server connection
  static Future<ServerTestResult> testConnection(ServerConfig config) async {
    try {
      final client = HttpClient();
      client.connectionTimeout = config.timeout;

      final uri = Uri.parse('${config.baseUrl}/health');
      final request = await client.getUrl(uri);

      // Add headers
      config.requestHeaders.forEach((key, value) {
        request.headers.set(key, value);
      });

      final response = await request.close();
      client.close();

      if (response.statusCode == 200) {
        final body = await response.transform(utf8.decoder).join();
        final data = jsonDecode(body);

        return ServerTestResult.success(
          'Connection successful',
          data: data,
        );
      } else {
        return ServerTestResult.error(
          'Server responded with status ${response.statusCode}',
        );
      }
    } catch (e) {
      if (e is SocketException) {
        return ServerTestResult.error(
          'Cannot connect to server. Check host and port.',
        );
      } else if (e is HttpException) {
        return ServerTestResult.error(
          'HTTP error: ${e.message}',
        );
      } else {
        return ServerTestResult.error(
          'Connection failed: ${e.toString()}',
        );
      }
    }
  }

  // Generate API key from server
  static Future<ApiKeyGenerationResult> generateApiKey({
    required ServerConfig config,
    required String deviceId,
    required String deviceName,
    List<String> permissions = const ['read', 'write'],
  }) async {
    try {
      final client = http.Client();
      final uri = Uri.parse('${config.apiBaseUrl}/devices/api-key/generate');

      final response = await client
          .post(
            uri,
            headers: config.requestHeaders,
            body: jsonEncode({
              'device_id': deviceId,
              'device_name': deviceName,
              'permissions': permissions,
            }),
          )
          .timeout(config.timeout);

      client.close();

      if (response.statusCode == 200 || response.statusCode == 201) {
        final data = jsonDecode(response.body);

        if (data['success'] == true && data['data'] != null) {
          final apiKeyData = data['data'];
          final apiKey = ApiKeyInfo(
            key: apiKeyData['api_key'],
            encodedKey: ApiKeyInfo.encodeApiKey(apiKeyData['api_key']),
            createdAt: DateTime.parse(apiKeyData['created_at']),
            expiresAt: apiKeyData['expires_at'] != null
                ? DateTime.parse(apiKeyData['expires_at'])
                : null,
            permissions: List<String>.from(apiKeyData['permissions'] ?? []),
            deviceId: deviceId,
            name: deviceName,
          );

          return ApiKeyGenerationResult.success(apiKey);
        } else {
          return ApiKeyGenerationResult.error(
            data['message'] ?? 'Failed to generate API key',
          );
        }
      } else {
        final errorData = jsonDecode(response.body);
        return ApiKeyGenerationResult.error(
          errorData['error']['message'] ?? 'Server error',
        );
      }
    } catch (e) {
      return ApiKeyGenerationResult.error(
        'Network error: ${e.toString()}',
      );
    }
  }

  // Validate API key with server
  static Future<ApiKeyValidationResult> validateApiKey({
    required ServerConfig config,
    required String apiKey,
  }) async {
    try {
      final client = http.Client();
      final uri = Uri.parse('${config.apiBaseUrl}/auth/validate-api-key');

      final response = await client
          .post(
            uri,
            headers: {
              ...config.requestHeaders,
              'X-API-Key': apiKey,
            },
            body: jsonEncode({}),
          )
          .timeout(config.timeout);

      client.close();

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);

        if (data['success'] == true) {
          return ApiKeyValidationResult.success(
            'API key is valid',
            permissions: List<String>.from(data['data']['permissions'] ?? []),
          );
        } else {
          return ApiKeyValidationResult.error(
            data['message'] ?? 'Invalid API key',
          );
        }
      } else {
        final errorData = jsonDecode(response.body);
        return ApiKeyValidationResult.error(
          errorData['error']['message'] ?? 'Invalid API key',
        );
      }
    } catch (e) {
      return ApiKeyValidationResult.error(
        'Network error: ${e.toString()}',
      );
    }
  }

  // Get online devices from server
  static Future<List<OnlineDevice>> getOnlineDevices({
    required ServerConfig config,
  }) async {
    try {
      final client = http.Client();
      final uri = Uri.parse('${config.apiBaseUrl}/devices/online');

      final response = await client
          .get(
            uri,
            headers: config.requestHeaders,
          )
          .timeout(config.timeout);

      client.close();

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);

        if (data['success'] == true) {
          final devices = (data['data'] as List)
              .map((device) => OnlineDevice.fromJson(device))
              .toList();

          return devices;
        }
      }

      return [];
    } catch (e) {
      return [];
    }
  }

  // Reset to default configuration
  static Future<void> resetToDefault() async {
    _cachedConfig = null;
    _cachedApiKey = null;

    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_configKey);
    await prefs.remove(_apiKeyKey);
  }
}

class ServerTestResult {
  final bool isSuccess;
  final String message;
  final Map<String, dynamic>? data;

  const ServerTestResult._(this.isSuccess, this.message, {this.data});

  factory ServerTestResult.success(String message,
          {Map<String, dynamic>? data}) =>
      ServerTestResult._(true, message, data: data);

  factory ServerTestResult.error(String message) =>
      ServerTestResult._(false, message);
}

class ApiKeyGenerationResult {
  final bool isSuccess;
  final String message;
  final ApiKeyInfo? apiKey;

  const ApiKeyGenerationResult._(this.isSuccess, this.message, {this.apiKey});

  factory ApiKeyGenerationResult.success(ApiKeyInfo apiKey) =>
      ApiKeyGenerationResult._(true, 'API key generated successfully',
          apiKey: apiKey);

  factory ApiKeyGenerationResult.error(String message) =>
      ApiKeyGenerationResult._(false, message);
}

class ApiKeyValidationResult {
  final bool isValid;
  final String message;
  final List<String> permissions;

  const ApiKeyValidationResult._(this.isValid, this.message,
      {this.permissions = const []});

  factory ApiKeyValidationResult.success(String message,
          {List<String> permissions = const []}) =>
      ApiKeyValidationResult._(true, message, permissions: permissions);

  factory ApiKeyValidationResult.error(String message) =>
      ApiKeyValidationResult._(false, message);
}

class OnlineDevice {
  final String deviceId;
  final String deviceName;
  final String deviceType;
  final String status;
  final DateTime lastSeen;
  final String? ipAddress;
  final List<String> permissions;

  const OnlineDevice({
    required this.deviceId,
    required this.deviceName,
    required this.deviceType,
    required this.status,
    required this.lastSeen,
    this.ipAddress,
    required this.permissions,
  });

  factory OnlineDevice.fromJson(Map<String, dynamic> json) {
    return OnlineDevice(
      deviceId: json['device_id'] ?? '',
      deviceName: json['device_name'] ?? '',
      deviceType: json['device_type'] ?? 'unknown',
      status: json['status'] ?? 'offline',
      lastSeen:
          DateTime.parse(json['last_seen'] ?? DateTime.now().toIso8601String()),
      ipAddress: json['ip_address'],
      permissions: List<String>.from(json['permissions'] ?? []),
    );
  }

  bool get isOnline => status == 'online';
  bool get isOffline => status == 'offline';
  Duration get timeSinceLastSeen => DateTime.now().difference(lastSeen);
}
