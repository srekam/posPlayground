import 'package:flutter/material.dart';
import '../../core/theme/tokens.dart';
import '../../domain/models/user_role.dart';

class ApprovalPinDialog extends StatefulWidget {
  final ApprovalAction action;
  final String reason;
  final Function(bool approved, String? supervisorPin) onResult;

  const ApprovalPinDialog({
    super.key,
    required this.action,
    required this.reason,
    required this.onResult,
  });

  @override
  State<ApprovalPinDialog> createState() => _ApprovalPinDialogState();
}

class _ApprovalPinDialogState extends State<ApprovalPinDialog> {
  final TextEditingController _pinController = TextEditingController();
  final TextEditingController _reasonController = TextEditingController();
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _reasonController.text = widget.reason;
  }

  @override
  void dispose() {
    _pinController.dispose();
    _reasonController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text('${widget.action.actionDisplayName} Approval'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'This action requires supervisor approval.',
            style: Theme.of(context).textTheme.bodyMedium,
          ),
          const SizedBox(height: Spacing.md),
          
          // Reason field
          TextField(
            controller: _reasonController,
            decoration: const InputDecoration(
              labelText: 'Reason',
              border: OutlineInputBorder(),
              hintText: 'Enter reason for this action',
            ),
            maxLines: 2,
          ),
          
          const SizedBox(height: Spacing.md),
          
          // Supervisor PIN field
          TextField(
            controller: _pinController,
            decoration: const InputDecoration(
              labelText: 'Supervisor PIN',
              border: OutlineInputBorder(),
              hintText: 'Enter supervisor PIN',
            ),
            obscureText: true,
            keyboardType: TextInputType.number,
            maxLength: 4,
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: _isLoading ? null : () {
            Navigator.of(context).pop();
            widget.onResult(false, null);
          },
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: _isLoading ? null : _submitApproval,
          child: _isLoading
              ? const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Text('Approve'),
        ),
      ],
    );
  }

  void _submitApproval() async {
    if (_pinController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter supervisor PIN')),
      );
      return;
    }

    if (_reasonController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter a reason')),
      );
      return;
    }

    setState(() => _isLoading = true);

    // Simulate approval process
    await Future.delayed(const Duration(seconds: 1));

    setState(() => _isLoading = false);

    Navigator.of(context).pop();
    widget.onResult(true, _pinController.text);
  }
}

class ApprovalRequiredDialog extends StatelessWidget {
  final ApprovalAction action;
  final VoidCallback onRequestApproval;

  const ApprovalRequiredDialog({
    super.key,
    required this.action,
    required this.onRequestApproval,
  });

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text('${action.actionDisplayName} Requires Approval'),
      content: Text(
        'This action requires supervisor approval. Please contact a supervisor.',
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: () {
            Navigator.of(context).pop();
            onRequestApproval();
          },
          child: const Text('Request Approval'),
        ),
      ],
    );
  }
}
