import '../database/database_helper.dart';
import '../models/database_ticket.dart';
import '../../domain/models/ticket.dart';

class OfflineTicketRepository {
  static const String _tableName = 'tickets';

  Future<List<Ticket>> getAllTickets() async {
    final maps = await DatabaseHelper.query(
      _tableName,
      orderBy: 'issued_at DESC',
    );
    return maps.map((map) => DatabaseTicket.fromMap(map).toDomain()).toList();
  }

  Future<List<Ticket>> getTicketsByShift(String shiftId) async {
    final maps = await DatabaseHelper.query(
      _tableName,
      where: 'shift_id = ?',
      whereArgs: [shiftId],
      orderBy: 'issued_at DESC',
    );
    return maps.map((map) => DatabaseTicket.fromMap(map).toDomain()).toList();
  }

  Future<List<Ticket>> getTicketsByStatus(TicketStatus status) async {
    final maps = await DatabaseHelper.query(
      _tableName,
      where: 'status = ?',
      whereArgs: [status.name],
      orderBy: 'issued_at DESC',
    );
    return maps.map((map) => DatabaseTicket.fromMap(map).toDomain()).toList();
  }

  Future<Ticket?> getTicketById(String id) async {
    final maps = await DatabaseHelper.query(
      _tableName,
      where: 'id = ?',
      whereArgs: [id],
    );
    if (maps.isEmpty) return null;
    return DatabaseTicket.fromMap(maps.first).toDomain();
  }

  Future<Ticket?> getTicketByShortCode(String shortCode) async {
    final maps = await DatabaseHelper.query(
      _tableName,
      where: 'short_code = ?',
      whereArgs: [shortCode],
    );
    if (maps.isEmpty) return null;
    return DatabaseTicket.fromMap(maps.first).toDomain();
  }

  Future<void> saveTicket(Ticket ticket) async {
    final dbTicket = DatabaseTicket.fromDomain(ticket);
    await DatabaseHelper.insert(_tableName, dbTicket.toMap());
  }

  Future<void> saveTickets(List<Ticket> tickets) async {
    for (final ticket in tickets) {
      await saveTicket(ticket);
    }
  }

  Future<void> updateTicket(Ticket ticket) async {
    final dbTicket = DatabaseTicket.fromDomain(ticket).copyWith(
      updatedAt: DateTime.now(),
    );
    await DatabaseHelper.update(
      _tableName,
      dbTicket.toMap(),
      where: 'id = ?',
      whereArgs: [ticket.id],
    );
  }

  Future<void> updateTicketStatus(String id, TicketStatus status) async {
    await DatabaseHelper.update(
      _tableName,
      {
        'status': status.name,
        'updated_at': DateTime.now().millisecondsSinceEpoch,
      },
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future<void> deleteTicket(String id) async {
    await DatabaseHelper.delete(
      _tableName,
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future<void> markTicketAsSynced(String id) async {
    await DatabaseHelper.update(
      _tableName,
      {'synced_at': DateTime.now().millisecondsSinceEpoch},
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future<List<Ticket>> getUnsyncedTickets() async {
    final maps = await DatabaseHelper.query(
      _tableName,
      where: 'synced_at IS NULL',
      orderBy: 'created_at ASC',
    );
    return maps.map((map) => DatabaseTicket.fromMap(map).toDomain()).toList();
  }

  Future<List<Ticket>> getActiveTickets() async {
    final maps = await DatabaseHelper.query(
      _tableName,
      where: 'status = ? AND valid_from <= ? AND valid_to >= ?',
      whereArgs: [
        TicketStatus.active.name,
        DateTime.now().millisecondsSinceEpoch,
        DateTime.now().millisecondsSinceEpoch,
      ],
      orderBy: 'issued_at DESC',
    );
    return maps.map((map) => DatabaseTicket.fromMap(map).toDomain()).toList();
  }

  Future<List<Ticket>> getExpiredTickets() async {
    final maps = await DatabaseHelper.query(
      _tableName,
      where: 'valid_to < ?',
      whereArgs: [DateTime.now().millisecondsSinceEpoch],
      orderBy: 'valid_to DESC',
    );
    return maps.map((map) => DatabaseTicket.fromMap(map).toDomain()).toList();
  }

  Future<void> clearAllTickets() async {
    await DatabaseHelper.delete(_tableName);
  }
}
