import 'package.dart';

class CartLine {
  final Package package;
  final int qty;
  final double? manualDiscountPercent;
  final double? manualDiscountAmount;

  const CartLine({
    required this.package,
    required this.qty,
    this.manualDiscountPercent,
    this.manualDiscountAmount,
  });

  double get unitPrice => package.price;

  double get lineTotal {
    final subtotal = unitPrice * qty;
    final discount = manualDiscountPercent != null
        ? subtotal * (manualDiscountPercent! / 100)
        : (manualDiscountAmount ?? 0);
    return (subtotal - discount).clamp(0, double.infinity);
  }

  double get discountAmount {
    final subtotal = unitPrice * qty;
    return manualDiscountPercent != null
        ? subtotal * (manualDiscountPercent! / 100)
        : (manualDiscountAmount ?? 0);
  }

  String get lineTotalText => '฿${lineTotal.toStringAsFixed(0)}';

  CartLine copyWith({
    Package? package,
    int? qty,
    double? manualDiscountPercent,
    double? manualDiscountAmount,
  }) {
    return CartLine(
      package: package ?? this.package,
      qty: qty ?? this.qty,
      manualDiscountPercent: manualDiscountPercent ?? this.manualDiscountPercent,
      manualDiscountAmount: manualDiscountAmount ?? this.manualDiscountAmount,
    );
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is CartLine && other.package.id == package.id;
  }

  @override
  int get hashCode => package.id.hashCode;
}
