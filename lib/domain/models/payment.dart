enum PaymentMethod { cash, qrCode, card }

class Payment {
  final String id;
  final PaymentMethod method;
  final double amount;
  final double? tenderedAmount;
  final double? changeAmount;
  final String? reference;
  final DateTime processedAt;
  final PaymentStatus status;

  const Payment({
    required this.id,
    required this.method,
    required this.amount,
    this.tenderedAmount,
    this.changeAmount,
    this.reference,
    required this.processedAt,
    required this.status,
  });

  String get methodName {
    switch (method) {
      case PaymentMethod.cash:
        return 'Cash';
      case PaymentMethod.qrCode:
        return 'QR Code';
      case PaymentMethod.card:
        return 'Bank Card';
    }
  }

  String get amountText => '฿${amount.toStringAsFixed(0)}';
  String get changeText => changeAmount != null ? '฿${changeAmount!.toStringAsFixed(0)}' : '';
}

enum PaymentStatus { pending, completed, failed, cancelled }
