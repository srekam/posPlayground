import 'dart:convert';
import '../../domain/models/ticket.dart';

class DatabaseSale {
  final String id;
  final String shiftId;
  final String employeeId;
  final double totalAmount;
  final String paymentMethod;
  final String? paymentReference;
  final List<SaleItem> items;
  final DateTime createdAt;
  final DateTime updatedAt;
  final DateTime? syncedAt;

  const DatabaseSale({
    required this.id,
    required this.shiftId,
    required this.employeeId,
    required this.totalAmount,
    required this.paymentMethod,
    this.paymentReference,
    required this.items,
    required this.createdAt,
    required this.updatedAt,
    this.syncedAt,
  });

  factory DatabaseSale.fromMap(Map<String, dynamic> map) {
    return DatabaseSale(
      id: map['id'] ?? '',
      shiftId: map['shift_id'] ?? '',
      employeeId: map['employee_id'] ?? '',
      totalAmount: (map['total_amount'] ?? 0).toDouble(),
      paymentMethod: map['payment_method'] ?? 'cash',
      paymentReference: map['payment_reference'],
      items: map['items'] != null 
          ? (jsonDecode(map['items']) as List)
              .map((item) => SaleItem.fromJson(item))
              .toList()
          : [],
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
      'shift_id': shiftId,
      'employee_id': employeeId,
      'total_amount': totalAmount,
      'payment_method': paymentMethod,
      'payment_reference': paymentReference,
      'items': jsonEncode(items.map((item) => item.toJson()).toList()),
      'created_at': createdAt.millisecondsSinceEpoch,
      'updated_at': updatedAt.millisecondsSinceEpoch,
      'synced_at': syncedAt?.millisecondsSinceEpoch,
    };
  }

  DatabaseSale copyWith({
    String? id,
    String? shiftId,
    String? employeeId,
    double? totalAmount,
    String? paymentMethod,
    String? paymentReference,
    List<SaleItem>? items,
    DateTime? createdAt,
    DateTime? updatedAt,
    DateTime? syncedAt,
  }) {
    return DatabaseSale(
      id: id ?? this.id,
      shiftId: shiftId ?? this.shiftId,
      employeeId: employeeId ?? this.employeeId,
      totalAmount: totalAmount ?? this.totalAmount,
      paymentMethod: paymentMethod ?? this.paymentMethod,
      paymentReference: paymentReference ?? this.paymentReference,
      items: items ?? this.items,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      syncedAt: syncedAt ?? this.syncedAt,
    );
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is DatabaseSale && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
}

class SaleItem {
  final String packageId;
  final String packageName;
  final double price;
  final int quantity;
  final double discount;

  const SaleItem({
    required this.packageId,
    required this.packageName,
    required this.price,
    required this.quantity,
    this.discount = 0.0,
  });

  double get lineTotal => (price * quantity) - discount;

  factory SaleItem.fromJson(Map<String, dynamic> json) {
    return SaleItem(
      packageId: json['package_id'] ?? '',
      packageName: json['package_name'] ?? '',
      price: (json['price'] ?? 0).toDouble(),
      quantity: json['quantity'] ?? 1,
      discount: (json['discount'] ?? 0).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'package_id': packageId,
      'package_name': packageName,
      'price': price,
      'quantity': quantity,
      'discount': discount,
    };
  }
}
