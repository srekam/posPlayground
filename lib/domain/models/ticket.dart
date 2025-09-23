enum TicketType { single, multi, timepass, credit }

enum TicketStatus { active, expired, used, cancelled }

class Ticket {
  final String id;
  final String shortCode;
  final String qrPayload;
  final TicketType type;
  final int quotaOrMinutes;
  final DateTime validFrom;
  final DateTime validTo;
  final String lotNo;
  final String shiftId;
  final DateTime issuedAt;
  final double price;
  final String token;
  final String signature;
  final TicketStatus status;

  const Ticket({
    required this.id,
    required this.shortCode,
    required this.qrPayload,
    required this.type,
    required this.quotaOrMinutes,
    required this.validFrom,
    required this.validTo,
    required this.lotNo,
    required this.shiftId,
    required this.issuedAt,
    required this.price,
    required this.token,
    required this.signature,
    this.status = TicketStatus.active,
  });

  bool get isExpired => DateTime.now().isAfter(validTo);
  bool get isNotStarted => DateTime.now().isBefore(validFrom);
  bool get isValid => !isExpired && !isNotStarted && status == TicketStatus.active;

  String get typeDisplayName {
    switch (type) {
      case TicketType.single:
        return 'Single Entry';
      case TicketType.multi:
        return 'Multi Entry';
      case TicketType.timepass:
        return 'Time Pass';
      case TicketType.credit:
        return 'Credit';
    }
  }

  String get priceText => '฿${price.toStringAsFixed(0)}';
}
