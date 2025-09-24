class AuthRequest {
  final String email;
  final String pin;

  AuthRequest({
    required this.email,
    required this.pin,
  });

  Map<String, dynamic> toJson() => {
    'email': email,
    'pin': pin,
  };
}

class DeviceAuthRequest {
  final String deviceId;
  final String deviceToken;

  DeviceAuthRequest({
    required this.deviceId,
    required this.deviceToken,
  });

  Map<String, dynamic> toJson() => {
    'device_id': deviceId,
    'device_token': deviceToken,
  };
}
