import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import '../../core/models/server_config.dart';
import '../../core/services/server_config_service.dart';
import '../../widgets/settings/settings_section.dart';
import '../../widgets/settings/settings_tile.dart';

class ServerConfigScreen extends StatefulWidget {
  const ServerConfigScreen({super.key});

  @override
  State<ServerConfigScreen> createState() => _ServerConfigScreenState();
}

class _ServerConfigScreenState extends State<ServerConfigScreen> {
  final _formKey = GlobalKey<FormState>();
  final _hostController = TextEditingController();
  final _portController = TextEditingController();
  final _apiKeyController = TextEditingController();
  
  bool _useHttps = false;
  bool _isLoading = false;
  bool _isTestingConnection = false;
  bool _isGeneratingApiKey = false;
  bool _showApiKey = false;
  
  ServerConfig? _currentConfig;
  ApiKeyInfo? _currentApiKey;
  ServerTestResult? _lastTestResult;

  @override
  void initState() {
    super.initState();
    _loadCurrentConfig();
  }

  @override
  void dispose() {
    _hostController.dispose();
    _portController.dispose();
    _apiKeyController.dispose();
    super.dispose();
  }

  Future<void> _loadCurrentConfig() async {
    setState(() => _isLoading = true);
    
    try {
      final config = await ServerConfigService.getCurrentConfig();
      final apiKey = await ServerConfigService.getCurrentApiKey();
      
      setState(() {
        _currentConfig = config;
        _currentApiKey = apiKey;
        _hostController.text = config.host;
        _portController.text = config.port.toString();
        _useHttps = config.useHttps;
        if (apiKey != null) {
          _apiKeyController.text = apiKey.displayKey;
        }
      });
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _saveConfig() async {
    if (!_formKey.currentState!.validate()) return;

    final config = ServerConfig(
      host: _hostController.text.trim(),
      port: int.parse(_portController.text),
      protocol: _useHttps ? 'https' : 'http',
      useHttps: _useHttps,
      apiKey: _apiKeyController.text.trim().isNotEmpty ? _apiKeyController.text.trim() : null,
    );

    await ServerConfigService.saveConfig(config);
    
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Server configuration saved')),
      );
      setState(() => _currentConfig = config);
    }
  }

