import '../../domain/models/package.dart';

class PackageRepository {
  static const _mockPackages = [
    Package(id: '1', name: 'Day Pass', price: 350, type: 'timepass', quotaOrMinutes: 480),
    Package(id: '2', name: 'Multi 5', price: 1200, type: 'multi', quotaOrMinutes: 5),
    Package(id: '3', name: 'Single', price: 250, type: 'single', quotaOrMinutes: 1),
    Package(id: '4', name: 'Adult + Kid', price: 500, type: 'bundle', quotaOrMinutes: 2),
    Package(id: '5', name: 'Credit 1000', price: 1000, type: 'credit', quotaOrMinutes: 1000),
    Package(id: '6', name: 'Evening', price: 180, type: 'timepass', quotaOrMinutes: 240),
  ];

  Future<List<Package>> getAllPackages() async {
    // Simulate network delay
    await Future.delayed(const Duration(milliseconds: 100));
    return _mockPackages;
  }

  Future<Package?> getPackageById(String id) async {
    await Future.delayed(const Duration(milliseconds: 50));
    try {
      return _mockPackages.firstWhere((p) => p.id == id);
    } catch (e) {
      return null;
    }
  }
}
