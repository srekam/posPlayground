import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import '../../core/theme/tokens.dart';
import 'providers/ticket_validator.dart';
import 'gate_result_screen.dart';

class GateScanScreen extends StatefulWidget {
  const GateScanScreen({super.key});

  @override
  State<GateScanScreen> createState() => _GateScanScreenState();
}

class _GateScanScreenState extends State<GateScanScreen> {
  bool _handled = false;
  final TicketValidator _validator = TicketValidator();
  final String _deviceId = 'GATE-001'; // Mock device ID

  void _onDetect(BarcodeCapture cap) {
    if (_handled) return;
    final code = cap.barcodes.firstOrNull?.rawValue;
    if (code == null) return;
    setState(() => _handled = true);

    // Validate the ticket
    final result = _validator.validateTicket(code, _deviceId);
    
    // Navigate to result screen
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => GateResultScreen(
          qrPayload: code,
          validationResult: result,
          onBack: () => setState(() => _handled = false),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Gate • Scan')),
      body: Stack(
        alignment: Alignment.center,
        children: [
          MobileScanner(onDetect: _onDetect),
          IgnorePointer(
            child: Container(
              decoration: BoxDecoration(
                border: Border.all(
                  width: 3,
                  color: Theme.of(context).colorScheme.primary,
                ),
                borderRadius: BorderRadius.circular(16),
              ),
              width: 260,
              height: 260,
            ),
          ),
          // Scanning indicator
          Positioned(
            bottom: 100,
            child: Container(
              padding: const EdgeInsets.symmetric(
                horizontal: Spacing.md,
                vertical: Spacing.sm,
              ),
              decoration: BoxDecoration(
                color: Colors.black54,
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Text(
                'Scan QR code',
                style: TextStyle(color: Colors.white),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

extension _FirstOrNull<T> on List<T> {
  T? get firstOrNull => isEmpty ? null : first;
}


