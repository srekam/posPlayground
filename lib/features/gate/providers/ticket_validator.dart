import '../../../domain/models/ticket.dart';
import '../../../domain/models/redemption.dart';

class TicketValidator {
  static final Map<String, List<Redemption>> _redemptionHistory = {};
  static final Map<String, int> _quotaUsage = {};

  ValidationResult validateTicket(String qrPayload, String deviceId) {
    try {
      // Parse QR payload
      final ticketData = _parseQrPayload(qrPayload);
      final ticketId = ticketData['tid'] as String?;
      
      if (ticketId == null) {
        return ValidationResult.fail(RedemptionReason.invalidSignature);
      }

      // Check if ticket exists in our mock store
      final ticket = _getTicketFromMockStore(ticketId);
      if (ticket == null) {
        return ValidationResult.fail(RedemptionReason.invalidSignature);
      }

      // Check validity period
      final now = DateTime.now();
      if (now.isBefore(ticket.validFrom)) {
        return ValidationResult.fail(RedemptionReason.notStarted);
      }
      
      if (now.isAfter(ticket.validTo)) {
        return ValidationResult.fail(RedemptionReason.expired);
      }

      // Check quota usage
      final currentUsage = _quotaUsage[ticketId] ?? 0;
      final maxQuota = ticket.quotaOrMinutes;
      
      if (ticket.type == TicketType.single || ticket.type == TicketType.multi) {
        // For single/multi tickets, check usage count
        if (currentUsage >= maxQuota) {
          return ValidationResult.fail(RedemptionReason.quotaExhausted);
        }
      }

      // Check for duplicate use in recent history (within 5 minutes)
      final recentRedemptions = _getRecentRedemptions(ticketId, Duration(minutes: 5));
      if (recentRedemptions.any((r) => r.status == RedemptionStatus.pass)) {
        return ValidationResult.fail(RedemptionReason.duplicateUse);
      }

      // If all checks pass, record the redemption
      final redemption = Redemption(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        ticketId: ticketId,
        deviceId: deviceId,
        timestamp: now,
        status: RedemptionStatus.pass,
        remainingQuotaOrTime: _calculateRemaining(ticket, currentUsage),
      );

      _recordRedemption(redemption);
      _incrementUsage(ticketId);

      return ValidationResult.pass(redemption.remainingQuotaOrTime);
      
    } catch (e) {
      return ValidationResult.fail(RedemptionReason.invalidSignature);
    }
  }

  Map<String, dynamic> _parseQrPayload(String payload) {
    // Parse the compact format: "v:1|tid:TKT-123|t:token|s:sig|lf:lot|tp:type|valid_from:123|valid_to:456|quota_or_minutes:5"
    final parts = payload.split('|');
    final result = <String, dynamic>{};
    
    for (final part in parts) {
      final keyValue = part.split(':');
      if (keyValue.length == 2) {
        final key = keyValue[0];
        final value = keyValue[1];
        
        // Parse numeric values
        if (key == 'v' || key == 'quota_or_minutes') {
          result[key] = int.tryParse(value);
        } else if (key == 'valid_from' || key == 'valid_to') {
          result[key] = int.tryParse(value);
        } else {
          result[key] = value;
        }
      }
    }
    
    return result;
  }

  Ticket? _getTicketFromMockStore(String ticketId) {
    // Mock ticket store - in real app this would query a database
    final now = DateTime.now();
    return Ticket(
      id: ticketId,
      shortCode: 'ABC-123',
      qrPayload: '', // Not needed for validation
      type: TicketType.multi,
      quotaOrMinutes: 5,
      validFrom: now.subtract(const Duration(hours: 1)),
      validTo: now.add(const Duration(hours: 23)),
      lotNo: 'LOT-001',
      shiftId: 'SHIFT-001',
      issuedAt: now.subtract(const Duration(hours: 1)),
      price: 250.0,
      token: 'mock_token',
      signature: 'mock_signature',
    );
  }

  List<Redemption> _getRecentRedemptions(String ticketId, Duration window) {
    final cutoff = DateTime.now().subtract(window);
    return _redemptionHistory[ticketId]?.where((r) => r.timestamp.isAfter(cutoff)).toList() ?? [];
  }

  void _recordRedemption(Redemption redemption) {
    _redemptionHistory.putIfAbsent(redemption.ticketId, () => []).add(redemption);
  }

  void _incrementUsage(String ticketId) {
    _quotaUsage[ticketId] = (_quotaUsage[ticketId] ?? 0) + 1;
  }

  int? _calculateRemaining(Ticket ticket, int currentUsage) {
    switch (ticket.type) {
      case TicketType.single:
        return 0; // Single use tickets have no remaining
      case TicketType.multi:
        return (ticket.quotaOrMinutes - currentUsage - 1).clamp(0, ticket.quotaOrMinutes);
      case TicketType.timepass:
        // For timepass, return remaining minutes (simplified calculation)
        final elapsed = DateTime.now().difference(ticket.issuedAt).inMinutes;
        return (ticket.quotaOrMinutes - elapsed).clamp(0, ticket.quotaOrMinutes);
      case TicketType.credit:
        return ticket.quotaOrMinutes; // Credits don't decrease on redemption
    }
  }

  // Get redemption history for a ticket
  List<Redemption> getRedemptionHistory(String ticketId) {
    return _redemptionHistory[ticketId] ?? [];
  }

  // Get current usage for a ticket
  int getCurrentUsage(String ticketId) {
    return _quotaUsage[ticketId] ?? 0;
  }
}

class ValidationResult {
  final RedemptionStatus status;
  final RedemptionReason? reason;
  final int? remainingQuotaOrTime;

  const ValidationResult._({
    required this.status,
    this.reason,
    this.remainingQuotaOrTime,
  });

  factory ValidationResult.pass(int? remaining) {
    return ValidationResult._(
      status: RedemptionStatus.pass,
      remainingQuotaOrTime: remaining,
    );
  }

  factory ValidationResult.fail(RedemptionReason reason) {
    return ValidationResult._(
      status: RedemptionStatus.fail,
      reason: reason,
    );
  }

  bool get isPass => status == RedemptionStatus.pass;
  bool get isFail => status == RedemptionStatus.fail;
}
