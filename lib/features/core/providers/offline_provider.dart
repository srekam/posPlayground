import 'package:flutter/foundation.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../../../domain/models/outbox_event.dart';

final offlineProvider = StateNotifierProvider<OfflineNotifier, OfflineState>((ref) {
  return OfflineNotifier();
});

class OfflineState {
  final bool isOnline;
  final List<OutboxEvent> outboxEvents;
  final int pendingCount;

  const OfflineState({
    this.isOnline = true,
    this.outboxEvents = const [],
    this.pendingCount = 0,
  });

  OfflineState copyWith({
    bool? isOnline,
    List<OutboxEvent>? outboxEvents,
    int? pendingCount,
  }) {
    return OfflineState(
      isOnline: isOnline ?? this.isOnline,
      outboxEvents: outboxEvents ?? this.outboxEvents,
      pendingCount: pendingCount ?? this.pendingCount,
    );
  }
}

class OfflineNotifier extends StateNotifier<OfflineState> {
  OfflineNotifier() : super(const OfflineState()) {
    // Simulate network status changes for demo
    _simulateNetworkChanges();
  }

  void _simulateNetworkChanges() {
    // Simulate going offline/online every 30 seconds for demo
    Future.delayed(const Duration(seconds: 30), () {
      if (mounted) {
        state = state.copyWith(isOnline: !state.isOnline);
        _simulateNetworkChanges();
      }
    });
  }

  void toggleOnlineStatus() {
    state = state.copyWith(isOnline: !state.isOnline);
  }

  void addOutboxEvent(OutboxEventType type, Map<String, dynamic> payload) {
    final event = OutboxEvent(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      type: type,
      payload: payload,
      timestamp: DateTime.now(),
    );

    final updatedEvents = [...state.outboxEvents, event];
    final pendingCount = updatedEvents.where((e) => e.status == OutboxEventStatus.queued).length;

    state = state.copyWith(
      outboxEvents: updatedEvents,
      pendingCount: pendingCount,
    );

    // If online, try to send immediately
    if (state.isOnline) {
      _processOutbox();
    }
  }

  Future<void> _processOutbox() async {
    final queuedEvents = state.outboxEvents
        .where((e) => e.status == OutboxEventStatus.queued)
        .toList();

    for (final event in queuedEvents) {
      await _sendEvent(event);
    }
  }

  Future<void> _sendEvent(OutboxEvent event) async {
    // Mark as sending
    _updateEventStatus(event.id, OutboxEventStatus.sending);

    try {
      // Simulate network delay
      await Future.delayed(const Duration(seconds: 1));

      // Simulate 90% success rate
      final success = (DateTime.now().millisecondsSinceEpoch % 10) != 0;
      
      if (success) {
        _updateEventStatus(event.id, OutboxEventStatus.sent);
      } else {
        _updateEventStatus(
          event.id, 
          OutboxEventStatus.failed, 
          error: 'Network timeout',
        );
      }
    } catch (e) {
      _updateEventStatus(
        event.id, 
        OutboxEventStatus.failed, 
        error: e.toString(),
      );
    }
  }


  void retryFailedEvents() {
    final failedEvents = state.outboxEvents
        .where((e) => e.status == OutboxEventStatus.failed)
        .toList();

    for (final event in failedEvents) {
      _updateEventStatus(event.id, OutboxEventStatus.queued);
    }

    if (state.isOnline) {
      _processOutbox();
    }
  }

  void clearSentEvents() {
    final filteredEvents = state.outboxEvents
        .where((e) => e.status != OutboxEventStatus.sent)
        .toList();

    state = state.copyWith(outboxEvents: filteredEvents);
  }

  List<OutboxEvent> getEventsByType(OutboxEventType type) {
    return state.outboxEvents.where((e) => e.type == type).toList();
  }

  int getEventCountByType(OutboxEventType type) {
    return getEventsByType(type).length;
  }

  void _updateEventStatus(String eventId, OutboxEventStatus status, {String? error}) {
    final updatedEvents = state.outboxEvents.map((event) {
      if (event.id == eventId) {
        return event.copyWith(
          status: status,
          error: error,
          retryCount: status == OutboxEventStatus.failed ? event.retryCount + 1 : event.retryCount,
        );
      }
      return event;
    }).toList();

    final pendingCount = updatedEvents.where((e) => e.status == OutboxEventStatus.queued).length;

    state = state.copyWith(
      outboxEvents: updatedEvents,
      pendingCount: pendingCount,
    );
  }
}
