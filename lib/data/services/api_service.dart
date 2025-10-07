import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/api_response.dart';
import '../models/sale_request.dart';
import '../models/ticket_redemption_request.dart';

class ApiService {
  static String get baseUrl {
    const url =
        'http://10.3.11.253:50080'; // Updated for Android emulator communication
    print('DEBUG: ApiService.baseUrl = $url');
    return url;
  }

  static String? _authToken;
  static String? _deviceToken;

  // Headers
  static Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        if (_authToken != null) 'Authorization': 'Bearer $_authToken',
        if (_deviceToken != null) 'X-Device-Token': _deviceToken!,
      };

  // Device Authentication
  static Future<ApiResponse> deviceLogin(
      String deviceId, String deviceToken) async {
    try {
      _deviceToken = deviceToken;
      final response = await http.post(
        Uri.parse('$baseUrl/api/v1/auth/device/login'),
        headers: _headers,
        body: jsonEncode({
          'device_id': deviceId,
          'device_token': deviceToken,
        }),
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        _authToken = data['data']['token'];
        return ApiResponse.success(data['data']);
      } else {
        return ApiResponse.error(data['error']['message'] ?? 'Login failed');
      }
    } catch (e) {
      return ApiResponse.error('Network error: $e');
    }
  }

  // Employee Authentication
  static Future<ApiResponse> employeeLogin(String email, String pin) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/v1/auth/employees/login'),
        headers: _headers,
        body: jsonEncode({
          'email': email,
          'pin': pin,
        }),
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        _authToken = data['data']['token'];
        return ApiResponse.success(data['data']);
      } else {
        return ApiResponse.error(data['error']['message'] ?? 'Login failed');
      }
    } catch (e) {
      return ApiResponse.error('Network error: $e');
    }
  }

  // Device Enrollment
  static Future<ApiResponse> enrollDevice({
    required String enrollToken,
    required String deviceType,
    required String appVersion,
    required String deviceFingerprint,
  }) async {
    try {
      final url = '$baseUrl/api/v1/auth/device/enroll';
      print('DEBUG: Enrolling device with URL: $url');
      final response = await http.post(
        Uri.parse(url),
        headers: _headers,
        body: jsonEncode({
          'enroll_token': enrollToken,
          'device_type': deviceType,
          'app_version': appVersion,
          'device_fingerprint': deviceFingerprint,
        }),
      );

      print('DEBUG: Response status: ${response.statusCode}');
      print('DEBUG: Response body: ${response.body}');

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return ApiResponse.success(data);
      } else {
        try {
          final data = jsonDecode(response.body);
          return ApiResponse.error(data['message'] ?? 'Enrollment failed');
        } catch (e) {
          return ApiResponse.error('Enrollment failed: ${response.body}');
        }
      }
    } catch (e) {
      return ApiResponse.error('Network error: $e');
    }
  }

  // Bootstrap
  static Future<ApiResponse> bootstrap() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/v1/gate/bootstrap'),
        headers: _headers,
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        return ApiResponse.success(data);
      } else {
        return ApiResponse.error(
            data['error']['message'] ?? 'Bootstrap failed');
      }
    } catch (e) {
      return ApiResponse.error('Network error: $e');
    }
  }

  // Get Packages
  static Future<ApiResponse> getPackages({String? storeId}) async {
    try {
      final queryParams = storeId != null ? '?store_id=$storeId' : '';
      final response = await http.get(
        Uri.parse('$baseUrl/api/v1/catalog/packages$queryParams'),
        headers: _headers,
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        return ApiResponse.success(data['data']);
      } else {
        return ApiResponse.error(
            data['error']['message'] ?? 'Failed to fetch packages');
      }
    } catch (e) {
      return ApiResponse.error('Network error: $e');
    }
  }

  // Get Pricing Rules
  static Future<ApiResponse> getPricingRules({String? storeId}) async {
    try {
      final queryParams = storeId != null ? '?store_id=$storeId' : '';
      final response = await http.get(
        Uri.parse('$baseUrl/api/v1/catalog/pricing-rules$queryParams'),
        headers: _headers,
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        return ApiResponse.success(data['data']);
      } else {
        return ApiResponse.error(
            data['error']['message'] ?? 'Failed to fetch pricing rules');
      }
    } catch (e) {
      return ApiResponse.error('Network error: $e');
    }
  }

  // Create Sale
  static Future<ApiResponse> createSale(SaleRequest saleRequest) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/v1/sales'),
        headers: _headers,
        body: jsonEncode(saleRequest.toJson()),
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 201) {
        return ApiResponse.success(data['data']);
      } else {
        return ApiResponse.error(
            data['error']['message'] ?? 'Failed to create sale');
      }
    } catch (e) {
      return ApiResponse.error('Network error: $e');
    }
  }

  // Redeem Ticket
  static Future<ApiResponse> redeemTicket(
      TicketRedemptionRequest request) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/v1/tickets/redeem'),
        headers: _headers,
        body: jsonEncode(request.toJson()),
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        return ApiResponse.success(data['data']);
      } else {
        return ApiResponse.error(
            data['error']['message'] ?? 'Failed to redeem ticket');
      }
    } catch (e) {
      return ApiResponse.error('Network error: $e');
    }
  }

  // Get Ticket Details
  static Future<ApiResponse> getTicket(String ticketId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/v1/tickets/$ticketId'),
        headers: _headers,
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        return ApiResponse.success(data['data']);
      } else {
        return ApiResponse.error(
            data['error']['message'] ?? 'Failed to fetch ticket');
      }
    } catch (e) {
      return ApiResponse.error('Network error: $e');
    }
  }

  // Open Shift
  static Future<ApiResponse> openShift(
      String employeeId, double cashOpen) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/v1/shifts/open'),
        headers: _headers,
        body: jsonEncode({
          'employee_id': employeeId,
          'cash_open': cashOpen,
        }),
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 201) {
        return ApiResponse.success(data['data']);
      } else {
        return ApiResponse.error(
            data['error']['message'] ?? 'Failed to open shift');
      }
    } catch (e) {
      return ApiResponse.error('Network error: $e');
    }
  }

  // Close Shift
  static Future<ApiResponse> closeShift(
      String employeeId, double cashCounted) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/v1/shifts/close'),
        headers: _headers,
        body: jsonEncode({
          'employee_id': employeeId,
          'cash_counted': cashCounted,
        }),
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        return ApiResponse.success(data['data']);
      } else {
        return ApiResponse.error(
            data['error']['message'] ?? 'Failed to close shift');
      }
    } catch (e) {
      return ApiResponse.error('Network error: $e');
    }
  }

  // Get Current Shift
  static Future<ApiResponse> getCurrentShift() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/v1/shifts/current'),
        headers: _headers,
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        return ApiResponse.success(data['data']);
      } else {
        return ApiResponse.error(
            data['error']['message'] ?? 'Failed to fetch current shift');
      }
    } catch (e) {
      return ApiResponse.error('Network error: $e');
    }
  }

  // Get Sales Report
  static Future<ApiResponse> getSalesReport({
    required String startDate,
    required String endDate,
    String? storeId,
  }) async {
    try {
      final queryParams = <String, String>{
        'start_date': startDate,
        'end_date': endDate,
        if (storeId != null) 'store_id': storeId,
      };

      final uri = Uri.parse('$baseUrl/api/v1/reports/sales').replace(
        queryParameters: queryParams,
      );

      final response = await http.get(uri, headers: _headers);
      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        return ApiResponse.success(data['data']);
      } else {
        return ApiResponse.error(
            data['error']['message'] ?? 'Failed to fetch sales report');
      }
    } catch (e) {
      return ApiResponse.error('Network error: $e');
    }
  }

  // Health Check
  static Future<ApiResponse> healthCheck() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/healthz'),
        headers: _headers,
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        return ApiResponse.success(data);
      } else {
        return ApiResponse.error('Health check failed');
      }
    } catch (e) {
      return ApiResponse.error('Network error: $e');
    }
  }

  // Logout
  static void logout() {
    _authToken = null;
    _deviceToken = null;
  }
}
