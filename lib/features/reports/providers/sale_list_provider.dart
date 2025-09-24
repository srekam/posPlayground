import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../../../domain/models/payment.dart';
import '../../../domain/models/ticket.dart';
import '../sale_list_screen.dart';

// Provider for managing sale records
final salesProvider = StateNotifierProvider<SalesNotifier, List<SaleRecord>>((ref) {
  return SalesNotifier();
});

class SalesNotifier extends StateNotifier<List<SaleRecord>> {
  SalesNotifier() : super([]);

  // Add a new sale record
  void addSale(Payment payment, List<Ticket> tickets) {
    final sale = SaleRecord(
      payment: payment,
      tickets: tickets,
      createdAt: DateTime.now(),
    );
    state = [sale, ...state]; // Add to beginning of list
  }

  // Remove a sale record (for refunds)
  void removeSale(String paymentId) {
    state = state.where((sale) => sale.payment.id != paymentId).toList();
  }

  // Get sales for current shift
  List<SaleRecord> getCurrentShiftSales() {
    // In a real app, you'd filter by shift ID
    return state;
  }

  // Get total sales amount for current shift
  double getCurrentShiftTotal() {
    return state.fold(0.0, (sum, sale) => sum + sale.payment.amount);
  }

  // Get total number of transactions
  int getTransactionCount() {
    return state.length;
  }
}
