import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../../../domain/models/cart.dart';
import '../../../domain/models/cart_line.dart';
import '../../../domain/models/package.dart';

final cartProvider = StateNotifierProvider<CartNotifier, Cart>((ref) {
  return CartNotifier();
});

class CartNotifier extends StateNotifier<Cart> {
  CartNotifier() : super(const Cart());

  void addPackage(Package package, {int qty = 1}) {
    final existingLineIndex = state.lines.indexWhere((line) => line.package.id == package.id);
    
    if (existingLineIndex != -1) {
      // Update existing line
      final existingLine = state.lines[existingLineIndex];
      final newQty = existingLine.qty + qty;
      
      if (newQty <= 99) { // Max qty guard
        final updatedLines = List<CartLine>.from(state.lines);
        updatedLines[existingLineIndex] = existingLine.copyWith(qty: newQty);
        state = state.copyWith(lines: updatedLines);
      }
    } else {
      // Add new line
      final newLine = CartLine(package: package, qty: qty);
      state = state.copyWith(lines: [...state.lines, newLine]);
    }
  }

  void updateLineQty(String packageId, int qty) {
    if (qty <= 0) {
      removePackage(packageId);
      return;
    }
    
    if (qty > 99) return; // Max qty guard
    
    final lineIndex = state.lines.indexWhere((line) => line.package.id == packageId);
    if (lineIndex != -1) {
      final updatedLines = List<CartLine>.from(state.lines);
      updatedLines[lineIndex] = updatedLines[lineIndex].copyWith(qty: qty);
      state = state.copyWith(lines: updatedLines);
    }
  }

  void removePackage(String packageId) {
    final updatedLines = state.lines.where((line) => line.package.id != packageId).toList();
    state = state.copyWith(lines: updatedLines);
  }

  void clearCart() {
    state = const Cart();
  }

  void applyCartLevelDiscount({double? percent, double? amount}) {
    state = state.copyWith(
      cartLevelDiscountPercent: percent,
      cartLevelDiscountAmount: amount,
    );
  }

  void setCouponCode(String? code) {
    state = state.copyWith(couponCode: code);
  }

  CartLine? getLineByPackageId(String packageId) {
    try {
      return state.lines.firstWhere((line) => line.package.id == packageId);
    } catch (e) {
      return null;
    }
  }
}
