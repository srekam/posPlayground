import 'package:flutter/material.dart';
import 'package:qr_flutter/qr_flutter.dart';
import '../core/theme/tokens.dart';

class TicketCard extends StatelessWidget {
  final String shortCode;
  final String qrPayload;
  final String subtitle;
  final bool disabled;
  final VoidCallback? onTap;

  const TicketCard({
    super.key,
    required this.shortCode,
    required this.qrPayload,
    required this.subtitle,
    this.disabled = false,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return InkWell(
      onTap: disabled ? null : onTap,
      child: Card(
        elevation: 0,
        child: Padding(
          padding: const EdgeInsets.all(Spacing.md),
          child: Row(
            children: [
              QrImageView(data: qrPayload, size: 72),
              const SizedBox(width: Spacing.md),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(shortCode, style: Theme.of(context).textTheme.titleLarge),
                    const SizedBox(height: Spacing.xs - 2),
                    Text(
                      subtitle,
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            color: cs.onSurfaceVariant,
                          ),
                    ),
                  ],
                ),
              ),
              Icon(
                Icons.chevron_right,
                color: disabled ? cs.onSurfaceVariant : cs.onSurface,
              ),
            ],
          ),
        ),
      ),
    );
  }
}


