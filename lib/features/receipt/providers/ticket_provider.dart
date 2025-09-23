import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../../../domain/models/ticket.dart';
import '../../../domain/models/cart.dart';
import '../../../domain/models/cart_line.dart';
import '../../../domain/models/package.dart';

final issuedTicketsProvider = FutureProvider<List<Ticket>>((ref) async {
  // In a real app, this would fetch from a repository
  // For now, return empty list - tickets are generated during checkout
  return [];
});

final ticketGeneratorProvider = Provider<TicketGenerator>((ref) {
  return TicketGenerator();
});

class TicketGenerator {
  List<Ticket> generateTicketsFromCart(Cart cart) {
    final tickets = <Ticket>[];
    final now = DateTime.now();
    final lotNo = _generateLotNumber();
    final shiftId = _generateShiftId();

    for (final line in cart.lines) {
      // Generate one ticket per quantity for single/multi types
      // Generate one ticket with total minutes for timepass types
      if (line.package.type == 'timepass') {
        final totalMinutes = line.package.quotaOrMinutes! * line.qty;
        final ticket = _createTicket(
          package: line.package,
          quotaOrMinutes: totalMinutes,
          lotNo: lotNo,
          shiftId: shiftId,
          issuedAt: now,
        );
        tickets.add(ticket);
      } else {
        // Generate separate tickets for each quantity
        for (int i = 0; i < line.qty; i++) {
          final ticket = _createTicket(
            package: line.package,
            quotaOrMinutes: line.package.quotaOrMinutes ?? 1,
            lotNo: lotNo,
            shiftId: shiftId,
            issuedAt: now,
          );
          tickets.add(ticket);
        }
      }
    }

    return tickets;
  }

  Ticket _createTicket({
    required Package package,
    required int quotaOrMinutes,
    required String lotNo,
    required String shiftId,
    required DateTime issuedAt,
  }) {
    final id = _generateTicketId();
    final shortCode = _generateShortCode();
    final token = _generateToken();
    final signature = _generateSignature(id, token); // Mock signature
    
    // Calculate validity based on package type
    final (validFrom, validTo) = _calculateValidity(package.type, issuedAt);
    
    final ticketType = _mapPackageTypeToTicketType(package.type);
    
    final qrPayload = _generateQrPayload({
      'v': 1,
      'tid': id,
      't': token,
      's': signature,
      'lf': lotNo,
      'tp': package.type,
      'valid_from': validFrom.millisecondsSinceEpoch,
      'valid_to': validTo.millisecondsSinceEpoch,
      'quota_or_minutes': quotaOrMinutes,
    });

    return Ticket(
      id: id,
      shortCode: shortCode,
      qrPayload: qrPayload,
      type: ticketType,
      quotaOrMinutes: quotaOrMinutes,
      validFrom: validFrom,
      validTo: validTo,
      lotNo: lotNo,
      shiftId: shiftId,
      issuedAt: issuedAt,
      price: package.price,
      token: token,
      signature: signature,
    );
  }

  String _generateTicketId() {
    return 'TKT-${DateTime.now().millisecondsSinceEpoch}';
  }

  String _generateShortCode() {
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'; // Exclude confusing chars
    final random = DateTime.now().millisecondsSinceEpoch;
    final code = <String>[];
    
    for (int i = 0; i < 6; i++) {
      code.add(chars[(random + i) % chars.length]);
    }
    
    return '${code.take(3).join()}-${code.skip(3).take(3).join()}';
  }

  String _generateToken() {
    return DateTime.now().millisecondsSinceEpoch.toRadixString(36);
  }

  String _generateSignature(String id, String token) {
    // Mock signature - in real app this would be HMAC
    return 'MOCK_SIG_${id.substring(0, 8)}_${token.substring(0, 8)}';
  }

  String _generateLotNumber() {
    return 'LOT-${DateTime.now().millisecondsSinceEpoch.toString().substring(8)}';
  }

  String _generateShiftId() {
    return 'SHIFT-${DateTime.now().millisecondsSinceEpoch.toString().substring(8)}';
  }

  (DateTime, DateTime) _calculateValidity(String packageType, DateTime issuedAt) {
    switch (packageType) {
      case 'single':
        return (issuedAt, issuedAt.add(const Duration(days: 1)));
      case 'multi':
        return (issuedAt, issuedAt.add(const Duration(days: 30)));
      case 'timepass':
        return (issuedAt, issuedAt.add(const Duration(hours: 8)));
      case 'credit':
        return (issuedAt, issuedAt.add(const Duration(days: 365)));
      default:
        return (issuedAt, issuedAt.add(const Duration(days: 1)));
    }
  }

  TicketType _mapPackageTypeToTicketType(String packageType) {
    switch (packageType) {
      case 'single':
        return TicketType.single;
      case 'multi':
        return TicketType.multi;
      case 'timepass':
        return TicketType.timepass;
      case 'credit':
        return TicketType.credit;
      default:
        return TicketType.single;
    }
  }

  String _generateQrPayload(Map<String, dynamic> data) {
    // Convert to compact JSON-like string
    return data.entries
        .map((e) => '${e.key}:${e.value}')
        .join('|');
  }
}
