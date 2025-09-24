class SaleRequest {
  final String deviceId;
  final String cashierId;
  final List<SaleItem> items;
  final double subtotal;
  final double discountTotal;
  final double taxTotal;
  final double grandTotal;
  final String paymentMethod;
  final double amountTendered;
  final double change;
  final String? idempotencyKey;

  SaleRequest({
    required this.deviceId,
    required this.cashierId,
    required this.items,
    required this.subtotal,
    required this.discountTotal,
    required this.taxTotal,
    required this.grandTotal,
    required this.paymentMethod,
    required this.amountTendered,
    required this.change,
    this.idempotencyKey,
  });

  Map<String, dynamic> toJson() => {
    'device_id': deviceId,
    'cashier_id': cashierId,
    'items': items.map((item) => item.toJson()).toList(),
    'subtotal': subtotal,
    'discount_total': discountTotal,
    'tax_total': taxTotal,
    'grand_total': grandTotal,
    'payment_method': paymentMethod,
    'amount_tendered': amountTendered,
    'change': change,
    if (idempotencyKey != null) 'idempotency_key': idempotencyKey,
  };
}

class SaleItem {
  final String packageId;
  final int quantity;
  final double price;
  final List<Discount> discounts;

  SaleItem({
    required this.packageId,
    required this.quantity,
    required this.price,
    this.discounts = const [],
  });

  Map<String, dynamic> toJson() => {
    'package_id': packageId,
    'qty': quantity,
    'price': price,
    'discounts': discounts.map((discount) => discount.toJson()).toList(),
  };
}

class Discount {
  final String type;
  final double amount;
  final String? reason;

  Discount({
    required this.type,
    required this.amount,
    this.reason,
  });

  Map<String, dynamic> toJson() => {
    'type': type,
    'amount': amount,
    if (reason != null) 'reason': reason,
  };
}
