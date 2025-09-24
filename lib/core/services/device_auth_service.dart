import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../config/app_config.dart';
import '../../data/services/api_service.dart';
import '../../data/models/api_response.dart';

class DeviceInfo {
  final String deviceId;
  final String deviceToken;
  final String type;
  final List<String> capabilities;
  final String storeId;
  final String tenantId;
  final DateTime registeredAt;
  final String status;

  const DeviceInfo({
    required this.deviceId,
    required this.deviceToken,
    required this.type,
    required this.capabilities,
    required this.storeId,
    required this.tenantId,
    required this.registeredAt,
    required this.status,
  });

  factory DeviceInfo.fromJson(Map<String, dynamic> json) {
    return DeviceInfo(
      deviceId: json['device_id'] ?? '',
      deviceToken: json['device_token'] ?? '',
      type: json['type'] ?? 'POS',
      capabilities: List<String>.from(json['capabilities'] ?? []),
      storeId: json['store_id'] ?? '',
      tenantId: json['tenant_id'] ?? '',
      registeredAt: DateTime.parse(json['registered_at'] ?? DateTime.now().toIso8601String()),
      status: json['status'] ?? 'active',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'device_id': deviceId,
      'device_token': deviceToken,
      'type': type,
      'capabilities': capabilities,
      'store_id': storeId,
      'tenant_id': tenantId,
      'registered_at': registeredAt.toIso8601String(),
      'status': status,
    };
  }
}

class EmployeeInfo {
  final String employeeId;
  final String name;
  final String email;
  final List<String> roles;
  final List<String> permissions;
  final String status;

  const EmployeeInfo({
    required this.employeeId,
    required this.name,
    required this.email,
    required this.roles,
    required this.permissions,
    required this.status,
  });

  factory EmployeeInfo.fromJson(Map<String, dynamic> json) {
    return EmployeeInfo(
      employeeId: json['employee_id'] ?? '',
      name: json['name'] ?? '',
      email: json['email'] ?? '',
      roles: List<String>.from(json['roles'] ?? []),
      permissions: List<String>.from(json['permissions'] ?? []),
      status: json['status'] ?? 'active',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'employee_id': employeeId,
      'name': name,
      'email': email,
      'roles': roles,
      'permissions': permissions,
      'status': status,
    };
  }
}

class DeviceAuthService {
  static final DeviceAuthService _instance = DeviceAuthService._internal();
  factory DeviceAuthService() => _instance;
  DeviceAuthService._internal();

  String? _accessToken;
  DeviceInfo? _deviceInfo;
  EmployeeInfo? _employeeInfo;
  DateTime? _tokenExpiresAt;

  // Getters
  String? get accessToken => _accessToken;
  DeviceInfo? get deviceInfo => _deviceInfo;
  EmployeeInfo? get employeeInfo => _employeeInfo;
  bool get isAuthenticated => _accessToken != null && _tokenExpiresAt != null && 
                             DateTime.now().isBefore(_tokenExpiresAt!);
  bool get isDeviceRegistered => _deviceInfo != null;
  bool get isEmployeeLoggedIn => _employeeInfo != null;

