import 'package:flutter/foundation.dart';
import '../../domain/models/package.dart';
import '../services/api_service.dart';
import 'hybrid_package_repository.dart';

class PackageRepository {
  final HybridPackageRepository _hybridRepo = HybridPackageRepository();

  Future<List<Package>> getAllPackages(
      {String? storeId, bool forceRefresh = false}) async {
    // On web, always use mock data to avoid SQLite issues
    if (kIsWeb) {
      return _getMockPackages();
    }

    // Try to get from hybrid repository (offline-first with sync)
    final packages = await _hybridRepo.getPackages(forceRefresh: forceRefresh);

    if (packages.isNotEmpty) {
      return packages;
    }

    // Fallback to mock data if no data available
    return _getMockPackages();
  }

  Future<Package?> getPackageById(String id) async {
    // On web, use mock data to avoid SQLite issues
    if (kIsWeb) {
      final mockPackages = _getMockPackages();
      try {
        return mockPackages.firstWhere((p) => p.id == id);
      } catch (e) {
        return null;
      }
    }

    final package = await _hybridRepo.getPackageById(id);

    if (package != null) {
      return package;
    }

    // Fallback to mock data
    final mockPackages = _getMockPackages();
    try {
      return mockPackages.firstWhere((p) => p.id == id);
    } catch (e) {
      return null;
    }
  }

  Future<List<Package>> getPackagesByType(String type) async {
    // On web, use mock data to avoid SQLite issues
    if (kIsWeb) {
      return _getMockPackages().where((p) => p.type == type).toList();
    }

    return await _hybridRepo.getPackagesByType(type);
  }

  // Force sync from server
  Future<void> syncFromServer() async {
    await _hybridRepo.syncFromServer();
  }

  // Check if we have local data
  Future<bool> hasLocalData() async {
    return await _hybridRepo.hasLocalData();
  }

  // Get local packages only (for offline scenarios)
  Future<List<Package>> getLocalPackages() async {
    return await _hybridRepo.getLocalPackages();
  }

  // Fallback mock data
  List<Package> _getMockPackages() {
    return [
      const Package(
          id: '1',
          name: 'Day Pass',
          price: 350,
          type: 'timepass',
          quotaOrMinutes: 480),
      const Package(
          id: '2',
          name: 'Multi 5',
          price: 1200,
          type: 'multi',
          quotaOrMinutes: 5),
      const Package(
          id: '3',
          name: 'Single',
          price: 250,
          type: 'single',
          quotaOrMinutes: 1),
      const Package(
          id: '4',
          name: 'Adult + Kid',
          price: 500,
          type: 'bundle',
          quotaOrMinutes: 2),
      const Package(
          id: '5',
          name: 'Credit 1000',
          price: 1000,
          type: 'credit',
          quotaOrMinutes: 1000),
      const Package(
          id: '6',
          name: 'Evening',
          price: 180,
          type: 'timepass',
          quotaOrMinutes: 240),
    ];
  }
}
