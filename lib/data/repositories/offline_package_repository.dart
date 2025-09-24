import '../database/database_helper.dart';
import '../models/database_package.dart';
import '../../domain/models/package.dart';

class OfflinePackageRepository {
  static const String _tableName = 'packages';

  Future<List<Package>> getAllPackages() async {
    final maps = await DatabaseHelper.query(
      _tableName,
      orderBy: 'name ASC',
    );
    return maps.map((map) => DatabasePackage.fromMap(map).toDomain()).toList();
  }

  Future<List<Package>> getPackagesByType(String type) async {
    final maps = await DatabaseHelper.query(
      _tableName,
      where: 'type = ?',
      whereArgs: [type],
      orderBy: 'name ASC',
    );
    return maps.map((map) => DatabasePackage.fromMap(map).toDomain()).toList();
  }

  Future<Package?> getPackageById(String id) async {
    final maps = await DatabaseHelper.query(
      _tableName,
      where: 'id = ?',
      whereArgs: [id],
    );
    if (maps.isEmpty) return null;
    return DatabasePackage.fromMap(maps.first).toDomain();
  }

  Future<void> savePackage(Package package) async {
    final dbPackage = DatabasePackage.fromDomain(package);
    await DatabaseHelper.insert(_tableName, dbPackage.toMap());
  }

  Future<void> savePackages(List<Package> packages) async {
    for (final package in packages) {
      await savePackage(package);
    }
  }

  Future<void> updatePackage(Package package) async {
    final dbPackage = DatabasePackage.fromDomain(package).copyWith(
      updatedAt: DateTime.now(),
    );
    await DatabaseHelper.update(
      _tableName,
      dbPackage.toMap(),
      where: 'id = ?',
      whereArgs: [package.id],
    );
  }

  Future<void> deletePackage(String id) async {
    await DatabaseHelper.delete(
      _tableName,
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future<void> markPackageAsSynced(String id) async {
    await DatabaseHelper.update(
      _tableName,
      {'synced_at': DateTime.now().millisecondsSinceEpoch},
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future<List<Package>> getUnsyncedPackages() async {
    final maps = await DatabaseHelper.query(
      _tableName,
      where: 'synced_at IS NULL',
      orderBy: 'created_at ASC',
    );
    return maps.map((map) => DatabasePackage.fromMap(map).toDomain()).toList();
  }

  Future<void> clearAllPackages() async {
    await DatabaseHelper.delete(_tableName);
  }
}
