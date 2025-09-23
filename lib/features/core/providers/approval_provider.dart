import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../../../domain/models/user_role.dart';

final approvalProvider = StateNotifierProvider<ApprovalNotifier, ApprovalState>((ref) {
  return ApprovalNotifier();
});

class ApprovalState {
  final User? currentUser;
  final List<ApprovalRecord> approvalHistory;

  const ApprovalState({
    this.currentUser,
    this.approvalHistory = const [],
  });

  ApprovalState copyWith({
    User? currentUser,
    List<ApprovalRecord>? approvalHistory,
  }) {
    return ApprovalState(
      currentUser: currentUser ?? this.currentUser,
      approvalHistory: approvalHistory ?? this.approvalHistory,
    );
  }
}

class ApprovalNotifier extends StateNotifier<ApprovalState> {
  ApprovalNotifier() : super(const ApprovalState()) {
    // Initialize with mock user
    state = state.copyWith(
      currentUser: const User(
        id: 'user-001',
        name: 'John Cashier',
        role: UserRole.cashier,
        pin: '1234',
      ),
    );
  }

  Future<bool> requestApproval(
    ApprovalAction action,
    String reason,
    String? supervisorPin,
  ) async {
    final currentUser = state.currentUser;
    if (currentUser == null) return false;

    // Check if user can perform action directly
    if (currentUser.canPerformAction(action)) {
      return true;
    }

    // Check supervisor PIN for elevated actions
    if (supervisorPin != null) {
      final supervisor = _findSupervisorByPin(supervisorPin);
      if (supervisor != null) {
        final record = ApprovalRecord(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          action: action,
          requestedBy: currentUser.id,
          approvedBy: supervisor.id,
          reason: reason,
          timestamp: DateTime.now(),
          approved: true,
        );

        state = state.copyWith(
          approvalHistory: [...state.approvalHistory, record],
        );

        return true;
      }
    }

    // Record failed approval attempt
    final record = ApprovalRecord(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      action: action,
      requestedBy: currentUser.id,
      reason: reason,
      timestamp: DateTime.now(),
      approved: false,
      rejectionReason: 'Invalid supervisor PIN',
    );

    state = state.copyWith(
      approvalHistory: [...state.approvalHistory, record],
    );

    return false;
  }

  User? _findSupervisorByPin(String pin) {
    // Mock supervisor lookup
    const supervisors = [
      User(
        id: 'supervisor-001',
        name: 'Jane Supervisor',
        role: UserRole.supervisor,
        pin: '5678',
      ),
      User(
        id: 'admin-001',
        name: 'Admin User',
        role: UserRole.admin,
        pin: '9999',
      ),
    ];

    return supervisors.firstWhere(
      (user) => user.pin == pin,
      orElse: () => throw StateError('Supervisor not found'),
    );
  }

  void switchUser(User user) {
    state = state.copyWith(currentUser: user);
  }

  List<ApprovalRecord> getApprovalHistory() {
    return state.approvalHistory;
  }

  List<ApprovalRecord> getApprovalHistoryByUser(String userId) {
    return state.approvalHistory
        .where((record) => record.requestedBy == userId)
        .toList();
  }

  int getApprovalCountByAction(ApprovalAction action) {
    return state.approvalHistory
        .where((record) => record.action == action && record.approved)
        .length;
  }
}
