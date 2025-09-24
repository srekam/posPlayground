import 'dart:convert';
import '../../domain/models/outbox_event.dart';

class DatabaseOutboxEvent {
  final String id;
  final OutboxEventType type;
  final Map<String, dynamic> payload;
  final DateTime timestamp;
  final OutboxEventStatus status;
  final String? error;
  final int retryCount;
  final DateTime createdAt;

  const DatabaseOutboxEvent({
    required this.id,
    required this.type,
    required this.payload,
    required this.timestamp,
    this.status = OutboxEventStatus.queued,
    this.error,
    this.retryCount = 0,
    required this.createdAt,
  });

  factory DatabaseOutboxEvent.fromDomain(OutboxEvent event) {
    return DatabaseOutboxEvent(
      id: event.id,
      type: event.type,
      payload: event.payload,
      timestamp: event.timestamp,
      status: event.status,
      error: event.error,
      retryCount: event.retryCount,
      createdAt: DateTime.now(),
    );
  }

  factory DatabaseOutboxEvent.fromMap(Map<String, dynamic> map) {
    return DatabaseOutboxEvent(
      id: map['id'] ?? '',
      type: OutboxEventType.values.firstWhere(
        (e) => e.name == map['type'],
        orElse: () => OutboxEventType.sale,
      ),
      payload: map['payload'] != null 
          ? Map<String, dynamic>.from(jsonDecode(map['payload']))
          : {},
      timestamp: DateTime.fromMillisecondsSinceEpoch(map['timestamp'] ?? 0),
      status: OutboxEventStatus.values.firstWhere(
        (e) => e.name == map['status'],
        orElse: () => OutboxEventStatus.queued,
      ),
      error: map['error'],
      retryCount: map['retry_count'] ?? 0,
      createdAt: DateTime.fromMillisecondsSinceEpoch(map['created_at'] ?? 0),
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'type': type.name,
      'payload': jsonEncode(payload),
      'timestamp': timestamp.millisecondsSinceEpoch,
      'status': status.name,
      'error': error,
      'retry_count': retryCount,
      'created_at': createdAt.millisecondsSinceEpoch,
    };
  }

  OutboxEvent toDomain() {
    return OutboxEvent(
      id: id,
      type: type,
      payload: payload,
      timestamp: timestamp,
      status: status,
      error: error,
      retryCount: retryCount,
    );
  }

  DatabaseOutboxEvent copyWith({
    String? id,
    OutboxEventType? type,
    Map<String, dynamic>? payload,
    DateTime? timestamp,
    OutboxEventStatus? status,
    String? error,
    int? retryCount,
    DateTime? createdAt,
  }) {
    return DatabaseOutboxEvent(
      id: id ?? this.id,
      type: type ?? this.type,
      payload: payload ?? this.payload,
      timestamp: timestamp ?? this.timestamp,
      status: status ?? this.status,
      error: error ?? this.error,
      retryCount: retryCount ?? this.retryCount,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is DatabaseOutboxEvent && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
}

