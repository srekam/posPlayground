import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'dart:convert';
import '../../data/services/api_service.dart';

class DeviceEnrollmentScreen extends StatefulWidget {
  const DeviceEnrollmentScreen({Key? key}) : super(key: key);

  @override
  State<DeviceEnrollmentScreen> createState() => _DeviceEnrollmentScreenState();
}

class _DeviceEnrollmentScreenState extends State<DeviceEnrollmentScreen> {
  final PageController _pageController = PageController();
  int _currentPage = 0;
  String? _errorMessage;
  String? _successMessage;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[50],
      body: SafeArea(
        child: Column(
          children: [
            // Header
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.white,
                boxShadow: [
                  BoxShadow(
                    color: Colors.grey.withOpacity(0.1),
                    spreadRadius: 1,
                    blurRadius: 3,
                    offset: const Offset(0, 1),
                  ),
                ],
              ),
              child: Row(
                children: [
                  IconButton(
                    onPressed: () => Navigator.of(context).pop(),
                    icon: const Icon(Icons.arrow_back),
                  ),
                  const SizedBox(width: 10),
                  const Text(
                    'Device Pairing',
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),

            // Progress Indicator
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
              child: Row(
                children: [
                  Expanded(
                    child: LinearProgressIndicator(
                      value: (_currentPage + 1) / 3,
                      backgroundColor: Colors.grey[300],
                      valueColor: AlwaysStoppedAnimation<Color>(
                        Theme.of(context).primaryColor,
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Text(
                    '${_currentPage + 1}/3',
                    style: TextStyle(
                      color: Colors.grey[600],
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
            ),

            // Content
            Expanded(
              child: PageView(
                controller: _pageController,
                onPageChanged: (index) {
                  setState(() {
                    _currentPage = index;
                  });
                },
                children: [
                  _buildWelcomePage(),
                  _buildPairingMethodPage(),
                  _buildSuccessPage(),
                ],
              ),
            ),

            // Error/Success Messages
            if (_errorMessage != null)
              Container(
                margin: const EdgeInsets.all(20),
                padding: const EdgeInsets.all(15),
                decoration: BoxDecoration(
                  color: Colors.red[50],
                  border: Border.all(color: Colors.red[200]!),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    Icon(Icons.error, color: Colors.red[600]),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        _errorMessage!,
                        style: TextStyle(color: Colors.red[600]),
                      ),
                    ),
                    IconButton(
                      onPressed: () => setState(() => _errorMessage = null),
                      icon: const Icon(Icons.close),
                      color: Colors.red[600],
                    ),
                  ],
                ),
              ),

            if (_successMessage != null)
              Container(
                margin: const EdgeInsets.all(20),
                padding: const EdgeInsets.all(15),
                decoration: BoxDecoration(
                  color: Colors.green[50],
                  border: Border.all(color: Colors.green[200]!),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    Icon(Icons.check_circle, color: Colors.green[600]),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        _successMessage!,
                        style: TextStyle(color: Colors.green[600]),
                      ),
                    ),
                    IconButton(
                      onPressed: () => setState(() => _successMessage = null),
                      icon: const Icon(Icons.close),
                      color: Colors.green[600],
                    ),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildWelcomePage() {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          // Logo
          Container(
            width: 120,
            height: 120,
            decoration: BoxDecoration(
              color: Theme.of(context).primaryColor,
              borderRadius: BorderRadius.circular(20),
            ),
            child: const Icon(
              Icons.store,
              size: 60,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 30),

          // Title
          const Text(
            'Welcome to PlayPark',
            style: TextStyle(
              fontSize: 28,
              fontWeight: FontWeight.bold,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 15),

          // Subtitle
          Text(
            'Let\'s pair your device to get started',
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey[600],
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 40),

          // Features
          _buildFeatureItem(
            Icons.qr_code_scanner,
            'Quick Setup',
            'Pair your device in under 1 minute',
          ),
          const SizedBox(height: 20),
          _buildFeatureItem(
            Icons.security,
            'Secure',
            'Your device is securely connected',
          ),
          const SizedBox(height: 20),
          _buildFeatureItem(
            Icons.support,
            'Support',
            'Get help when you need it',
          ),
          const SizedBox(height: 50),

          // Continue Button
          SizedBox(
            width: double.infinity,
            height: 50,
            child: ElevatedButton(
              onPressed: () => _pageController.nextPage(
                duration: const Duration(milliseconds: 300),
                curve: Curves.easeInOut,
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: Theme.of(context).primaryColor,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(25),
                ),
              ),
              child: const Text(
                'Get Started',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                  color: Colors.white,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFeatureItem(IconData icon, String title, String description) {
    return Row(
      children: [
        Container(
          width: 50,
          height: 50,
          decoration: BoxDecoration(
            color: Theme.of(context).primaryColor.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Icon(
            icon,
            color: Theme.of(context).primaryColor,
            size: 24,
          ),
        ),
        const SizedBox(width: 15),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),
              Text(
                description,
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey[600],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildPairingMethodPage() {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Text(
            'Choose Pairing Method',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 10),
          Text(
            'Select how you\'d like to pair your device',
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey[600],
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 40),

          // QR Code Option
          _buildPairingOption(
            icon: Icons.qr_code_scanner,
            title: 'Scan QR Code',
            description: 'Point your camera at the QR code',
            onTap: () => _navigateToQRScanner(),
          ),
          const SizedBox(height: 20),

          // Deep Link Option
          _buildPairingOption(
            icon: Icons.link,
            title: 'Open Link',
            description: 'Tap a pairing link from email or message',
            onTap: () => _handleDeepLink(),
          ),
          const SizedBox(height: 20),

          // Manual Key Option
          _buildPairingOption(
            icon: Icons.keyboard,
            title: 'Enter Code',
            description: 'Type the pairing code manually',
            onTap: () => _showManualKeyDialog(),
          ),
        ],
      ),
    );
  }

  Widget _buildPairingOption({
    required IconData icon,
    required String title,
    required String description,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.grey[200]!),
          boxShadow: [
            BoxShadow(
              color: Colors.grey.withOpacity(0.1),
              spreadRadius: 1,
              blurRadius: 3,
              offset: const Offset(0, 1),
            ),
          ],
        ),
        child: Row(
          children: [
            Container(
              width: 60,
              height: 60,
              decoration: BoxDecoration(
                color: Theme.of(context).primaryColor.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(
                icon,
                color: Theme.of(context).primaryColor,
                size: 28,
              ),
            ),
            const SizedBox(width: 20),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 5),
                  Text(
                    description,
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey[600],
                    ),
                  ),
                ],
              ),
            ),
            Icon(
              Icons.arrow_forward_ios,
              color: Colors.grey[400],
              size: 16,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSuccessPage() {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          // Success Icon
          Container(
            width: 120,
            height: 120,
            decoration: BoxDecoration(
              color: Colors.green,
              borderRadius: BorderRadius.circular(60),
            ),
            child: const Icon(
              Icons.check,
              size: 60,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 30),

          // Success Message
          const Text(
            'Device Paired Successfully!',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 15),

          Text(
            'Your device is now connected and ready to use',
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey[600],
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 40),

          // Device Info
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.grey[200]!),
            ),
            child: Column(
              children: [
                _buildInfoRow('Device Type', 'POS Terminal'),
                const Divider(),
                _buildInfoRow('Store', 'Main Store'),
                const Divider(),
                _buildInfoRow('Status', 'Active'),
              ],
            ),
          ),
          const SizedBox(height: 40),

          // Continue Button
          SizedBox(
            width: double.infinity,
            height: 50,
            child: ElevatedButton(
              onPressed: () {
                // Navigate to main app
                Navigator.of(context).pushReplacementNamed('/pos');
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Theme.of(context).primaryColor,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(25),
                ),
              ),
              child: const Text(
                'Continue to App',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                  color: Colors.white,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey[600],
            ),
          ),
          Text(
            value,
            style: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  void _navigateToQRScanner() {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) =>
            QRScannerScreen(onEnrollmentToken: _processEnrollment),
      ),
    );
  }

  void _handleDeepLink() {
    // This would be handled by the app's deep link handler
    // For now, show a message
    setState(() {
      _errorMessage = 'Deep link handling not implemented yet';
    });
  }

  void _showManualKeyDialog() {
    showDialog(
      context: context,
      builder: (context) => ManualKeyDialog(
        onKeyEntered: (key) => _processEnrollmentToken(key),
      ),
    );
  }

  Future<void> _processEnrollmentToken(String token) async {
    setState(() {
      _errorMessage = null;
    });

    try {
      // Call enrollment API
      final response = await ApiService.enrollDevice(
        enrollToken: token,
        deviceType: 'POS',
        appVersion: '1.0.0',
        deviceFingerprint: 'device_${DateTime.now().millisecondsSinceEpoch}',
      );

      if (response.isSuccess) {
        setState(() {
          _successMessage = 'Device enrolled successfully!';
        });

        // Move to success page
        _pageController.animateToPage(
          2,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeInOut,
        );
      } else {
        setState(() {
          _errorMessage = response.error ?? 'Enrollment failed';
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Enrollment failed: $e';
      });
    }
  }

  Future<void> _processEnrollment(String enrollToken) async {
    setState(() {
      _errorMessage = null;
    });

    try {
      // Call enrollment API
      final response = await ApiService.enrollDevice(
        enrollToken: enrollToken,
        deviceType: 'POS',
        appVersion: '1.0.0',
        deviceFingerprint: 'device_${DateTime.now().millisecondsSinceEpoch}',
      );

      if (response.isSuccess) {
        setState(() {
          _successMessage = 'Device enrolled successfully!';
        });

        // Move to success page
        _pageController.animateToPage(
          2,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeInOut,
        );
      } else {
        setState(() {
          _errorMessage = response.error ?? 'Enrollment failed';
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Network error: $e';
      });
    }
  }
}

class QRScannerScreen extends StatefulWidget {
  final Function(String) onEnrollmentToken;

  const QRScannerScreen({Key? key, required this.onEnrollmentToken})
      : super(key: key);

  @override
  State<QRScannerScreen> createState() => _QRScannerScreenState();
}

class _QRScannerScreenState extends State<QRScannerScreen> {
  MobileScannerController controller = MobileScannerController();
  String? _scannedData;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Scan QR Code'),
        backgroundColor: Colors.black,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            onPressed: () => controller.toggleTorch(),
            icon: const Icon(Icons.flash_on),
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            flex: 4,
            child: MobileScanner(
              controller: controller,
              onDetect: _onDetect,
            ),
          ),
          Expanded(
            flex: 1,
            child: Container(
              padding: const EdgeInsets.all(20),
              child: Column(
                children: [
                  const Text(
                    'Point your camera at the QR code',
                    style: TextStyle(fontSize: 16),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 10),
                  ElevatedButton(
                    onPressed: () => Navigator.of(context).pop(),
                    child: const Text('Cancel'),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _onDetect(BarcodeCapture capture) {
    final List<Barcode> barcodes = capture.barcodes;
    for (final barcode in barcodes) {
      if (barcode.rawValue != null && _scannedData == null) {
        setState(() {
          _scannedData = barcode.rawValue;
        });

        // Process the scanned data
        _processScannedData(barcode.rawValue!);
      }
    }
  }

  void _processScannedData(String data) {
    try {
      // Decode the QR payload
      final decoded = base64Url.decode(data);
      final payload = jsonDecode(utf8.decode(decoded));

      // Extract enrollment token
      final enrollToken = payload['et'];

      if (enrollToken != null) {
        Navigator.of(context).pop();
        // Process enrollment
        widget.onEnrollmentToken(enrollToken);
      } else {
        throw Exception('No enrollment token found in QR code');
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Invalid QR code: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }
}

class ManualKeyDialog extends StatefulWidget {
  final Function(String) onKeyEntered;

  const ManualKeyDialog({
    Key? key,
    required this.onKeyEntered,
  }) : super(key: key);

  @override
  State<ManualKeyDialog> createState() => _ManualKeyDialogState();
}

class _ManualKeyDialogState extends State<ManualKeyDialog> {
  final TextEditingController _keyController = TextEditingController();
  final FocusNode _keyFocusNode = FocusNode();

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Enter Pairing Code'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Text(
            'Enter the pairing code provided by your administrator',
            style: TextStyle(fontSize: 14),
          ),
          const SizedBox(height: 20),
          TextField(
            controller: _keyController,
            focusNode: _keyFocusNode,
            decoration: const InputDecoration(
              labelText: 'Pairing Code',
              hintText: 'PP.XXXX.XXXX.XXXX.XXXX.XX',
              border: OutlineInputBorder(),
            ),
            textCapitalization: TextCapitalization.characters,
            inputFormatters: [
              FilteringTextInputFormatter.allow(RegExp(r'[A-Z0-9.-]')),
              LengthLimitingTextInputFormatter(
                  35), // Increased to accommodate new manual key format
            ],
            onSubmitted: (value) => _submitKey(),
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: _submitKey,
          child: const Text('Pair Device'),
        ),
      ],
    );
  }

  void _submitKey() {
    final key = _keyController.text.trim();
    if (key.isNotEmpty) {
      widget.onKeyEntered(key);
      Navigator.of(context).pop();
    }
  }

  @override
  void dispose() {
    _keyController.dispose();
    _keyFocusNode.dispose();
    super.dispose();
  }
}
