import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../../../domain/models/package.dart';
import '../../../data/repositories/package_repository.dart';

final packageRepositoryProvider = Provider<PackageRepository>((ref) {
  return PackageRepository();
});

final packagesProvider = FutureProvider<List<Package>>((ref) async {
  final repository = ref.watch(packageRepositoryProvider);
  return await repository.getAllPackages();
});
