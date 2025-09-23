enum OutboxEventType { sale, redemption, reprint, refund }

enum OutboxEventStatus { queued, sending, sent, failed }

class OutboxEvent {
  final String id;
  final OutboxEventType type;
  final Map<String, dynamic> payload;
  final DateTime timestamp;
  final OutboxEventStatus status;
  final String? error;
  final int retryCount;

  const OutboxEvent({
    required this.id,
    required this.type,
    required this.payload,
    required this.timestamp,
    this.status = OutboxEventStatus.queued,
    this.error,
    this.retryCount = 0,
  });

  OutboxEvent copyWith({
    String? id,
    OutboxEventType? type,
    Map<String, dynamic>? payload,
    DateTime? timestamp,
    OutboxEventStatus? status,
    String? error,
    int? retryCount,
  }) {
    return OutboxEvent(
      id: id ?? this.id,
      type: type ?? this.type,
      payload: payload ?? this.payload,
      timestamp: timestamp ?? this.timestamp,
      status: status ?? this.status,
      error: error ?? this.error,
      retryCount: retryCount ?? this.retryCount,
    );
  }

  String get typeDisplayName {
    switch (type) {
      case OutboxEventType.sale:
        return 'Sale';
      case OutboxEventType.redemption:
        return 'Redemption';
      case OutboxEventType.reprint:
        return 'Reprint';
      case OutboxEventType.refund:
        return 'Refund';
    }
  }

  String get statusDisplayName {
    switch (status) {
      case OutboxEventStatus.queued:
        return 'Queued';
      case OutboxEventStatus.sending:
        return 'Sending';
      case OutboxEventStatus.sent:
        return 'Sent';
      case OutboxEventStatus.failed:
        return 'Failed';
    }
  }
}
