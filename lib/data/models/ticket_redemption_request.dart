class TicketRedemptionRequest {
  final String qrToken;
  final String deviceId;

  TicketRedemptionRequest({
    required this.qrToken,
    required this.deviceId,
  });

  Map<String, dynamic> toJson() => {
    'qr_token': qrToken,
    'device_id': deviceId,
  };
}
