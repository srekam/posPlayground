import 'package:flutter/foundation.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../../../domain/models/payment.dart';
import '../../../domain/models/cart.dart';

final paymentProvider = StateNotifierProvider<PaymentNotifier, PaymentState>((ref) {
  return PaymentNotifier();
});

class PaymentState {
  final PaymentMethod selectedMethod;
  final double tenderedAmount;
  final bool isProcessing;

  const PaymentState({
    this.selectedMethod = PaymentMethod.cash,
    this.tenderedAmount = 0,
    this.isProcessing = false,
  });

  PaymentState copyWith({
    PaymentMethod? selectedMethod,
    double? tenderedAmount,
    bool? isProcessing,
  }) {
    return PaymentState(
      selectedMethod: selectedMethod ?? this.selectedMethod,
      tenderedAmount: tenderedAmount ?? this.tenderedAmount,
      isProcessing: isProcessing ?? this.isProcessing,
    );
  }
}

class PaymentNotifier extends StateNotifier<PaymentState> {
  PaymentNotifier() : super(const PaymentState());

  void selectPaymentMethod(PaymentMethod method) {
    state = state.copyWith(selectedMethod: method);
  }

  void setTenderedAmount(double amount) {
    state = state.copyWith(tenderedAmount: amount);
  }

  bool canCompletePayment(double grandTotal) {
    switch (state.selectedMethod) {
      case PaymentMethod.cash:
        return state.tenderedAmount >= grandTotal;
      case PaymentMethod.qrCode:
      case PaymentMethod.card:
        return true; // Mock - always allowed
    }
  }

  Future<Payment> processPayment(Cart cart) async {
    state = state.copyWith(isProcessing: true);
    
    try {
      // Simulate payment processing delay
      await Future.delayed(const Duration(seconds: 1));
      
      final payment = Payment(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        method: state.selectedMethod,
        amount: cart.grandTotal,
        tenderedAmount: state.selectedMethod == PaymentMethod.cash ? state.tenderedAmount : null,
        changeAmount: state.selectedMethod == PaymentMethod.cash 
            ? state.tenderedAmount - cart.grandTotal 
            : null,
        reference: _generateReference(),
        processedAt: DateTime.now(),
        status: PaymentStatus.completed,
      );

      // Reset state after successful payment
      state = const PaymentState();
      
      return payment;
    } catch (e) {
      state = state.copyWith(isProcessing: false);
      rethrow;
    }
  }

  String _generateReference() {
    switch (state.selectedMethod) {
      case PaymentMethod.cash:
        return 'CASH-${DateTime.now().millisecondsSinceEpoch.toString().substring(8)}';
      case PaymentMethod.qrCode:
        return 'QR-${DateTime.now().millisecondsSinceEpoch.toString().substring(8)}';
      case PaymentMethod.card:
        return 'CARD-${DateTime.now().millisecondsSinceEpoch.toString().substring(8)}';
    }
  }
}
