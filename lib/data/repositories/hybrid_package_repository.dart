import '../services/api_service.dart';
import '../services/sync_service.dart';
import '../models/api_response.dart';
import 'offline_package_repository.dart';
import '../../domain/models/package.dart';

class HybridPackageRepository {
  final OfflinePackageRepository _offlineRepo = OfflinePackageRepository();
  final SyncService _syncService = SyncService();

  // Get packages with offline-first approach
  Future<List<Package>> getPackages({bool forceRefresh = false}) async {
    // Always try to return from local storage first
    final localPackages = await _offlineRepo.getAllPackages();
    
    // If no local data or force refresh, try to sync from server
    if (localPackages.isEmpty || forceRefresh) {
      final syncResult = await _syncService.syncPackagesFromServer();
      if (syncResult.isSuccess) {
        // Return fresh data from local storage after sync
        return await _offlineRepo.getAllPackages();
      }
    }
    
    // Return local data (even if empty)
    return localPackages;
  }

  // Get packages by type
  Future<List<Package>> getPackagesByType(String type) async {
    final localPackages = await _offlineRepo.getPackagesByType(type);
    
    // If no local data for this type, try to sync
    if (localPackages.isEmpty) {
      await _syncService.syncPackagesFromServer();
      return await _offlineRepo.getPackagesByType(type);
    }
    
    return localPackages;
  }

  // Get single package by ID
  Future<Package?> getPackageById(String id) async {
    var package = await _offlineRepo.getPackageById(id);
    
    // If not found locally, try to sync and check again
    if (package == null) {
      await _syncService.syncPackagesFromServer();
      package = await _offlineRepo.getPackageById(id);
    }
    
    return package;
  }

  // Force sync from server
  Future<ApiResponse> syncFromServer() async {
    try {
      final response = await ApiService.getPackages();
      
      if (response.isSuccess) {
        final packagesData = response.data as List;
        final packages = packagesData
            .map((data) => Package.fromJson(data))
            .toList();
        
        await _offlineRepo.savePackages(packages);
        
        // Mark all packages as synced
        for (final package in packages) {
          await _offlineRepo.markPackageAsSynced(package.id);
        }
        
        return ApiResponse.success(packages);
      } else {
        return response;
      }
    } catch (e) {
      return ApiResponse.error('Network error: $e');
    }
  }

  // Check if we have local data
  Future<bool> hasLocalData() async {
    final packages = await _offlineRepo.getAllPackages();
    return packages.isNotEmpty;
  }

  // Get local packages only (for offline scenarios)
  Future<List<Package>> getLocalPackages() async {
    return await _offlineRepo.getAllPackages();
  }

  // Clear all local data
  Future<void> clearLocalData() async {
    await _offlineRepo.clearAllPackages();
  }
}
