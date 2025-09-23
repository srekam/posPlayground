enum UserRole { cashier, supervisor, admin }

enum ApprovalAction { reprint, refund, manualDiscount }

class User {
  final String id;
  final String name;
  final UserRole role;
  final String? pin;

  const User({
    required this.id,
    required this.name,
    required this.role,
    this.pin,
  });

  String get roleDisplayName {
    switch (role) {
      case UserRole.cashier:
        return 'Cashier';
      case UserRole.supervisor:
        return 'Supervisor';
      case UserRole.admin:
        return 'Admin';
    }
  }

  bool canPerformAction(ApprovalAction action) {
    switch (action) {
      case ApprovalAction.reprint:
      case ApprovalAction.refund:
        return role == UserRole.supervisor || role == UserRole.admin;
      case ApprovalAction.manualDiscount:
        return role == UserRole.supervisor || role == UserRole.admin;
    }
  }
}

class ApprovalRecord {
  final String id;
  final ApprovalAction action;
  final String requestedBy;
  final String? approvedBy;
  final String reason;
  final DateTime timestamp;
  final bool approved;
  final String? rejectionReason;

  const ApprovalRecord({
    required this.id,
    required this.action,
    required this.requestedBy,
    this.approvedBy,
    required this.reason,
    required this.timestamp,
    this.approved = false,
    this.rejectionReason,
  });

  String get actionDisplayName {
    switch (action) {
      case ApprovalAction.reprint:
        return 'Reprint';
      case ApprovalAction.refund:
        return 'Refund';
      case ApprovalAction.manualDiscount:
        return 'Manual Discount';
    }
  }
}
