import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:uuid/uuid.dart';

import '../repositories/offline_package_repository.dart';
import '../repositories/offline_ticket_repository.dart';
import '../repositories/offline_sale_repository.dart';
import '../repositories/offline_outbox_repository.dart';
import '../models/database_outbox_event.dart';
import '../models/database_sale.dart' as db;
import '../models/sale_request.dart';
import '../models/ticket_redemption_request.dart';
import '../../domain/models/package.dart';
import '../../domain/models/ticket.dart';
import '../../domain/models/outbox_event.dart';
import 'api_service.dart';

class SyncService {
  static const _uuid = Uuid();

  final OfflinePackageRepository _packageRepo = OfflinePackageRepository();
  final OfflineTicketRepository _ticketRepo = OfflineTicketRepository();
  final OfflineSaleRepository _saleRepo = OfflineSaleRepository();
  final OfflineOutboxRepository _outboxRepo = OfflineOutboxRepository();

  // Sync packages from server to local database
  Future<SyncResult> syncPackagesFromServer() async {
    // On web, return success without database operations
    if (kIsWeb) {
      return SyncResult.success('Web mode: Using mock data');
    }

    try {
      final response = await ApiService.getPackages();

      if (response.isSuccess) {
        final packagesData = response.data as List;
        final packages =
            packagesData.map((data) => Package.fromJson(data)).toList();

        await _packageRepo.savePackages(packages);

        // Mark all packages as synced
        for (final package in packages) {
          await _packageRepo.markPackageAsSynced(package.id);
        }

        return SyncResult.success('Synced ${packages.length} packages');
      } else {
        return SyncResult.error('Failed to fetch packages: ${response.error}');
      }
    } catch (e) {
      return SyncResult.error('Error syncing packages: $e');
    }
  }

  // Sync local data to server
  Future<SyncResult> syncLocalDataToServer() async {
    try {
      final results = <String>[];

      // Process outbox events
      final outboxResult = await _processOutboxEvents();
      results.addAll(outboxResult);

      return SyncResult.success('Sync completed: ${results.join(', ')}');
    } catch (e) {
      return SyncResult.error('Error syncing to server: $e');
    }
  }

  Future<List<String>> _processOutboxEvents() async {
    final results = <String>[];
    final queuedEvents = await _outboxRepo.getQueuedEvents();

    for (final event in queuedEvents) {
      try {
        // Mark as sending
        await _outboxRepo.updateEventStatus(
            event.id, OutboxEventStatus.sending);

        bool success = false;
        String? errorMessage;

        switch (event.type) {
          case OutboxEventType.sale:
            success = await _processSaleEvent(event);
            break;
          case OutboxEventType.redemption:
            success = await _processRedemptionEvent(event);
            break;
          case OutboxEventType.reprint:
            success = await _processReprintEvent(event);
            break;
          case OutboxEventType.refund:
            success = await _processRefundEvent(event);
            break;
        }

        if (success) {
          await _outboxRepo.updateEventStatus(event.id, OutboxEventStatus.sent);
          results.add('${event.type.name}: Success');
        } else {
          await _outboxRepo.updateEventStatus(
            event.id,
            OutboxEventStatus.failed,
            error: errorMessage ?? 'Unknown error',
          );
          results.add('${event.type.name}: Failed');
        }
      } catch (e) {
        await _outboxRepo.updateEventStatus(
          event.id,
          OutboxEventStatus.failed,
          error: e.toString(),
        );
        results.add('${event.type.name}: Error - $e');
      }
    }

    return results;
  }

  Future<bool> _processSaleEvent(DatabaseOutboxEvent event) async {
    try {
      final saleData = event.payload;
      final saleRequest = SaleRequest(
        deviceId: saleData['device_id'] ?? '',
        cashierId: saleData['cashier_id'] ?? '',
        items: (saleData['items'] as List<dynamic>?)
                ?.map((item) => SaleItem(
                      packageId: item['package_id'] ?? '',
                      quantity: (item['quantity'] ?? 1).toInt(),
                      price: (item['unit_price'] ?? 0.0).toDouble(),
                    ))
                .toList() ??
            [],
        subtotal: (saleData['subtotal'] ?? 0.0).toDouble(),
        discountTotal: (saleData['discount_total'] ?? 0.0).toDouble(),
        taxTotal: (saleData['tax_total'] ?? 0.0).toDouble(),
        grandTotal: (saleData['grand_total'] ?? 0.0).toDouble(),
        paymentMethod: saleData['payment_method'] ?? 'cash',
        amountTendered: (saleData['amount_tendered'] ?? 0.0).toDouble(),
        change: (saleData['change'] ?? 0.0).toDouble(),
        idempotencyKey: saleData['idempotency_key'],
      );
      final response = await ApiService.createSale(saleRequest);

      if (response.isSuccess) {
        // Mark sale as synced
        final saleId = saleData['id'] as String?;
        if (saleId != null) {
          await _saleRepo.markSaleAsSynced(saleId);
        }
        return true;
      }
      return false;
    } catch (e) {
      return false;
    }
  }