  Future<void> _testConnection() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isTestingConnection = true);
    
    try {
      final config = ServerConfig(
        host: _hostController.text.trim(),
        port: int.parse(_portController.text),
        protocol: _useHttps ? 'https' : 'http',
        useHttps: _useHttps,
        apiKey: _apiKeyController.text.trim().isNotEmpty ? _apiKeyController.text.trim() : null,
      );

      final result = await ServerConfigService.testConnection(config);
      
      setState(() => _lastTestResult = result);
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(result.message),
            backgroundColor: result.isSuccess ? Colors.green : Colors.red,
          ),
        );
      }
    } finally {
      setState(() => _isTestingConnection = false);
    }
  }

  Future<void> _generateApiKey() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isGeneratingApiKey = true);
    
    try {
      final config = ServerConfig(
        host: _hostController.text.trim(),
        port: int.parse(_portController.text),
        protocol: _useHttps ? 'https' : 'http',
        useHttps: _useHttps,
      );

      final deviceId = 'flutter_pos_${DateTime.now().millisecondsSinceEpoch}';
      final deviceName = 'Flutter POS Device';
      
      final result = await ServerConfigService.generateApiKey(
        config: config,
        deviceId: deviceId,
        deviceName: deviceName,
        permissions: ['read', 'write', 'sell', 'redeem'],
      );
      
      if (result.isSuccess && result.apiKey != null) {
        await ServerConfigService.saveApiKey(result.apiKey!);
        
        setState(() {
          _currentApiKey = result.apiKey;
          _apiKeyController.text = result.apiKey!.displayKey;
        });
        
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('API key generated successfully')),
          );
        }
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(result.message),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    } finally {
      setState(() => _isGeneratingApiKey = false);
    }
  }

  Future<void> _validateApiKey() async {
    if (_apiKeyController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter an API key')),
      );
      return;
    }

    setState(() => _isTestingConnection = true);
    
    try {
      final config = ServerConfig(
        host: _hostController.text.trim(),
        port: int.parse(_portController.text),
        protocol: _useHttps ? 'https' : 'http',
        useHttps: _useHttps,
        apiKey: _apiKeyController.text.trim(),
      );

      final result = await ServerConfigService.validateApiKey(
        config: config,
        apiKey: _apiKeyController.text.trim(),
      );
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(result.message),
            backgroundColor: result.isValid ? Colors.green : Colors.red,
          ),
        );
      }
    } finally {
      setState(() => _isTestingConnection = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Server Configuration'),
        actions: [
          IconButton(
            onPressed: _isLoading ? null : _loadCurrentConfig,
            icon: const Icon(Icons.refresh),
            tooltip: 'Refresh',
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Server Configuration Section
                    Card(
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Server Settings',
                              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: 16.0),
                            TextFormField(
                              controller: _hostController,
                              decoration: const InputDecoration(
                                labelText: 'Host/IP Address',
                                hintText: '127.0.0.1 or your-server.com',
                                prefixIcon: Icon(Icons.computer),
                              ),
                              validator: (value) {
                                if (value == null || value.trim().isEmpty) {
                                  return 'Please enter a host address';
                                }
                                return null;
                              },
                            ),
                        const SizedBox(height: 16),
                            TextFormField(
                              controller: _portController,
                              decoration: const InputDecoration(
                                labelText: 'Port',
                                hintText: '48080',
                                prefixIcon: Icon(Icons.network_check),
                              ),
                              keyboardType: TextInputType.number,
                              inputFormatters: [FilteringTextInputFormatter.digitsOnly],
                              validator: (value) {
                                if (value == null || value.trim().isEmpty) {
                                  return 'Please enter a port number';
                                }
                                final port = int.tryParse(value);
                                if (port == null || port < 1 || port > 65535) {
                                  return 'Please enter a valid port (1-65535)';
                                }
                                return null;
                              },
                            ),
                        const SizedBox(height: 16),
                            SwitchListTile(
                              title: const Text('Use HTTPS'),
                              subtitle: const Text('Enable secure connection'),
                              value: _useHttps,
                              onChanged: (value) {
                                setState(() => _useHttps = value);
                              },
                            ),
                      ],
                    ),

                    const SizedBox(height: 24),

                    // API Key Section
                    Card(
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'API Key',
                              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: 16.0),
                            TextFormField(
                              controller: _apiKeyController,
                              decoration: InputDecoration(
                                labelText: 'API Key',
                                hintText: 'Enter your API key',
                                prefixIcon: const Icon(Icons.key),
                                suffixIcon: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    if (_apiKeyController.text.isNotEmpty)
                                      IconButton(
                                        onPressed: () {
                                          setState(() => _showApiKey = !_showApiKey);
                                        },
                                        icon: Icon(_showApiKey ? Icons.visibility_off : Icons.visibility),
                                      ),
                                    IconButton(
                                      onPressed: () {
                                        Clipboard.setData(ClipboardData(text: _apiKeyController.text));
                                        ScaffoldMessenger.of(context).showSnackBar(
                                          const SnackBar(content: Text('API key copied to clipboard')),
                                        );
                                      },
                                      icon: const Icon(Icons.copy),
                                    ),
                                  ],
                                ),
                              ),
                              obscureText: !_showApiKey && _apiKeyController.text.length > 8,
                            ),
                        const SizedBox(height: 16),
                        Row(
                          children: [
                            Expanded(
                              child: ElevatedButton.icon(
                                onPressed: _isGeneratingApiKey ? null : _generateApiKey,
                                icon: _isGeneratingApiKey 
                                    ? const SizedBox(
                                        width: 16,
                                        height: 16,
                                        child: CircularProgressIndicator(strokeWidth: 2),
                                      )
                                    : const Icon(Icons.add),
                                label: Text(_isGeneratingApiKey ? 'Generating...' : 'Generate'),
                              ),
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: OutlinedButton.icon(
                                onPressed: _isTestingConnection ? null : _validateApiKey,
                                icon: _isTestingConnection 
                                    ? const SizedBox(
                                        width: 16,
                                        height: 16,
                                        child: CircularProgressIndicator(strokeWidth: 2),
                                      )
                                    : const Icon(Icons.check_circle),
                                label: Text(_isTestingConnection ? 'Validating...' : 'Validate'),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),

                    const SizedBox(height: 24),

                    // Connection Test Section
                    Card(
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Connection Test',
                              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: 16.0),
                        if (_lastTestResult != null) ...[
                          Container(
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              color: _lastTestResult!.isSuccess 
                                  ? Colors.green.withOpacity(0.1)
                                  : Colors.red.withOpacity(0.1),
                              borderRadius: BorderRadius.circular(8),
                              border: Border.all(
                                color: _lastTestResult!.isSuccess 
                                    ? Colors.green
                                    : Colors.red,
                              ),
                            ),
                            child: Row(
                              children: [
                                Icon(
                                  _lastTestResult!.isSuccess 
                                      ? Icons.check_circle
                                      : Icons.error,
                                  color: _lastTestResult!.isSuccess 
                                      ? Colors.green
                                      : Colors.red,
                                ),
                                const SizedBox(width: 8),
                                Expanded(
                                  child: Text(
                                    _lastTestResult!.message,
                                    style: TextStyle(
                                      color: _lastTestResult!.isSuccess 
                                          ? Colors.green[800]
                                          : Colors.red[800],
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(height: 16),
                        ],
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton.icon(
                            onPressed: _isTestingConnection ? null : _testConnection,
                            icon: _isTestingConnection 
                                ? const SizedBox(
                                    width: 20,
                                    height: 20,
                                    child: CircularProgressIndicator(strokeWidth: 2),
                                  )
                                : const Icon(Icons.wifi_find),
                            label: Text(_isTestingConnection ? 'Testing...' : 'Test Connection'),
                            style: ElevatedButton.styleFrom(
                              padding: const EdgeInsets.symmetric(vertical: 12),
                            ),
                          ),
                          ],
                        ),
                      ),
                    ),

                    const SizedBox(height: 24),

                    // Save Configuration
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton.icon(
                        onPressed: _saveConfig,
                        icon: const Icon(Icons.save),
                        label: const Text('Save Configuration'),
                        style: ElevatedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 12),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
    );
  }
}
