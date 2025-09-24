import '../database/database_helper.dart';
import '../models/database_sale.dart';

class OfflineSaleRepository {
  static const String _tableName = 'sales';

  Future<List<DatabaseSale>> getAllSales() async {
    final maps = await DatabaseHelper.query(
      _tableName,
      orderBy: 'created_at DESC',
    );
    return maps.map((map) => DatabaseSale.fromMap(map)).toList();
  }

  Future<List<DatabaseSale>> getSalesByShift(String shiftId) async {
    final maps = await DatabaseHelper.query(
      _tableName,
      where: 'shift_id = ?',
      whereArgs: [shiftId],
      orderBy: 'created_at DESC',
    );
    return maps.map((map) => DatabaseSale.fromMap(map)).toList();
  }

  Future<DatabaseSale?> getSaleById(String id) async {
    final maps = await DatabaseHelper.query(
      _tableName,
      where: 'id = ?',
      whereArgs: [id],
    );
    if (maps.isEmpty) return null;
    return DatabaseSale.fromMap(maps.first);
  }

  Future<void> saveSale(DatabaseSale sale) async {
    await DatabaseHelper.insert(_tableName, sale.toMap());
  }

  Future<void> updateSale(DatabaseSale sale) async {
    final updatedSale = sale.copyWith(updatedAt: DateTime.now());
    await DatabaseHelper.update(
      _tableName,
      updatedSale.toMap(),
      where: 'id = ?',
      whereArgs: [sale.id],
    );
  }

  Future<void> deleteSale(String id) async {
    await DatabaseHelper.delete(
      _tableName,
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future<void> markSaleAsSynced(String id) async {
    await DatabaseHelper.update(
      _tableName,
      {'synced_at': DateTime.now().millisecondsSinceEpoch},
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future<List<DatabaseSale>> getUnsyncedSales() async {
    final maps = await DatabaseHelper.query(
      _tableName,
      where: 'synced_at IS NULL',
      orderBy: 'created_at ASC',
    );
    return maps.map((map) => DatabaseSale.fromMap(map)).toList();
  }

  Future<double> getTotalSalesByShift(String shiftId) async {
    final result = await DatabaseHelper.rawQuery(
      'SELECT SUM(total_amount) as total FROM $_tableName WHERE shift_id = ?',
      [shiftId],
    );
    return (result.first['total'] as num?)?.toDouble() ?? 0.0;
  }

  Future<int> getSaleCountByShift(String shiftId) async {
    final result = await DatabaseHelper.rawQuery(
      'SELECT COUNT(*) as count FROM $_tableName WHERE shift_id = ?',
      [shiftId],
    );
    return result.first['count'] as int? ?? 0;
  }

  Future<Map<String, double>> getSalesByPaymentMethod(String shiftId) async {
    final maps = await DatabaseHelper.rawQuery(
      'SELECT payment_method, SUM(total_amount) as total FROM $_tableName WHERE shift_id = ? GROUP BY payment_method',
      [shiftId],
    );
    
    final result = <String, double>{};
    for (final map in maps) {
      result[map['payment_method'] as String] = (map['total'] as num).toDouble();
    }
    return result;
  }

  Future<void> clearAllSales() async {
    await DatabaseHelper.delete(_tableName);
  }
}
