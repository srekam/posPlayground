import '../../domain/models/ticket.dart';

class DatabaseTicket {
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
  final DateTime createdAt;
  final DateTime updatedAt;
  final DateTime? syncedAt;

  const DatabaseTicket({
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
    required this.createdAt,
    required this.updatedAt,
    this.syncedAt,
  });

  factory DatabaseTicket.fromDomain(Ticket ticket) {
    final now = DateTime.now();
    return DatabaseTicket(
      id: ticket.id,
      shortCode: ticket.shortCode,
      qrPayload: ticket.qrPayload,
      type: ticket.type,
      quotaOrMinutes: ticket.quotaOrMinutes,
      validFrom: ticket.validFrom,
      validTo: ticket.validTo,
      lotNo: ticket.lotNo,
      shiftId: ticket.shiftId,
      issuedAt: ticket.issuedAt,
      price: ticket.price,
      token: ticket.token,
      signature: ticket.signature,
      status: ticket.status,
      createdAt: now,
      updatedAt: now,
    );
  }

  factory DatabaseTicket.fromMap(Map<String, dynamic> map) {
    return DatabaseTicket(
      id: map['id'] ?? '',
      shortCode: map['short_code'] ?? '',
      qrPayload: map['qr_payload'] ?? '',
      type: TicketType.values.firstWhere(
        (e) => e.name == map['type'],
        orElse: () => TicketType.single,
      ),
      quotaOrMinutes: map['quota_or_minutes'] ?? 0,
      validFrom: DateTime.fromMillisecondsSinceEpoch(map['valid_from'] ?? 0),
      validTo: DateTime.fromMillisecondsSinceEpoch(map['valid_to'] ?? 0),
      lotNo: map['lot_no'] ?? '',
      shiftId: map['shift_id'] ?? '',
      issuedAt: DateTime.fromMillisecondsSinceEpoch(map['issued_at'] ?? 0),
      price: (map['price'] ?? 0).toDouble(),
      token: map['token'] ?? '',
      signature: map['signature'] ?? '',
      status: TicketStatus.values.firstWhere(
        (e) => e.name == map['status'],
        orElse: () => TicketStatus.active,
      ),
      createdAt: DateTime.fromMillisecondsSinceEpoch(map['created_at'] ?? 0),
      updatedAt: DateTime.fromMillisecondsSinceEpoch(map['updated_at'] ?? 0),
      syncedAt: map['synced_at'] != null 
          ? DateTime.fromMillisecondsSinceEpoch(map['synced_at'])
          : null,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'short_code': shortCode,
      'qr_payload': qrPayload,
      'type': type.name,
      'quota_or_minutes': quotaOrMinutes,
      'valid_from': validFrom.millisecondsSinceEpoch,
      'valid_to': validTo.millisecondsSinceEpoch,
      'lot_no': lotNo,
      'shift_id': shiftId,
      'issued_at': issuedAt.millisecondsSinceEpoch,
      'price': price,
      'token': token,
      'signature': signature,
      'status': status.name,
      'created_at': createdAt.millisecondsSinceEpoch,
      'updated_at': updatedAt.millisecondsSinceEpoch,
      'synced_at': syncedAt?.millisecondsSinceEpoch,
    };
  }

  Ticket toDomain() {
    return Ticket(
      id: id,
      shortCode: shortCode,
      qrPayload: qrPayload,
      type: type,
      quotaOrMinutes: quotaOrMinutes,
      validFrom: validFrom,
      validTo: validTo,
      lotNo: lotNo,
      shiftId: shiftId,
      issuedAt: issuedAt,
      price: price,
      token: token,
      signature: signature,
      status: status,
    );
  }

  DatabaseTicket copyWith({
    String? id,
    String? shortCode,
    String? qrPayload,
    TicketType? type,
    int? quotaOrMinutes,
    DateTime? validFrom,
    DateTime? validTo,
    String? lotNo,
    String? shiftId,
    DateTime? issuedAt,
    double? price,
    String? token,
    String? signature,
    TicketStatus? status,
    DateTime? createdAt,
    DateTime? updatedAt,
    DateTime? syncedAt,
  }) {
    return DatabaseTicket(
      id: id ?? this.id,
      shortCode: shortCode ?? this.shortCode,
      qrPayload: qrPayload ?? this.qrPayload,
      type: type ?? this.type,
      quotaOrMinutes: quotaOrMinutes ?? this.quotaOrMinutes,
      validFrom: validFrom ?? this.validFrom,
      validTo: validTo ?? this.validTo,
      lotNo: lotNo ?? this.lotNo,
      shiftId: shiftId ?? this.shiftId,
      issuedAt: issuedAt ?? this.issuedAt,
      price: price ?? this.price,
      token: token ?? this.token,
      signature: signature ?? this.signature,
      status: status ?? this.status,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      syncedAt: syncedAt ?? this.syncedAt,
    );
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is DatabaseTicket && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
}
