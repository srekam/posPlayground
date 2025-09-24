// MongoDB initialization script
// This script creates the initial database structure and seed data

// Switch to the playpark database
db = db.getSiblingDB('playpark');

// Create collections with validation
db.createCollection('tenants');
db.createCollection('stores');
db.createCollection('devices');
db.createCollection('employees');
db.createCollection('roles');
db.createCollection('memberships');
db.createCollection('packages');
db.createCollection('pricingrules');
db.createCollection('accesszones');
db.createCollection('tickets');
db.createCollection('redemptions');
db.createCollection('sales');
db.createCollection('shifts');
db.createCollection('refunds');
db.createCollection('reprints');
db.createCollection('auditlogs');
db.createCollection('settings');
db.createCollection('webhookdeliveries');
db.createCollection('outboxevents');

// Create indexes for better performance
print('Creating indexes...');

// Tenants
db.tenants.createIndex({ "tenant_id": 1 }, { unique: true });

// Stores
db.stores.createIndex({ "store_id": 1 }, { unique: true });
db.stores.createIndex({ "tenant_id": 1 });

// Devices
db.devices.createIndex({ "device_id": 1 }, { unique: true });
db.devices.createIndex({ "device_token_hash": 1 }, { unique: true });
db.devices.createIndex({ "tenant_id": 1, "store_id": 1 });

// Employees
db.employees.createIndex({ "employee_id": 1 }, { unique: true });
db.employees.createIndex({ "email": 1 }, { unique: true });
db.employees.createIndex({ "tenant_id": 1 });

// Roles
db.roles.createIndex({ "role_id": 1 }, { unique: true });
db.roles.createIndex({ "name": 1 }, { unique: true });

// Memberships
db.memberships.createIndex({ "employee_id": 1, "store_id": 1 });

// Packages
db.packages.createIndex({ "package_id": 1 }, { unique: true });
db.packages.createIndex({ "tenant_id": 1, "store_id": 1 });
db.packages.createIndex({ "active": 1 });

// Pricing Rules
db.pricingrules.createIndex({ "rule_id": 1 }, { unique: true });
db.pricingrules.createIndex({ "scope": 1, "scope_id": 1 });
db.pricingrules.createIndex({ "active": 1, "priority": -1 });

// Tickets
db.tickets.createIndex({ "ticket_id": 1 }, { unique: true });
db.tickets.createIndex({ "qr_token": 1 }, { unique: true });
db.tickets.createIndex({ "short_code": 1 }, { unique: true });
db.tickets.createIndex({ "tenant_id": 1, "store_id": 1 });
db.tickets.createIndex({ "sale_id": 1 });
db.tickets.createIndex({ "status": 1 });
db.tickets.createIndex({ "valid_from": 1, "valid_to": 1 });

// Redemptions
db.redemptions.createIndex({ "redemption_id": 1 }, { unique: true });
db.redemptions.createIndex({ "ticket_id": 1 });
db.redemptions.createIndex({ "device_id": 1 });
db.redemptions.createIndex({ "timestamp": 1 });

// Sales
db.sales.createIndex({ "sale_id": 1 }, { unique: true });
db.sales.createIndex({ "reference": 1 }, { unique: true, sparse: true });
db.sales.createIndex({ "tenant_id": 1, "store_id": 1 });
db.sales.createIndex({ "timestamp": 1 });

// Shifts
db.shifts.createIndex({ "shift_id": 1 }, { unique: true });
db.shifts.createIndex({ "store_id": 1, "device_id": 1 });
db.shifts.createIndex({ "status": 1 });

// Audit Logs
db.auditlogs.createIndex({ "audit_id": 1 }, { unique: true });
db.auditlogs.createIndex({ "timestamp": 1 });
db.auditlogs.createIndex({ "event_type": 1 });
db.auditlogs.createIndex({ "tenant_id": 1, "store_id": 1, "timestamp": 1 });

// Settings
db.settings.createIndex({ "settings_id": 1 }, { unique: true });
db.settings.createIndex({ "scope": 1, "scope_id": 1 }, { unique: true });

// Webhook Deliveries
db.webhookdeliveries.createIndex({ "delivery_id": 1 }, { unique: true });
db.webhookdeliveries.createIndex({ "status": 1 });
db.webhookdeliveries.createIndex({ "next_retry_at": 1 });

// Outbox Events
db.outboxevents.createIndex({ "event_id": 1 }, { unique: true });
db.outboxevents.createIndex({ "device_id": 1, "status": 1 });
db.outboxevents.createIndex({ "created_at": 1 });

print('Indexes created successfully');

// Create default tenant and store
print('Creating default tenant and store...');

const tenantId = 'tenant_01HQ7XKQM0Z3N2YXVBW5EXAMPLE';
const storeId = 'store_01HQ7XKQM0Z3N2YXVBW5EXAMPLE';

