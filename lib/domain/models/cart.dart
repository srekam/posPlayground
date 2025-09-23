import 'cart_line.dart';

class Cart {
  final List<CartLine> lines;
  final double? cartLevelDiscountPercent;
  final double? cartLevelDiscountAmount;
  final String? couponCode;

  const Cart({
    this.lines = const [],
    this.cartLevelDiscountPercent,
    this.cartLevelDiscountAmount,
    this.couponCode,
  });

  double get subtotal => lines.fold(0.0, (sum, line) => sum + line.lineTotal);

  double get cartLevelDiscount {
    if (cartLevelDiscountPercent != null) {
      return subtotal * (cartLevelDiscountPercent! / 100);
    }
    return cartLevelDiscountAmount ?? 0;
  }

  double get grandTotal => (subtotal - cartLevelDiscount).clamp(0, double.infinity);

  bool get isEmpty => lines.isEmpty;

  bool get isNotEmpty => lines.isNotEmpty;

  int get totalItems => lines.fold(0, (sum, line) => sum + line.qty);

  String get subtotalText => '฿${subtotal.toStringAsFixed(0)}';
  String get grandTotalText => '฿${grandTotal.toStringAsFixed(0)}';
  String get cartLevelDiscountText => '฿${cartLevelDiscount.toStringAsFixed(0)}';

  Cart copyWith({
    List<CartLine>? lines,
    double? cartLevelDiscountPercent,
    double? cartLevelDiscountAmount,
    String? couponCode,
  }) {
    return Cart(
      lines: lines ?? this.lines,
      cartLevelDiscountPercent: cartLevelDiscountPercent ?? this.cartLevelDiscountPercent,
      cartLevelDiscountAmount: cartLevelDiscountAmount ?? this.cartLevelDiscountAmount,
      couponCode: couponCode ?? this.couponCode,
    );
  }
}
