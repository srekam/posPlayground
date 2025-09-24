import '../database/database_helper.dart';
import '../models/database_outbox_event.dart';
import '../../domain/models/outbox_event.dart';

class OfflineOutboxRepository {
  static const String _tableName = 'outbox_events';

  Future<List<DatabaseOutboxEvent>> getAllEvents() async {
    final maps = await DatabaseHelper.query(
      _tableName,
      orderBy: 'created_at ASC',
    );
    return maps.map((map) => DatabaseOutboxEvent.fromMap(map)).toList();
  }

  Future<List<DatabaseOutboxEvent>> getQueuedEvents() async {
    final maps = await DatabaseHelper.query(
      _tableName,
      where: 'status = ?',
      whereArgs: [OutboxEventStatus.queued.name],
      orderBy: 'created_at ASC',
    );
    return maps.map((map) => DatabaseOutboxEvent.fromMap(map)).toList();
  }

  Future<List<DatabaseOutboxEvent>> getFailedEvents() async {
    final maps = await DatabaseHelper.query(
      _tableName,
      where: 'status = ?',
      whereArgs: [OutboxEventStatus.failed.name],
      orderBy: 'created_at ASC',
    );
    return maps.map((map) => DatabaseOutboxEvent.fromMap(map)).toList();
  }

  Future<List<DatabaseOutboxEvent>> getEventsByType(OutboxEventType type) async {
    final maps = await DatabaseHelper.query(
      _tableName,
      where: 'type = ?',
      whereArgs: [type.name],
      orderBy: 'created_at ASC',
    );
    return maps.map((map) => DatabaseOutboxEvent.fromMap(map)).toList();
  }

  Future<DatabaseOutboxEvent?> getEventById(String id) async {
    final maps = await DatabaseHelper.query(
      _tableName,
      where: 'id = ?',
      whereArgs: [id],
    );
    if (maps.isEmpty) return null;
    return DatabaseOutboxEvent.fromMap(maps.first);
  }

  Future<void> saveEvent(OutboxEvent event) async {
    final dbEvent = DatabaseOutboxEvent.fromDomain(event);
    await DatabaseHelper.insert(_tableName, dbEvent.toMap());
  }

  Future<void> saveEvents(List<OutboxEvent> events) async {
    for (final event in events) {
      await saveEvent(event);
    }
  }

  Future<void> updateEvent(DatabaseOutboxEvent event) async {
    await DatabaseHelper.update(
      _tableName,
      event.toMap(),
      where: 'id = ?',
      whereArgs: [event.id],
    );
  }

  Future<void> updateEventStatus(String id, OutboxEventStatus status, {String? error}) async {
    final updateData = {
      'status': status.name,
      if (error != null) 'error': error,
    };

    if (status == OutboxEventStatus.sending || status == OutboxEventStatus.failed) {
      updateData['retry_count'] = (await _incrementRetryCount(id)).toString();
    }

    await DatabaseHelper.update(
      _tableName,
      updateData,
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future<int> _incrementRetryCount(String id) async {
    final event = await getEventById(id);
    return (event?.retryCount ?? 0) + 1;
  }

  Future<void> deleteEvent(String id) async {
    await DatabaseHelper.delete(
      _tableName,
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future<void> deleteSentEvents() async {
    await DatabaseHelper.delete(
      _tableName,
      where: 'status = ?',
      whereArgs: [OutboxEventStatus.sent.name],
    );
  }

  Future<void> clearAllEvents() async {
    await DatabaseHelper.delete(_tableName);
  }

  Future<int> getQueuedEventsCount() async {
    final result = await DatabaseHelper.rawQuery(
      'SELECT COUNT(*) as count FROM $_tableName WHERE status = ?',
      [OutboxEventStatus.queued.name],
    );
    return result.first['count'] as int? ?? 0;
  }

  Future<int> getFailedEventsCount() async {
    final result = await DatabaseHelper.rawQuery(
      'SELECT COUNT(*) as count FROM $_tableName WHERE status = ?',
      [OutboxEventStatus.failed.name],
    );
    return result.first['count'] as int? ?? 0;
  }
}
