class Package {
  final String id;
  final String name;
  final double price;
  final String type;
  final int? quotaOrMinutes;
  final List<String>? bindDeviceIds;

  const Package({
    required this.id,
    required this.name,
    required this.price,
    required this.type,
    this.quotaOrMinutes,
    this.bindDeviceIds,
  });

  String get priceText => '฿${price.toStringAsFixed(0)}';

  Package copyWith({
    String? id,
    String? name,
    double? price,
    String? type,
    int? quotaOrMinutes,
    List<String>? bindDeviceIds,
  }) {
    return Package(
      id: id ?? this.id,
      name: name ?? this.name,
      price: price ?? this.price,
      type: type ?? this.type,
      quotaOrMinutes: quotaOrMinutes ?? this.quotaOrMinutes,
      bindDeviceIds: bindDeviceIds ?? this.bindDeviceIds,
    );
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Package && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
}
