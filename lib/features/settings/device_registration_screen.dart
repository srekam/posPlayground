import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

import '../../core/services/device_auth_service.dart';
import '../../core/config/app_config.dart';
import '../../core/providers/adaptive_provider.dart';

class DeviceRegistrationScreen extends HookConsumerWidget {
  const DeviceRegistrationScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final adaptiveState = ref.watch(adaptiveProvider);
    final siteKeyController = useTextEditingController(text: EnvironmentConfig.siteKey);
    final deviceNameController = useTextEditingController(text: 'POS Device');
    final isRegistering = useState(false);
    final errorMessage = useState<String?>(null);
    final successMessage = useState<String?>(null);

    final adaptiveMode = ref.watch(adaptiveProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Device Registration'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Current Status
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Current Status',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    const SizedBox(height: 8),
                    _buildStatusItem('Adaptive Mode', adaptiveState.mode.message),
                    _buildStatusItem('Backend URL', EnvironmentConfig.backendUrl),
                    _buildStatusItem('Device ID', EnvironmentConfig.deviceId),
                    _buildStatusItem(
                      'Device Token', 
                      EnvironmentConfig.deviceToken.isNotEmpty ? 'Set' : 'Not Set',
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 16),

            // Registration Form
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Device Registration',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    const SizedBox(height: 16),
                    
                    TextField(
                      controller: siteKeyController,
                      decoration: const InputDecoration(
                        labelText: 'Site Key',
                        hintText: 'tenant:store:secret-key',
                        border: OutlineInputBorder(),
                      ),
                    ),
                    
                    const SizedBox(height: 16),
                    
                    TextField(
                      controller: deviceNameController,
                      decoration: const InputDecoration(
                        labelText: 'Device Name',
                        hintText: 'Enter device name',
                        border: OutlineInputBorder(),
                      ),
                    ),
                    
                    const SizedBox(height: 16),
                    
                    if (errorMessage.value != null)
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.red.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: Colors.red.withOpacity(0.3)),
                        ),
                        child: Row(
                          children: [
                            const Icon(Icons.error, color: Colors.red, size: 20),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                errorMessage.value!,
                                style: const TextStyle(color: Colors.red),
                              ),
                            ),
                          ],
                        ),
                      ),
                    
                    if (successMessage.value != null)
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.green.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: Colors.green.withOpacity(0.3)),
                        ),
                        child: Row(
                          children: [
                            const Icon(Icons.check_circle, color: Colors.green, size: 20),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                successMessage.value!,
                                style: const TextStyle(color: Colors.green),
                              ),
                            ),
                          ],
                        ),
                      ),
                    
                    const SizedBox(height: 16),
                    
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        onPressed: isRegistering.value ? null : () => _registerDevice(
                          context,
                          ref,
                          siteKeyController.text,
                          deviceNameController.text,
                          isRegistering,
                          errorMessage,
                          successMessage,
                        ),
                        child: isRegistering.value
                            ? const Row(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  SizedBox(
                                    width: 16,
                                    height: 16,
                                    child: CircularProgressIndicator(strokeWidth: 2),
                                  ),
                                  SizedBox(width: 8),
                                  Text('Registering...'),
                                ],
                              )
                            : const Text('Register Device'),
                      ),
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 16),

            // Quick Actions
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Quick Actions',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 16),
                    
                    Row(
                      children: [
                        Expanded(
                          child: OutlinedButton.icon(
                            onPressed: () => _useDemoCredentials(
                              siteKeyController,
                              deviceNameController,
                            ),
                            icon: const Icon(Icons.play_arrow),
                            label: const Text('Use Demo'),
                          ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: OutlinedButton.icon(
                            onPressed: () => _resetToDefaults(
                              siteKeyController,
                              deviceNameController,
                              errorMessage,
                              successMessage,
                            ),
                            icon: const Icon(Icons.refresh),
                            label: const Text('Reset'),
                          ),
                        ),
                      ],
                    ),
                    
                    const SizedBox(height: 8),
                    
                    SizedBox(
                      width: double.infinity,
                      child: OutlinedButton.icon(
                        onPressed: () => _testConnection(context, ref),
                        icon: const Icon(Icons.network_check),
                        label: const Text('Test Connection'),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusItem(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 100,
            child: Text(
              '$label:',
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(fontFamily: 'monospace'),
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _registerDevice(
    BuildContext context,
    WidgetRef ref,
    String siteKey,
    String deviceName,
    ValueNotifier<bool> isRegistering,
    ValueNotifier<String?> errorMessage,
    ValueNotifier<String?> successMessage,
  ) async {
    if (siteKey.isEmpty) {
      errorMessage.value = 'Site key is required';
      return;
    }

    isRegistering.value = true;
    errorMessage.value = null;
    successMessage.value = null;

    try {
      final deviceAuthService = DeviceAuthService();
      final result = await deviceAuthService.registerDevice(
        siteKey: siteKey,
        deviceName: deviceName,
      );

      if (result.isSuccess) {
        successMessage.value = 'Device registered successfully!';
        
        // Update adaptive mode
        ref.read(adaptiveProvider.notifier).forceUpdate();
        
        // Show success dialog
        if (context.mounted) {
          showDialog(
            context: context,
            builder: (context) => AlertDialog(
              title: const Text('Registration Successful'),
              content: const Text('Your device has been registered successfully. You can now use the app.'),
              actions: [
                TextButton(
                  onPressed: () {
                    Navigator.of(context).pop();
                    Navigator.of(context).pop();
                  },
                  child: const Text('OK'),
                ),
              ],
            ),
          );
        }
      } else {
        errorMessage.value = result.error;
      }
    } catch (e) {
      errorMessage.value = 'Registration failed: $e';
    } finally {
      isRegistering.value = false;
    }
  }

  void _useDemoCredentials(
    TextEditingController siteKeyController,
    TextEditingController deviceNameController,
  ) {
    siteKeyController.text = AppConfig.defaultSiteKey;
    deviceNameController.text = 'Demo POS Device';
  }

  void _resetToDefaults(
    TextEditingController siteKeyController,
    TextEditingController deviceNameController,
    ValueNotifier<String?> errorMessage,
    ValueNotifier<String?> successMessage,
  ) {
    siteKeyController.text = '';
    deviceNameController.text = '';
    errorMessage.value = null;
    successMessage.value = null;
    EnvironmentConfig.reset();
  }

  Future<void> _testConnection(BuildContext context, WidgetRef ref) async {
    try {
      final connectivityService = ref.read(connectivityServiceProvider);
      await connectivityService.forceBackendHealthCheck();
      
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Connection test initiated'),
            duration: Duration(seconds: 2),
          ),
        );
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Connection test failed: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }
}
