class Shift {
  final String id;
  final String userId;
  final DateTime openedAt;
  final DateTime? closedAt;
  final double cashOpen;
  final double? cashClose;
  final double? variance;
  final ShiftCounters counters;
  final bool isActive;

  const Shift({
    required this.id,
    required this.userId,
    required this.openedAt,
    this.closedAt,
    required this.cashOpen,
    this.cashClose,
    this.variance,
    this.counters = const ShiftCounters(),
    this.isActive = true,
  });

  Shift copyWith({
    String? id,
    String? userId,
    DateTime? openedAt,
    DateTime? closedAt,
    double? cashOpen,
    double? cashClose,
    double? variance,
    ShiftCounters? counters,
    bool? isActive,
  }) {
    return Shift(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      openedAt: openedAt ?? this.openedAt,
      closedAt: closedAt ?? this.closedAt,
      cashOpen: cashOpen ?? this.cashOpen,
      cashClose: cashClose ?? this.cashClose,
      variance: variance ?? this.variance,
      counters: counters ?? this.counters,
      isActive: isActive ?? this.isActive,
    );
  }

  Duration? get duration {
    if (closedAt == null) return null;
    return closedAt!.difference(openedAt);
  }

  String get durationText {
    final dur = duration;
    if (dur == null) return 'Active';
    
    final hours = dur.inHours;
    final minutes = dur.inMinutes % 60;
    return '${hours}h ${minutes}m';
  }

  double get netSales {
    return counters.totalSales - (counters.totalRefunds + counters.totalDiscounts);
  }

  String get cashOpenText => '฿${cashOpen.toStringAsFixed(0)}';
  String get cashCloseText => cashClose != null ? '฿${cashClose!.toStringAsFixed(0)}' : 'N/A';
  String get varianceText => variance != null ? '฿${variance!.toStringAsFixed(0)}' : 'N/A';
}

class ShiftCounters {
  final int totalSales;
  final int totalRefunds;
  final int totalReprints;
  final double totalSalesAmount;
  final double totalRefundAmount;
  final double totalDiscounts;
  final int totalRedemptions;
  final int totalTicketsIssued;

  const ShiftCounters({
    this.totalSales = 0,
    this.totalRefunds = 0,
    this.totalReprints = 0,
    this.totalSalesAmount = 0.0,
    this.totalRefundAmount = 0.0,
    this.totalDiscounts = 0.0,
    this.totalRedemptions = 0,
    this.totalTicketsIssued = 0,
  });

  ShiftCounters copyWith({
    int? totalSales,
    int? totalRefunds,
    int? totalReprints,
    double? totalSalesAmount,
    double? totalRefundAmount,
    double? totalDiscounts,
    int? totalRedemptions,
    int? totalTicketsIssued,
  }) {
    return ShiftCounters(
      totalSales: totalSales ?? this.totalSales,
      totalRefunds: totalRefunds ?? this.totalRefunds,
      totalReprints: totalReprints ?? this.totalReprints,
      totalSalesAmount: totalSalesAmount ?? this.totalSalesAmount,
      totalRefundAmount: totalRefundAmount ?? this.totalRefundAmount,
      totalDiscounts: totalDiscounts ?? this.totalDiscounts,
      totalRedemptions: totalRedemptions ?? this.totalRedemptions,
      totalTicketsIssued: totalTicketsIssued ?? this.totalTicketsIssued,
    );
  }

  String get totalSalesAmountText => '฿${totalSalesAmount.toStringAsFixed(0)}';
  String get totalRefundAmountText => '฿${totalRefundAmount.toStringAsFixed(0)}';
  String get totalDiscountsText => '฿${totalDiscounts.toStringAsFixed(0)}';
}
