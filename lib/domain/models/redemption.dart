enum RedemptionStatus { pass, fail }
enum RedemptionReason { 
  expired, 
  notStarted, 
  quotaExhausted, 
  duplicateUse, 
  invalidSignature, 
  wrongDevice;

  String get reasonDisplayName {
    switch (this) {
      case RedemptionReason.expired:
        return 'Ticket expired';
      case RedemptionReason.notStarted:
        return 'Ticket not yet valid';
      case RedemptionReason.quotaExhausted:
        return 'No uses remaining';
      case RedemptionReason.duplicateUse:
        return 'Already used';
      case RedemptionReason.invalidSignature:
        return 'Invalid ticket';
      case RedemptionReason.wrongDevice:
        return 'Wrong device';
    }
  }
}

class Redemption {
  final String id;
  final String ticketId;
  final String deviceId;
  final DateTime timestamp;
  final RedemptionStatus status;
  final RedemptionReason? reason;
  final int? remainingQuotaOrTime;
  final String? notes;

  const Redemption({
    required this.id,
    required this.ticketId,
    required this.deviceId,
    required this.timestamp,
    required this.status,
    this.reason,
    this.remainingQuotaOrTime,
    this.notes,
  });

  String get statusDisplayName {
    switch (status) {
      case RedemptionStatus.pass:
        return 'PASS';
      case RedemptionStatus.fail:
        return 'FAIL';
    }
  }

}
