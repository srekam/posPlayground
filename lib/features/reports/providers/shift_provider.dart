import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../../../domain/models/shift.dart';
import '../../../domain/models/payment.dart';

final shiftProvider = StateNotifierProvider<ShiftNotifier, ShiftState>((ref) {
  return ShiftNotifier();
});

class ShiftState {
  final Shift? currentShift;
  final List<Shift> shiftHistory;
  final bool isLoading;

  const ShiftState({
    this.currentShift,
    this.shiftHistory = const [],
    this.isLoading = false,
  });

  ShiftState copyWith({
    Shift? currentShift,
    List<Shift>? shiftHistory,
    bool? isLoading,
  }) {
    return ShiftState(
      currentShift: currentShift ?? this.currentShift,
      shiftHistory: shiftHistory ?? this.shiftHistory,
      isLoading: isLoading ?? this.isLoading,
    );
  }
}

class ShiftNotifier extends StateNotifier<ShiftState> {
  ShiftNotifier() : super(const ShiftState()) {
    _loadShiftHistory();
  }

  void _loadShiftHistory() {
    // Mock shift history
    final now = DateTime.now();
    final mockHistory = [
      Shift(
        id: 'shift-001',
        userId: 'user-001',
        openedAt: now.subtract(const Duration(hours: 8)),
        closedAt: now.subtract(const Duration(hours: 1)),
        cashOpen: 1000.0,
        cashClose: 1250.0,
        variance: 250.0,
        counters: const ShiftCounters(
          totalSales: 15,
          totalRefunds: 2,
          totalReprints: 1,
          totalSalesAmount: 3750.0,
          totalRefundAmount: 500.0,
          totalDiscounts: 150.0,
          totalRedemptions: 12,
          totalTicketsIssued: 15,
        ),
        isActive: false,
      ),
    ];

    state = state.copyWith(shiftHistory: mockHistory);
  }

  Future<bool> openShift(String userId, double cashOpen) async {
    if (state.currentShift != null) {
      return false; // Shift already open
    }

    state = state.copyWith(isLoading: true);

    // Simulate opening shift
    await Future.delayed(const Duration(seconds: 1));

    final shift = Shift(
      id: 'shift-${DateTime.now().millisecondsSinceEpoch}',
      userId: userId,
      openedAt: DateTime.now(),
      cashOpen: cashOpen,
    );

    state = state.copyWith(
      currentShift: shift,
      isLoading: false,
    );

    return true;
  }

  Future<bool> closeShift(double cashClose) async {
    if (state.currentShift == null) {
      return false; // No active shift
    }

    state = state.copyWith(isLoading: true);

    // Simulate closing shift
    await Future.delayed(const Duration(seconds: 1));

    final currentShift = state.currentShift!;
    final variance = cashClose - currentShift.cashOpen - currentShift.netSales;

    final closedShift = currentShift.copyWith(
      closedAt: DateTime.now(),
      cashClose: cashClose,
      variance: variance,
      isActive: false,
    );

    state = state.copyWith(
      currentShift: null,
      shiftHistory: [...state.shiftHistory, closedShift],
      isLoading: false,
    );

    return true;
  }

  void recordSale(Payment payment) {
    if (state.currentShift == null) return;

    final currentShift = state.currentShift!;
    final counters = currentShift.counters.copyWith(
      totalSales: currentShift.counters.totalSales + 1,
      totalSalesAmount: currentShift.counters.totalSalesAmount + payment.amount,
      totalTicketsIssued: currentShift.counters.totalTicketsIssued + 1,
    );

    state = state.copyWith(
      currentShift: currentShift.copyWith(counters: counters),
    );
  }

  void recordRefund(double amount) {
    if (state.currentShift == null) return;

    final currentShift = state.currentShift!;
    final counters = currentShift.counters.copyWith(
      totalRefunds: currentShift.counters.totalRefunds + 1,
      totalRefundAmount: currentShift.counters.totalRefundAmount + amount,
    );

    state = state.copyWith(
      currentShift: currentShift.copyWith(counters: counters),
    );
  }

  void recordReprint() {
    if (state.currentShift == null) return;

    final currentShift = state.currentShift!;
    final counters = currentShift.counters.copyWith(
      totalReprints: currentShift.counters.totalReprints + 1,
    );

    state = state.copyWith(
      currentShift: currentShift.copyWith(counters: counters),
    );
  }

  void recordRedemption() {
    if (state.currentShift == null) return;

    final currentShift = state.currentShift!;
    final counters = currentShift.counters.copyWith(
      totalRedemptions: currentShift.counters.totalRedemptions + 1,
    );

    state = state.copyWith(
      currentShift: currentShift.copyWith(counters: counters),
    );
  }

  void recordDiscount(double amount) {
    if (state.currentShift == null) return;

    final currentShift = state.currentShift!;
    final counters = currentShift.counters.copyWith(
      totalDiscounts: currentShift.counters.totalDiscounts + amount,
    );

    state = state.copyWith(
      currentShift: currentShift.copyWith(counters: counters),
    );
  }

  List<Shift> getTodayShifts() {
    final today = DateTime.now();
    return state.shiftHistory.where((shift) {
      return shift.openedAt.day == today.day &&
          shift.openedAt.month == today.month &&
          shift.openedAt.year == today.year;
    }).toList();
  }

  double getTodayTotalSales() {
    return getTodayShifts()
        .fold(0.0, (sum, shift) => sum + shift.counters.totalSalesAmount);
  }

  int getTodayTotalTransactions() {
    return getTodayShifts()
        .fold(0, (sum, shift) => sum + shift.counters.totalSales);
  }
}