// Insert default tenant
db.tenants.insertOne({
  tenant_id: tenantId,
  name: 'PlayPark Demo',
  legal_name: 'PlayPark Indoor Playground Ltd.',
  timezone: 'Asia/Bangkok',
  currency: 'THB',
  billing_plan: 'premium',
  status: 'active',
  created_at: new Date(),
  updated_at: new Date()
});

// Insert default store
db.stores.insertOne({
  store_id: storeId,
  tenant_id: tenantId,
  name: 'PlayPark Main Store',
  address: {
    street: '123 Playground Street',
    city: 'Bangkok',
    state: 'Bangkok',
    postal_code: '10110',
    country: 'Thailand'
  },
  timezone: 'Asia/Bangkok',
  receipt_header: 'PlayPark\nIndoor Playground',
  receipt_footer: 'Thank you for visiting!\nCome back soon!',
  active: true,
  created_at: new Date(),
  updated_at: new Date()
});

// Create default roles
print('Creating default roles...');

const roles = [
  {
    role_id: 'role_cashier',
    name: 'Cashier',
    permissions: ['sell', 'redeem'],
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    role_id: 'role_supervisor',
    name: 'Supervisor',
    permissions: ['sell', 'redeem', 'refund', 'reprint', 'manual_discount', 'shift_open', 'shift_close'],
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    role_id: 'role_manager',
    name: 'Manager',
    permissions: ['sell', 'redeem', 'refund', 'reprint', 'manual_discount', 'shift_open', 'shift_close', 'settings_write', 'employee_manage', 'reports_view'],
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    role_id: 'role_admin',
    name: 'Administrator',
    permissions: ['sell', 'redeem', 'refund', 'reprint', 'manual_discount', 'shift_open', 'shift_close', 'settings_write', 'employee_manage', 'reports_view', 'admin_access'],
    created_at: new Date(),
    updated_at: new Date()
  }
];

db.roles.insertMany(roles);

// Create sample packages
print('Creating sample packages...');

const packages = [
  {
    package_id: 'pkg_01HQ7XKQM0Z3N2YXVBW5PKG001',
    tenant_id: tenantId,
    store_id: storeId,
    name: 'Single Entry',
    type: 'single',
    price: 150,
    quota_or_minutes: 1,
    visible_on: ['POS', 'KIOSK'],
    active: true,
    description: 'Single entry ticket for playground access',
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    package_id: 'pkg_01HQ7XKQM0Z3N2YXVBW5PKG002',
    tenant_id: tenantId,
    store_id: storeId,
    name: '5-Entry Pass',
    type: 'multi',
    price: 600,
    quota_or_minutes: 5,
    visible_on: ['POS', 'KIOSK'],
    active: true,
    description: 'Multi-entry pass with 5 uses',
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    package_id: 'pkg_01HQ7XKQM0Z3N2YXVBW5PKG003',
    tenant_id: tenantId,
    store_id: storeId,
    name: '2-Hour Pass',
    type: 'timepass',
    price: 250,
    quota_or_minutes: 120,
    visible_on: ['POS', 'KIOSK'],
    active: true,
    description: '2-hour unlimited access pass',
    created_at: new Date(),
    updated_at: new Date()
  },
  {
    package_id: 'pkg_01HQ7XKQM0Z3N2YXVBW5PKG004',
    tenant_id: tenantId,
    store_id: storeId,
    name: 'Birthday Party Package',
    type: 'bundle',
    price: 1500,
    quota_or_minutes: 1,
    visible_on: ['POS'],
    active: true,
    description: 'Complete birthday party package for up to 10 kids',
    created_at: new Date(),
    updated_at: new Date()
  }
];

db.packages.insertMany(packages);

// Create default settings
print('Creating default settings...');

db.settings.insertOne({
  settings_id: 'settings_tenant_default',
  scope: 'tenant',
  scope_id: tenantId,
  features: {
    kiosk: true,
    gate_binding: true,
    multi_price: true,
    webhooks: true,
    offline_sync: true
  },
  billing: {
    plan: 'premium',
    trial_start: new Date(),
    trial_end: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)
  },
  payment_types: {
    cash: { enabled: true, surcharge: 0 },
    qr: { enabled: true, surcharge: 0 },
    card: { enabled: true, surcharge: 0 },
    other: { enabled: false, surcharge: 0 }
  },
  taxes: {
    inclusive: true,
    rates: [
      { name: 'VAT', rate: 0.07, default: true }
    ]
  },
  receipt: {
    header: 'PlayPark\nIndoor Playground',
    footer: 'Thank you for visiting!\nCome back soon!',
    paper_width: 80
  },
  created_at: new Date(),
  updated_at: new Date()
});

print('Database initialization completed successfully!');
print('Default tenant ID: ' + tenantId);
print('Default store ID: ' + storeId);
print('Created 4 sample packages');
print('Created 4 default roles');
print('MongoDB setup complete!');
