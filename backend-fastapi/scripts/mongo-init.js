// MongoDB Initialization Script for PlayPark API
// This script creates the initial database structure and demo data

// Switch to playpark database
db = db.getSiblingDB('playpark');

// Create demo tenant
db.tenants.insertOne({
    tenant_id: "tenant_demo_01",
    name: "PlayPark Demo",
    status: "active",
    settings: {
        currency: "THB",
        timezone: "Asia/Bangkok",
        language: "th"
    },
    created_at: new Date(),
    updated_at: new Date()
});

// Create demo store
db.stores.insertOne({
    store_id: "store_demo_01",
    tenant_id: "tenant_demo_01",
    name: "PlayPark Main Store",
    address: "123 Play Street, Bangkok 10110",
    timezone: "Asia/Bangkok",
    currency: "THB",
    status: "active",
    settings: {
        operating_hours: "09:00-21:00",
        max_capacity: 100
    },
    created_at: new Date(),
    updated_at: new Date()
});

// Create demo devices
const devices = [
    {
        device_id: "pos-device-001",
        tenant_id: "tenant_demo_01",
        store_id: "store_demo_01",
        name: "POS Terminal 1",
        type: "POS",
        capabilities: ["can_sell", "can_redeem", "can_refund"],
        status: "active",
        last_seen: new Date(),
        settings: {
            receipt_printer: true,
            cash_drawer: true
        },
        created_at: new Date(),
        updated_at: new Date()
    },
    {
        device_id: "gate-device-001",
        tenant_id: "tenant_demo_01",
        store_id: "store_demo_01",
        name: "Entry Gate 1",
        type: "GATE",
        capabilities: ["can_redeem"],
        status: "active",
        last_seen: new Date(),
        settings: {
            gate_type: "turnstile",
            access_control: true
        },
        created_at: new Date(),
        updated_at: new Date()
    },
    {
        device_id: "kiosk-device-001",
        tenant_id: "tenant_demo_01",
        store_id: "store_demo_01",
        name: "Self-Service Kiosk 1",
        type: "KIOSK",
        capabilities: ["can_sell"],
        status: "active",
        last_seen: new Date(),
        settings: {
            touch_screen: true,
            card_reader: true,
            receipt_printer: true
        },
        created_at: new Date(),
        updated_at: new Date()
    }
];

db.devices.insertMany(devices);

// Create demo roles
const roles = [
    {
        role_id: "role_manager",
        tenant_id: "tenant_demo_01",
        name: "Manager",
        description: "Store manager with full access",
        permissions: [
            "sell", "redeem", "refund", "reprint",
            "view_reports", "manage_employees", "manage_settings"
        ],
        is_system: false,
        status: "active",
        created_at: new Date(),
        updated_at: new Date()
    },
    {
        role_id: "role_cashier",
        tenant_id: "tenant_demo_01",
        name: "Cashier",
        description: "Cashier with sales access",
        permissions: [
            "sell", "redeem", "refund", "reprint"
        ],
        is_system: false,
        status: "active",
        created_at: new Date(),
        updated_at: new Date()
    }
];

db.roles.insertMany(roles);

// Create demo employee
db.employees.insertOne({
    employee_id: "emp_001",
    tenant_id: "tenant_demo_01",
    store_id: "store_demo_01",
    name: "Demo Manager",
    email: "manager@playpark.demo",
    pin: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4f2C5z7V3q", // "1234"
    roles: ["role_manager"],
    status: "active",
    permissions: [
        "sell", "redeem", "refund", "reprint",
        "view_reports", "manage_employees", "manage_settings"
    ],
    settings: {
        language: "th",
        timezone: "Asia/Bangkok"
    },
    created_at: new Date(),
    updated_at: new Date()
});