  Future<bool> _processRedemptionEvent(DatabaseOutboxEvent event) async {
    try {
      final redemptionData = event.payload;
      final redemptionRequest = TicketRedemptionRequest(
        qrToken: redemptionData['qr_token'] ?? '',
        deviceId: redemptionData['device_id'] ?? '',
      );
      final response = await ApiService.redeemTicket(redemptionRequest);
      return response.isSuccess;
    } catch (e) {
      return false;
    }
  }

  Future<bool> _processReprintEvent(DatabaseOutboxEvent event) async {
    // Reprint events are typically just logged, no server call needed
    return true;
  }

  Future<bool> _processRefundEvent(DatabaseOutboxEvent event) async {
    // Implement refund API call when available
    return true;
  }

  // Add sale to outbox for later sync
  Future<void> queueSale(db.DatabaseSale sale) async {
    final event = OutboxEvent(
      id: _uuid.v4(),
      type: OutboxEventType.sale,
      payload: sale.toMap(),
      timestamp: DateTime.now(),
    );

    await _outboxRepo.saveEvent(event);
  }

  // Add redemption to outbox for later sync
  Future<void> queueRedemption(Map<String, dynamic> redemptionData) async {
    final event = OutboxEvent(
      id: _uuid.v4(),
      type: OutboxEventType.redemption,
      payload: redemptionData,
      timestamp: DateTime.now(),
    );

    await _outboxRepo.saveEvent(event);
  }

  // Add reprint to outbox for later sync
  Future<void> queueReprint(Map<String, dynamic> reprintData) async {
    final event = OutboxEvent(
      id: _uuid.v4(),
      type: OutboxEventType.reprint,
      payload: reprintData,
      timestamp: DateTime.now(),
    );

    await _outboxRepo.saveEvent(event);
  }

  // Add refund to outbox for later sync
  Future<void> queueRefund(Map<String, dynamic> refundData) async {
    final event = OutboxEvent(
      id: _uuid.v4(),
      type: OutboxEventType.refund,
      payload: refundData,
      timestamp: DateTime.now(),
    );

    await _outboxRepo.saveEvent(event);
  }

  // Check sync status
  Future<SyncStatus> getSyncStatus() async {
    // On web, return empty sync status to avoid database errors
    if (kIsWeb) {
      return const SyncStatus(
        queuedEvents: 0,
        failedEvents: 0,
        unsyncedPackages: 0,
        unsyncedTickets: 0,
        unsyncedSales: 0,
      );
    }

    final queuedCount = await _outboxRepo.getQueuedEventsCount();
    final failedCount = await _outboxRepo.getFailedEventsCount();
    final unsyncedPackages = await _packageRepo.getUnsyncedPackages();
    final unsyncedTickets = await _ticketRepo.getUnsyncedTickets();
    final unsyncedSales = await _saleRepo.getUnsyncedSales();

    return SyncStatus(
      queuedEvents: queuedCount,
      failedEvents: failedCount,
      unsyncedPackages: unsyncedPackages.length,
      unsyncedTickets: unsyncedTickets.length,
      unsyncedSales: unsyncedSales.length,
    );
  }

  // Retry failed events
  Future<SyncResult> retryFailedEvents() async {
    try {
      final failedEvents = await _outboxRepo.getFailedEvents();
      final results = <String>[];

      for (final event in failedEvents) {
        // Reset status to queued for retry
        await _outboxRepo.updateEventStatus(event.id, OutboxEventStatus.queued);
        results.add('Retrying ${event.type.name}');
      }

      // Process the retried events
      final retryResults = await _processOutboxEvents();
      results.addAll(retryResults);

      return SyncResult.success('Retry completed: ${results.join(', ')}');
    } catch (e) {
      return SyncResult.error('Error retrying failed events: $e');
    }
  }

  // Clear old synced data
  Future<void> cleanupOldData() async {
    // Delete sent outbox events older than 7 days
    await _outboxRepo.deleteSentEvents();

    // You can add more cleanup logic here
  }
}

class SyncResult {
  final bool isSuccess;
  final String message;

  const SyncResult._(this.isSuccess, this.message);

  factory SyncResult.success(String message) => SyncResult._(true, message);
  factory SyncResult.error(String message) => SyncResult._(false, message);
}

class SyncStatus {
  final int queuedEvents;
  final int failedEvents;
  final int unsyncedPackages;
  final int unsyncedTickets;
  final int unsyncedSales;

  const SyncStatus({
    required this.queuedEvents,
    required this.failedEvents,
    required this.unsyncedPackages,
    required this.unsyncedTickets,
    required this.unsyncedSales,
  });

  bool get hasUnsyncedData =>
      queuedEvents > 0 ||
      failedEvents > 0 ||
      unsyncedPackages > 0 ||
      unsyncedTickets > 0 ||
      unsyncedSales > 0;

  int get totalUnsynced =>
      queuedEvents +
      failedEvents +
      unsyncedPackages +
      unsyncedTickets +
      unsyncedSales;
}
