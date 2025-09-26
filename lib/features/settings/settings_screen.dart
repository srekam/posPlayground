import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../../core/theme/tokens.dart';
import 'providers/settings_provider.dart';
import 'offline_test_screen.dart';

class SettingsScreen extends HookConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settings = ref.watch(settingsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
        actions: [
          IconButton(
            onPressed: () => Navigator.of(context).pop(),
            icon: const Icon(Icons.close),
            tooltip: 'Close',
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(Spacing.md),
        children: [
          // Theme Section
          _SettingsSection(
            title: 'Theme',
            icon: Icons.palette,
            children: [
              _ThemeOption(
                title: 'Dark',
                subtitle: 'Dark theme',
                isSelected: settings.themeMode == ThemeMode.dark,
                onTap: () => ref
                    .read(settingsProvider.notifier)
                    .setThemeMode(ThemeMode.dark),
              ),
              _ThemeOption(
                title: 'Light',
                subtitle: 'Light theme',
                isSelected: settings.themeMode == ThemeMode.light,
                onTap: () => ref
                    .read(settingsProvider.notifier)
                    .setThemeMode(ThemeMode.light),
              ),
              _ThemeOption(
                title: 'Lollipop',
                subtitle: 'Colorful theme',
                isSelected: settings.themeMode == ThemeMode.system &&
                    settings.colorScheme == 'lollipop',
                onTap: () => ref
                    .read(settingsProvider.notifier)
                    .setColorScheme('lollipop'),
              ),
              _ThemeOption(
                title: 'Monochrome',
                subtitle: 'Black & white theme',
                isSelected: settings.themeMode == ThemeMode.system &&
                    settings.colorScheme == 'monochrome',
                onTap: () => ref
                    .read(settingsProvider.notifier)
                    .setColorScheme('monochrome'),
              ),
            ],
          ),

          const SizedBox(height: Spacing.lg),

          // Language Section
          _SettingsSection(
            title: 'Language',
            icon: Icons.language,
            children: [
              _LanguageOption(
                title: 'English',
                subtitle: 'English',
                isSelected: settings.language == 'en',
                onTap: () =>
                    ref.read(settingsProvider.notifier).setLanguage('en'),
              ),
              _LanguageOption(
                title: 'ไทย',
                subtitle: 'Thai',
                isSelected: settings.language == 'th',
                onTap: () =>
                    ref.read(settingsProvider.notifier).setLanguage('th'),
              ),
            ],
          ),

          const SizedBox(height: Spacing.lg),

          // Background Section
          _SettingsSection(
            title: 'Background',
            icon: Icons.image,
            children: [
              SwitchListTile(
                title: const Text('Background Image'),
                subtitle: const Text('Show playground background'),
                value: settings.showBackgroundImage,
                onChanged: (value) => ref
                    .read(settingsProvider.notifier)
                    .setShowBackgroundImage(value),
                secondary: const Icon(Icons.image),
              ),
            ],
          ),

          const SizedBox(height: Spacing.lg),

          // Client Features Section
          _SettingsSection(
            title: 'Client Features',
            icon: Icons.smartphone,
            children: [
              ListTile(
                leading: const Icon(Icons.storage, color: Colors.blue),
                title: const Text('Offline Mode'),
                subtitle: const Text('Test offline functionality'),
                onTap: () => Navigator.of(context).push(
                  MaterialPageRoute(builder: (_) => const OfflineTestScreen()),
                ),
              ),
              ListTile(
                leading: const Icon(Icons.info, color: Colors.green),
                title: const Text('App Information'),
                subtitle: const Text('Version and app details'),
                onTap: () => _showAppInfoDialog(context),
              ),
            ],
          ),

          const SizedBox(height: Spacing.lg),

          // Reset Section
          _SettingsSection(
            title: 'Reset',
            icon: Icons.restore,
            children: [
              ListTile(
                leading: const Icon(Icons.restore, color: Colors.orange),
                title: const Text('Reset to Default'),
                subtitle: const Text('Reset all settings to default values'),
                onTap: () => _showResetDialog(context, ref),
              ),
            ],
          ),
        ],
      ),
    );
  }

  void _showResetDialog(BuildContext context, WidgetRef ref) {
    showDialog(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Reset Settings'),
        content: const Text(
            'Are you sure you want to reset all settings to default values?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(dialogContext).pop(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(dialogContext).pop();
              ref.read(settingsProvider.notifier).resetToDefault();
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Settings reset to default')),
              );
            },
            child: const Text('Reset'),
          ),
        ],
      ),
    );
  }

  void _showAppInfoDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('App Information'),
        content: const Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('PlayPark POS Client',
                style: TextStyle(fontWeight: FontWeight.bold)),
            SizedBox(height: 8),
            Text('Version: 1.0.0'),
            Text('Platform: Web'),
            Text('Build: Debug'),
            SizedBox(height: 16),
            Text('Features:', style: TextStyle(fontWeight: FontWeight.bold)),
            Text('• Point of Sale'),
            Text('• Offline Mode'),
            Text('• Multi-language Support'),
            Text('• Adaptive UI'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }
}

class _SettingsSection extends StatelessWidget {
  final String title;
  final IconData icon;
  final List<Widget> children;

  const _SettingsSection({
    required this.title,
    required this.icon,
    required this.children,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(Spacing.md),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, color: Theme.of(context).colorScheme.primary),
                const SizedBox(width: Spacing.sm),
                Text(
                  title,
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
              ],
            ),
            const SizedBox(height: Spacing.sm),
            ...children,
          ],
        ),
      ),
    );
  }
}

class _ThemeOption extends StatelessWidget {
  final String title;
  final String subtitle;
  final bool isSelected;
  final VoidCallback onTap;

  const _ThemeOption({
    required this.title,
    required this.subtitle,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      title: Text(title),
      subtitle: Text(subtitle),
      trailing:
          isSelected ? const Icon(Icons.check, color: Colors.green) : null,
      onTap: onTap,
    );
  }
}

class _LanguageOption extends StatelessWidget {
  final String title;
  final String subtitle;
  final bool isSelected;
  final VoidCallback onTap;

  const _LanguageOption({
    required this.title,
    required this.subtitle,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      title: Text(title),
      subtitle: Text(subtitle),
      trailing:
          isSelected ? const Icon(Icons.check, color: Colors.green) : null,
      onTap: onTap,
    );
  }
}