  // Register device with backend
  Future<ApiResponse> registerDevice({
    required String siteKey,
    String? deviceName,
    Map<String, dynamic>? deviceMetadata,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('${EnvironmentConfig.backendUrl}/auth/device/register'),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: jsonEncode({
          'site_key': siteKey,
          'device_id': EnvironmentConfig.deviceId,
          'device_name': deviceName ?? 'POS Device',
          'device_type': 'POS',
          'capabilities': AppConfig.deviceCapabilities,
          'metadata': deviceMetadata ?? {},
        }),
      ).timeout(AppConfig.apiTimeout);

      final data = jsonDecode(response.body);

      if (response.statusCode == 201 || response.statusCode == 200) {
        _deviceInfo = DeviceInfo.fromJson(data['data']);
        EnvironmentConfig.setDeviceToken(_deviceInfo!.deviceToken);
        
        return ApiResponse.success(data['data']);
      } else {
        return ApiResponse.error(data['error']['message'] ?? 'Device registration failed');
      }
    } catch (e) {
      return ApiResponse.error('Network error during device registration: $e');
    }
  }

  // Login device with backend
  Future<ApiResponse> loginDevice() async {
    try {
      final response = await ApiService.deviceLogin(
        EnvironmentConfig.deviceId,
        EnvironmentConfig.deviceToken,
      );

      if (response.isSuccess) {
        final data = response.data;
        _accessToken = data['token'];
        _tokenExpiresAt = DateTime.now().add(const Duration(hours: 8)); // Default JWT expiry
        
        // Update device info if provided
        if (data['device'] != null) {
          _deviceInfo = DeviceInfo.fromJson(data['device']);
        }

        return response;
      } else {
        return response;
      }
    } catch (e) {
      return ApiResponse.error('Network error during device login: $e');
    }
  }

  // Login employee
  Future<ApiResponse> loginEmployee({
    required String email,
    required String pin,
  }) async {
    try {
      final response = await ApiService.employeeLogin(email, pin);

      if (response.isSuccess) {
        final data = response.data;
        _accessToken = data['token'];
        _tokenExpiresAt = DateTime.now().add(const Duration(hours: 8));
        
        // Update employee info
        if (data['employee'] != null) {
          _employeeInfo = EmployeeInfo.fromJson(data['employee']);
        }

        return response;
      } else {
        return response;
      }
    } catch (e) {
      return ApiResponse.error('Network error during employee login: $e');
    }
  }

  // Get current device info
  Future<ApiResponse> getCurrentDevice() async {
    if (!isAuthenticated) {
      return ApiResponse.error('Not authenticated');
    }

    try {
      final response = await http.get(
        Uri.parse('${EnvironmentConfig.backendUrl}/devices/me'),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'Authorization': 'Bearer $_accessToken',
        },
      ).timeout(AppConfig.apiTimeout);

      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        _deviceInfo = DeviceInfo.fromJson(data['data']);
        return ApiResponse.success(data['data']);
      } else {
        return ApiResponse.error(data['error']['message'] ?? 'Failed to get device info');
      }
    } catch (e) {
      return ApiResponse.error('Network error: $e');
    }
  }

  // Check if device has specific capability
  bool hasCapability(String capability) {
    return _deviceInfo?.capabilities.contains(capability) ?? false;
  }

  // Check if employee has specific permission
  bool hasPermission(String permission) {
    return _employeeInfo?.permissions.contains(permission) ?? false;
  }

  // Check if employee has specific role
  bool hasRole(String role) {
    return _employeeInfo?.roles.contains(role) ?? false;
  }

  // Refresh access token
  Future<ApiResponse> refreshToken() async {
    if (_deviceInfo == null) {
      return ApiResponse.error('Device not registered');
    }

    return await loginDevice();
  }

  // Logout
  void logout() {
    _accessToken = null;
    _employeeInfo = null;
    _tokenExpiresAt = null;
    ApiService.logout();
  }

  // Clear all authentication data
  void clearAuthentication() {
    _accessToken = null;
    _deviceInfo = null;
    _employeeInfo = null;
    _tokenExpiresAt = null;
    ApiService.logout();
  }

  // Get authentication status info
  Map<String, dynamic> getAuthStatus() {
    return {
      'is_authenticated': isAuthenticated,
      'is_device_registered': isDeviceRegistered,
      'is_employee_logged_in': isEmployeeLoggedIn,
      'token_expires_at': _tokenExpiresAt?.toIso8601String(),
      'device_info': _deviceInfo?.toJson(),
      'employee_info': _employeeInfo?.toJson(),
      'backend_url': EnvironmentConfig.backendUrl,
    };
  }

  // Initialize with stored credentials
  Future<void> initialize() async {
    // On web, skip device authentication initialization
    if (kIsWeb) {
      return;
    }
    
    // Try to login with stored device credentials
    if (EnvironmentConfig.deviceId.isNotEmpty && EnvironmentConfig.deviceToken.isNotEmpty) {
      await loginDevice();
    }
  }

  // Auto-register device if not registered
  Future<ApiResponse> ensureDeviceRegistered() async {
    if (isDeviceRegistered) {
      return ApiResponse.success(_deviceInfo!.toJson());
    }

    // Try to register with default site key
    return await registerDevice(siteKey: EnvironmentConfig.siteKey);
  }

  // Validate authentication and refresh if needed
  Future<bool> validateAuthentication() async {
    if (!isAuthenticated) {
      // Try to refresh token
      final refreshResult = await refreshToken();
      return refreshResult.isSuccess;
    }
    
    return true;
  }
}
