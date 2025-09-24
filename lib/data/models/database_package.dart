import '../../domain/models/package.dart';

class DatabasePackage {
  final String id;
  final String name;
  final double price;
  final String type;
  final int? quotaOrMinutes;
  final List<String>? bindDeviceIds;
  final DateTime createdAt;
  final DateTime updatedAt;
  final DateTime? syncedAt;

  const DatabasePackage({
    required this.id,
    required this.name,
    required this.price,
    required this.type,
    this.quotaOrMinutes,
    this.bindDeviceIds,
    required this.createdAt,
    required this.updatedAt,
    this.syncedAt,
  });

  factory DatabasePackage.fromDomain(Package package) {
    final now = DateTime.now();
    return DatabasePackage(
      id: package.id,
      name: package.name,
      price: package.price,
      type: package.type,
      quotaOrMinutes: package.quotaOrMinutes,
      bindDeviceIds: package.bindDeviceIds,
      createdAt: now,
      updatedAt: now,
    );
  }

  factory DatabasePackage.fromMap(Map<String, dynamic> map) {
    return DatabasePackage(
      id: map['id'] ?? '',
      name: map['name'] ?? '',
      price: (map['price'] ?? 0).toDouble(),
      type: map['type'] ?? 'single',
      quotaOrMinutes: map['quota_or_minutes'],
      bindDeviceIds: map['allowed_devices'] != null 
          ? (map['allowed_devices'] as String).split(',').where((s) => s.isNotEmpty).toList()
          : null,
      createdAt: DateTime.fromMillisecondsSinceEpoch(map['created_at'] ?? 0),
      updatedAt: DateTime.fromMillisecondsSinceEpoch(map['updated_at'] ?? 0),
      syncedAt: map['synced_at'] != null 
          ? DateTime.fromMillisecondsSinceEpoch(map['synced_at'])
          : null,
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'name': name,
      'price': price,
      'type': type,
      'quota_or_minutes': quotaOrMinutes,
      'allowed_devices': bindDeviceIds?.join(','),
      'created_at': createdAt.millisecondsSinceEpoch,
      'updated_at': updatedAt.millisecondsSinceEpoch,
      'synced_at': syncedAt?.millisecondsSinceEpoch,
    };
  }

  Package toDomain() {
    return Package(
      id: id,
      name: name,
      price: price,
      type: type,
      quotaOrMinutes: quotaOrMinutes,
      bindDeviceIds: bindDeviceIds,
    );
  }

  DatabasePackage copyWith({
    String? id,
    String? name,
    double? price,
    String? type,
    int? quotaOrMinutes,
    List<String>? bindDeviceIds,
    DateTime? createdAt,
    DateTime? updatedAt,
    DateTime? syncedAt,
  }) {
    return DatabasePackage(
      id: id ?? this.id,
      name: name ?? this.name,
      price: price ?? this.price,
      type: type ?? this.type,
      quotaOrMinutes: quotaOrMinutes ?? this.quotaOrMinutes,
      bindDeviceIds: bindDeviceIds ?? this.bindDeviceIds,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      syncedAt: syncedAt ?? this.syncedAt,
    );
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is DatabasePackage && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
}
