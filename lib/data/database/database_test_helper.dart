import 'database_helper.dart';
import '../models/database_package.dart';
import '../../domain/models/package.dart';

class DatabaseTestHelper {
  // Test data for offline functionality
  static const List<Map<String, dynamic>> _testPackages = [
    {
      'id': 'test_1',
      'name': 'Test Day Pass',
      'price': 350.0,
      'type': 'timepass',
      'quota_or_minutes': 480,
      'allowed_devices': null,
    },
    {
      'id': 'test_2',
      'name': 'Test Single Entry',
      'price': 250.0,
      'type': 'single',
      'quota_or_minutes': 1,
      'allowed_devices': null,
    },
    {
      'id': 'test_3',
      'name': 'Test Multi 5',
      'price': 1200.0,
      'type': 'multi',
      'quota_or_minutes': 5,
      'allowed_devices': null,
    },
  ];

  // Populate database with test data
  static Future<void> populateTestData() async {
    final db = await DatabaseHelper.database;
    
    // Clear existing data
    await db.delete('packages');
    
    // Insert test packages
    for (final packageData in _testPackages) {
      final package = DatabasePackage.fromMap({
        ...packageData,
        'created_at': DateTime.now().millisecondsSinceEpoch,
        'updated_at': DateTime.now().millisecondsSinceEpoch,
        'synced_at': null, // Mark as unsynced for testing
      });
      
      await DatabaseHelper.insert('packages', package.toMap());
    }
  }

  // Create test package
  static Package createTestPackage({
    String id = 'test_package',
    String name = 'Test Package',
    double price = 100.0,
    String type = 'single',
    int? quotaOrMinutes,
  }) {
    return Package(
      id: id,
      name: name,
      price: price,
      type: type,
      quotaOrMinutes: quotaOrMinutes,
    );
  }

  // Get database statistics
  static Future<Map<String, int>> getDatabaseStats() async {
    final stats = <String, int>{};
    final tables = ['packages', 'tickets', 'sales', 'outbox_events'];
    
    for (final table in tables) {
      final result = await DatabaseHelper.rawQuery('SELECT COUNT(*) as count FROM $table');
      stats[table] = result.first['count'] as int;
    }
    
    return stats;
  }

  // Clear all test data
  static Future<void> clearTestData() async {
    await DatabaseHelper.clearDatabase();
  }

  // Check if database is properly initialized
  static Future<bool> isDatabaseInitialized() async {
    try {
      final db = await DatabaseHelper.database;
      final result = await db.rawQuery('SELECT name FROM sqlite_master WHERE type="table"');
      return result.length >= 4; // Should have at least 4 tables
    } catch (e) {
      return false;
    }
  }
}
