import 'dart:convert';
import 'dart:io';

class ServerConfig {
  final String host;
  final int port;
  final String protocol;
  final String? apiKey;
  final bool useHttps;
  final Duration timeout;
  final Map<String, String> headers;

  const ServerConfig({
    required this.host,
    required this.port,
    this.protocol = 'http',
    this.apiKey,
    this.useHttps = false,
    this.timeout = const Duration(seconds: 30),
    this.headers = const {},
  });

  String get baseUrl {
    final protocol = useHttps ? 'https' : this.protocol;
    return '$protocol://$host:$port';
  }

  String get apiBaseUrl => '$baseUrl/v1';

  Map<String, String> get requestHeaders {
    final headers = Map<String, String>.from(this.headers);
    if (apiKey != null) {
      headers['X-API-Key'] = apiKey!;
    }
    headers['Content-Type'] = 'application/json';
    headers['Accept'] = 'application/json';
    return headers;
  }

  bool get isValid {
    try {
      // Validate host format
      if (host.isEmpty) return false;
      
      // Check if it's a valid IP or hostname
      if (RegExp(r'^(\d{1,3}\.){3}\d{1,3}$').hasMatch(host)) {
        // Valid IP address
        return true;
      } else if (RegExp(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$').hasMatch(host)) {
        // Valid hostname
        return true;
      } else if (host == 'localhost' || host == '127.0.0.1') {
        return true;
      }
      
      return false;
    } catch (e) {
      return false;
    }
  }

  bool get isLocalhost => host == 'localhost' || host == '127.0.0.1';

  ServerConfig copyWith({
    String? host,
    int? port,
    String? protocol,
    String? apiKey,
    bool? useHttps,
    Duration? timeout,
    Map<String, String>? headers,
  }) {
    return ServerConfig(
      host: host ?? this.host,
      port: port ?? this.port,
      protocol: protocol ?? this.protocol,
      apiKey: apiKey ?? this.apiKey,
      useHttps: useHttps ?? this.useHttps,
      timeout: timeout ?? this.timeout,
      headers: headers ?? this.headers,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'host': host,
      'port': port,
      'protocol': protocol,
      'apiKey': apiKey,
      'useHttps': useHttps,
      'timeoutSeconds': timeout.inSeconds,
      'headers': headers,
    };
  }

  factory ServerConfig.fromJson(Map<String, dynamic> json) {
    return ServerConfig(
      host: json['host'] ?? 'localhost',
      port: json['port'] ?? 48080,
      protocol: json['protocol'] ?? 'http',
      apiKey: json['apiKey'],
      useHttps: json['useHttps'] ?? false,
      timeout: Duration(seconds: json['timeoutSeconds'] ?? 30),
      headers: Map<String, String>.from(json['headers'] ?? {}),
    );
  }

  @override
  String toString() {
    return 'ServerConfig(host: $host, port: $port, protocol: $protocol, hasApiKey: ${apiKey != null})';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is ServerConfig &&
        other.host == host &&
        other.port == port &&
        other.protocol == protocol &&
        other.apiKey == apiKey &&
        other.useHttps == useHttps;
  }

  @override
  int get hashCode {
    return Object.hash(host, port, protocol, apiKey, useHttps);
  }
}

class ApiKeyInfo {
  final String key;
  final String encodedKey;
  final DateTime createdAt;
  final DateTime? expiresAt;
  final List<String> permissions;
  final String deviceId;
  final String name;

  const ApiKeyInfo({
    required this.key,
    required this.encodedKey,
    required this.createdAt,
    this.expiresAt,
    required this.permissions,
    required this.deviceId,
    required this.name,
  });

  bool get isExpired {
    if (expiresAt == null) return false;
    return DateTime.now().isAfter(expiresAt!);
  }

  bool get isValid => !isExpired;

  String get displayKey {
    if (key.length <= 8) return key;
    return '${key.substring(0, 4)}...${key.substring(key.length - 4)}';
  }

  Map<String, dynamic> toJson() {
    return {
      'key': key,
      'encodedKey': encodedKey,
      'createdAt': createdAt.toIso8601String(),
      'expiresAt': expiresAt?.toIso8601String(),
      'permissions': permissions,
      'deviceId': deviceId,
      'name': name,
    };
  }

  factory ApiKeyInfo.fromJson(Map<String, dynamic> json) {
    return ApiKeyInfo(
      key: json['key'] ?? '',
      encodedKey: json['encodedKey'] ?? '',
      createdAt: DateTime.parse(json['createdAt'] ?? DateTime.now().toIso8601String()),
      expiresAt: json['expiresAt'] != null ? DateTime.parse(json['expiresAt']) : null,
      permissions: List<String>.from(json['permissions'] ?? []),
      deviceId: json['deviceId'] ?? '',
      name: json['name'] ?? '',
    );
  }

  static String encodeApiKey(String key) {
    return base64Encode(utf8.encode(key));
  }

  static String decodeApiKey(String encodedKey) {
    try {
      return utf8.decode(base64Decode(encodedKey));
    } catch (e) {
      throw FormatException('Invalid API key encoding');
    }
  }
}