// Create demo packages
const packages = [
    {
        package_id: "pkg_001",
        tenant_id: "tenant_demo_01",
        store_id: "store_demo_01",
        name: "Single Entry",
        description: "One-time entry ticket",
        type: "single",
        price: 150,
        quota_or_minutes: 1,
        active: true,
        visible_on: ["POS", "KIOSK"],
        access_zones: ["main_area"],
        settings: {
            valid_days: 30,
            refundable: true
        },
        created_at: new Date(),
        updated_at: new Date()
    },
    {
        package_id: "pkg_002",
        tenant_id: "tenant_demo_01",
        store_id: "store_demo_01",
        name: "5-Entry Pass",
        description: "Five-time entry pass",
        type: "multi",
        price: 600,
        quota_or_minutes: 5,
        active: true,
        visible_on: ["POS", "KIOSK"],
        access_zones: ["main_area"],
        settings: {
            valid_days: 30,
            refundable: true,
            discount: 0.2
        },
        created_at: new Date(),
        updated_at: new Date()
    },
    {
        package_id: "pkg_003",
        tenant_id: "tenant_demo_01",
        store_id: "store_demo_01",
        name: "VIP Day Pass",
        description: "All-day VIP access",
        type: "time_based",
        price: 500,
        quota_or_minutes: 480, // 8 hours in minutes
        active: true,
        visible_on: ["POS"],
        access_zones: ["main_area", "vip_area"],
        settings: {
            valid_days: 1,
            refundable: false,
            vip_benefits: true
        },
        created_at: new Date(),
        updated_at: new Date()
    }
];

db.packages.insertMany(packages);

// Create demo pricing rules
const pricing_rules = [
    {
        rule_id: "rule_001",
        tenant_id: "tenant_demo_01",
        store_id: "store_demo_01",
        name: "Early Bird Discount",
        description: "10% discount for early morning visits",
        kind: "line_percent",
        params: {
            discount_percent: 10,
            time_window: "06:00-10:00"
        },
        priority: 1,
        active: true,
        conditions: {
            time_range: {
                start: "06:00",
                end: "10:00"
            }
        },
        settings: {
            max_discount: 50,
            min_purchase: 100
        },
        created_at: new Date(),
        updated_at: new Date()
    },
    {
        rule_id: "rule_002",
        tenant_id: "tenant_demo_01",
        store_id: "store_demo_01",
        name: "Bulk Discount",
        description: "15% discount for 5+ items",
        kind: "cart_percent",
        params: {
            discount_percent: 15,
            min_quantity: 5
        },
        priority: 2,
        active: true,
        conditions: {
            min_quantity: 5
        },
        settings: {
            max_discount: 200,
            applicable_packages: ["pkg_001", "pkg_002"]
        },
        created_at: new Date(),
        updated_at: new Date()
    }
];

db.pricing_rules.insertMany(pricing_rules);

// Create indexes for better performance
db.sales.createIndex({"tenant_id": 1, "store_id": 1, "timestamp": -1});
db.sales.createIndex({"sale_id": 1}, {"unique": true});
db.sales.createIndex({"reference": 1}, {"unique": true});

db.tickets.createIndex({"ticket_id": 1}, {"unique": true});
db.tickets.createIndex({"qr_token": 1}, {"unique": true});
db.tickets.createIndex({"tenant_id": 1, "store_id": 1});
db.tickets.createIndex({"sale_id": 1, "status": 1});

db.audit_logs.createIndex({"tenant_id": 1, "timestamp": -1});
db.audit_logs.createIndex({"event_type": 1, "timestamp": -1});
db.audit_logs.createIndex({"actor_id": 1});

db.users.createIndex({"email": 1}, {"unique": true});
db.users.createIndex({"employee_id": 1}, {"unique": true});
db.users.createIndex({"tenant_id": 1, "store_id": 1});

db.devices.createIndex({"device_id": 1}, {"unique": true});
db.devices.createIndex({"tenant_id": 1, "store_id": 1});

db.packages.createIndex({"package_id": 1}, {"unique": true});
db.packages.createIndex({"tenant_id": 1, "store_id": 1, "active": 1});

// Print success message
print("PlayPark database initialization completed successfully!");
print("Demo data created:");
print("- 1 tenant (tenant_demo_01)");
print("- 1 store (store_demo_01)");
print("- 3 devices (POS, Gate, Kiosk)");
print("- 2 roles (Manager, Cashier)");
print("- 1 employee (manager@playpark.demo / PIN: 1234)");
print("- 3 packages (Single Entry, 5-Entry Pass, VIP Day Pass)");
print("- 2 pricing rules (Early Bird, Bulk Discount)");
print("- Database indexes created");
