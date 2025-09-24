import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../data/services/sync_service.dart';

final syncServiceProvider = Provider<SyncService>((ref) {
  return SyncService();
});

final syncStatusProvider = FutureProvider<SyncStatus>((ref) async {
  final syncService = ref.read(syncServiceProvider);
  return await syncService.getSyncStatus();
});

final syncInProgressProvider = StateProvider<bool>((ref) => false);

final syncProvider = StateNotifierProvider<SyncNotifier, SyncState>((ref) {
  return SyncNotifier(ref.read(syncServiceProvider));
});

class SyncNotifier extends StateNotifier<SyncState> {
  final SyncService _syncService;

  SyncNotifier(this._syncService) : super(const SyncState.idle());

  Future<void> syncPackagesFromServer() async {
    state = const SyncState.loading('Syncing packages from server...');
    
    try {
      final result = await _syncService.syncPackagesFromServer();
      
      if (result.isSuccess) {
        state = SyncState.success(result.message);
      } else {
        state = SyncState.error(result.message);
      }
    } catch (e) {
      state = SyncState.error('Error syncing packages: $e');
    }
  }

  Future<void> syncLocalDataToServer() async {
    state = const SyncState.loading('Syncing local data to server...');
    
    try {
      final result = await _syncService.syncLocalDataToServer();
      
      if (result.isSuccess) {
        state = SyncState.success(result.message);
      } else {
        state = SyncState.error(result.message);
      }
    } catch (e) {
      state = SyncState.error('Error syncing to server: $e');
    }
  }

  Future<void> retryFailedEvents() async {
    state = const SyncState.loading('Retrying failed events...');
    
    try {
      final result = await _syncService.retryFailedEvents();
      
      if (result.isSuccess) {
        state = SyncState.success(result.message);
      } else {
        state = SyncState.error(result.message);
      }
    } catch (e) {
      state = SyncState.error('Error retrying failed events: $e');
    }
  }

  Future<void> fullSync() async {
    state = const SyncState.loading('Performing full sync...');
    
    try {
      // Sync packages from server first
      final packagesResult = await _syncService.syncPackagesFromServer();
      if (!packagesResult.isSuccess) {
        state = SyncState.error('Failed to sync packages: ${packagesResult.message}');
        return;
      }
      
      // Then sync local data to server
      final localResult = await _syncService.syncLocalDataToServer();
      if (!localResult.isSuccess) {
        state = SyncState.error('Failed to sync local data: ${localResult.message}');
        return;
      }
      
      state = const SyncState.success('Full sync completed successfully');
    } catch (e) {
      state = SyncState.error('Error during full sync: $e');
    }
  }

  void clearState() {
    state = const SyncState.idle();
  }
}

class SyncState {
  final SyncStatusType type;
  final String message;

  const SyncState._(this.type, this.message);

  const SyncState.idle() : this._(SyncStatusType.idle, '');
  
  const SyncState.loading(String message) : this._(SyncStatusType.loading, message);
  
  const SyncState.success(String message) : this._(SyncStatusType.success, message);
  
  const SyncState.error(String message) : this._(SyncStatusType.error, message);

  bool get isLoading => type == SyncStatusType.loading;
  bool get isSuccess => type == SyncStatusType.success;
  bool get isError => type == SyncStatusType.error;
  bool get isIdle => type == SyncStatusType.idle;
}

enum SyncStatusType {
  idle,
  loading,
  success,
  error,
}
