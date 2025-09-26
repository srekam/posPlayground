import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';

import '../../data/database/database_test_helper.dart';
import '../../data/repositories/offline_package_repository.dart';
import '../../domain/models/package.dart';

class OfflineTestScreen extends HookConsumerWidget {
  const OfflineTestScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Offline Test'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              'Database Test Functions',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),

            // Database Status
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Database Status',
                        style: TextStyle(fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    FutureBuilder<bool>(
                      future: DatabaseTestHelper.isDatabaseInitialized(),
                      builder: (context, snapshot) {
                        if (snapshot.hasData) {
                          return Row(
                            children: [
                              Icon(
                                snapshot.data!
                                    ? Icons.check_circle
                                    : Icons.error,
                                color:
                                    snapshot.data! ? Colors.green : Colors.red,
                              ),
                              const SizedBox(width: 8),
                              Text(snapshot.data!
                                  ? 'Database initialized'
                                  : 'Database not initialized'),
                            ],
                          );
                        }
                        return const CircularProgressIndicator();
                      },
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 16),

            // Database Stats
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Database Statistics',
                        style: TextStyle(fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    FutureBuilder<Map<String, int>>(
                      future: DatabaseTestHelper.getDatabaseStats(),
                      builder: (context, snapshot) {
                        if (snapshot.hasData) {
                          final stats = snapshot.data!;
                          return Column(
                            children: [
                              _StatRow('Packages', stats['packages'] ?? 0),
                              _StatRow('Tickets', stats['tickets'] ?? 0),
                              _StatRow('Sales', stats['sales'] ?? 0),
                              _StatRow(
                                  'Outbox Events', stats['outbox_events'] ?? 0),
                            ],
                          );
                        }
                        return const CircularProgressIndicator();
                      },
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 16),

            // Test Actions
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Test Actions',
                        style: TextStyle(fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        Expanded(
                          child: ElevatedButton(
                            onPressed: () async {
                              await DatabaseTestHelper.populateTestData();
                              if (context.mounted) {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(
                                      content: Text('Test data populated')),
                                );
                              }
                            },
                            child: const Text('Populate Test Data'),
                          ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: ElevatedButton(
                            onPressed: () async {
                              await DatabaseTestHelper.clearTestData();
                              if (context.mounted) {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(
                                      content: Text('Test data cleared')),
                                );
                              }
                            },
                            child: const Text('Clear Test Data'),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    ElevatedButton(
                      onPressed: () async {
                        await _testOfflinePackageRepository(context);
                      },
                      child: const Text('Test Offline Package Repository'),
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 16),

            // Test Results
            Expanded(
              child: Card(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Test Results',
                          style: TextStyle(fontWeight: FontWeight.bold)),
                      const SizedBox(height: 8),
                      Expanded(
                        child: FutureBuilder<List<Package>>(
                          future: OfflinePackageRepository().getAllPackages(),
                          builder: (context, snapshot) {
                            if (snapshot.hasData) {
                              final packages = snapshot.data!;
                              if (packages.isEmpty) {
                                return const Center(
                                  child: Text(
                                      'No packages found. Try populating test data.'),
                                );
                              }

                              return ListView.builder(
                                itemCount: packages.length,
                                itemBuilder: (context, index) {
                                  final package = packages[index];
                                  return ListTile(
                                    title: Text(package.name),
                                    subtitle: Text(
                                        '${package.priceText} • ${package.type}'),
                                    trailing: package.quotaOrMinutes != null
                                        ? Text('${package.quotaOrMinutes}')
                                        : null,
                                  );
                                },
                              );
                            }

                            if (snapshot.hasError) {
                              return Center(
                                child: Text('Error: ${snapshot.error}'),
                              );
                            }

                            return const Center(
                                child: CircularProgressIndicator());
                          },
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _StatRow extends StatelessWidget {
  final String label;
  final int count;

  const _StatRow(this.label, this.count);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label),
          Text('$count'),
        ],
      ),
    );
  }
}

Future<void> _testOfflinePackageRepository(BuildContext context) async {
  final repository = OfflinePackageRepository();

  try {
    // Test creating a package
    final testPackage = DatabaseTestHelper.createTestPackage();
    await repository.savePackage(testPackage);

    // Test retrieving packages
    final packages = await repository.getAllPackages();

    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Success! Found ${packages.length} packages'),
          backgroundColor: Colors.green,
        ),
      );
    }
  } catch (e) {
    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }
}
