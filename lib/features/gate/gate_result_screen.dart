import 'package:flutter/material.dart';
import '../../core/theme/tokens.dart';
import 'providers/ticket_validator.dart';

class GateResultScreen extends StatelessWidget {
  final String qrPayload;
  final ValidationResult validationResult;
  final VoidCallback onBack;

  const GateResultScreen({
    super.key,
    required this.qrPayload,
    required this.validationResult,
    required this.onBack,
  });

  @override
  Widget build(BuildContext context) {
    final isPass = validationResult.isPass;
    final colorScheme = Theme.of(context).colorScheme;

    return Scaffold(
      backgroundColor: isPass ? Colors.green.shade50 : Colors.red.shade50,
      appBar: AppBar(
        title: const Text('Gate • Result'),
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(Spacing.xl),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Large status indicator
              Container(
                width: 200,
                height: 200,
                decoration: BoxDecoration(
                  color: isPass ? Colors.green : Colors.red,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color:
                          (isPass ? Colors.green : Colors.red).withOpacity(0.3),
                      blurRadius: 20,
                      spreadRadius: 5,
                    ),
                  ],
                ),
                child: Icon(
                  isPass ? Icons.check : Icons.close,
                  size: 100,
                  color: Colors.white,
                ),
              ),

              const SizedBox(height: Spacing.xl),

              // Status text
              Text(
                isPass ? 'PASS' : 'FAIL',
                style: Theme.of(context).textTheme.displayLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: isPass ? Colors.green : Colors.red,
                    ),
              ),

              const SizedBox(height: Spacing.md),

              // Reason or remaining info
              if (isPass) ...[
                if (validationResult.remainingQuotaOrTime != null) ...[
                  Text(
                    'Remaining: ${validationResult.remainingQuotaOrTime}',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const SizedBox(height: Spacing.sm),
                  Text(
                    _getRemainingDescription(
                        validationResult.remainingQuotaOrTime!),
                    style: Theme.of(context).textTheme.bodyLarge,
                    textAlign: TextAlign.center,
                  ),
                ],
              ] else ...[
                Text(
                  validationResult.reason?.reasonDisplayName ?? 'Unknown error',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        color: Colors.red,
                      ),
                  textAlign: TextAlign.center,
                ),
              ],

              const SizedBox(height: Spacing.xl),

              // QR payload info
              Container(
                padding: const EdgeInsets.all(Spacing.md),
                decoration: BoxDecoration(
                  color: colorScheme.surface,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: colorScheme.outline),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Scanned Code:',
                      style: Theme.of(context).textTheme.labelMedium,
                    ),
                    const SizedBox(height: Spacing.xs),
                    Text(
                      qrPayload,
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            fontFamily: 'monospace',
                          ),
                      maxLines: 3,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              ),

              const SizedBox(height: Spacing.xl),

              // Action buttons
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () {
                        Navigator.of(context).pop();
                        onBack();
                      },
                      icon: const Icon(Icons.qr_code_scanner),
                      label: const Text('Scan Again'),
                    ),
                  ),
                  const SizedBox(width: Spacing.md),
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () => Navigator.of(context).pop(),
                      icon: const Icon(Icons.home),
                      label: const Text('Home'),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _getRemainingDescription(int remaining) {
    if (remaining == 0) {
      return 'Last use - ticket complete';
    } else if (remaining == 1) {
      return '1 use remaining';
    } else {
      return '$remaining uses remaining';
    }
  }
}
