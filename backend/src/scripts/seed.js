const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const crypto = require('crypto');
require('dotenv').config();

const { Tenant, Store, Device, Employee, Membership } = require('../models/core');
const { Package } = require('../models/catalog');
const logger = require('../utils/logger');

async function seedDatabase() {
  try {
    // Connect to MongoDB
    await mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/playpark');
    console.log('Connected to MongoDB');

    // Check if data already exists
    const existingTenant = await Tenant.findOne();
    if (existingTenant) {
      console.log('Database already seeded. Skipping...');
      process.exit(0);
    }

    // Create demo tenant
    const tenant = new Tenant({
      tenant_id: 'tenant_demo_01',
      name: 'PlayPark Demo',
      legal_name: 'PlayPark Indoor Playground Ltd.',
      timezone: 'Asia/Bangkok',
      currency: 'THB',
      billing_plan: 'premium',
      status: 'active'
    });
    await tenant.save();
    console.log('✓ Created demo tenant');

    // Create demo store
    const store = new Store({
      store_id: 'store_demo_01',
      tenant_id: tenant.tenant_id,
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
      active: true
    });
    await store.save();
    console.log('✓ Created demo store');

    // Create demo employee (manager)
    const pinHash = await bcrypt.hash('1234', 12);
    const employee = new Employee({
      employee_id: 'emp_demo_manager',
      tenant_id: tenant.tenant_id,
      name: 'Demo Manager',
      email: 'manager@playpark.demo',
      pin_hash: pinHash,
      status: 'active'
    });
    await employee.save();
    console.log('✓ Created demo manager employee');

    // Create demo devices
    const devices = [
      {
        device_id: 'dev_pos_01',
        tenant_id: tenant.tenant_id,
        store_id: store.store_id,
        type: 'POS',
        name: 'POS Terminal 1',
        device_token_hash: crypto.createHash('sha256').update('pos-token-1').digest('hex'),
        capabilities: {
          can_sell: true,
          can_redeem: false,
          kiosk_mode: false,
          offline_cap: true
        }
      },
      {
        device_id: 'dev_gate_01',
        tenant_id: tenant.tenant_id,
        store_id: store.store_id,
        type: 'GATE',
        name: 'Entry Gate 1',
        device_token_hash: crypto.createHash('sha256').update('gate-token-1').digest('hex'),
        capabilities: {
          can_sell: false,
          can_redeem: true,
          kiosk_mode: false,
          offline_cap: true
        }
      },
      {
        device_id: 'dev_kiosk_01',
        tenant_id: tenant.tenant_id,
        store_id: store.store_id,
        type: 'KIOSK',
        name: 'Self-Service Kiosk 1',
        device_token_hash: crypto.createHash('sha256').update('kiosk-token-1').digest('hex'),
        capabilities: {
          can_sell: true,
          can_redeem: false,
          kiosk_mode: true,
          offline_cap: false
        }
      }
    ];

    for (const deviceData of devices) {
      const device = new Device(deviceData);
      await device.save();
    }
    console.log('✓ Created demo devices (POS, Gate, Kiosk)');

    // Create demo packages
    const packages = [
      {
        package_id: 'pkg_single_entry',
        tenant_id: tenant.tenant_id,
        store_id: store.store_id,
        name: 'Single Entry',
        type: 'single',
        price: 150,
        quota_or_minutes: 1,
        visible_on: ['POS', 'KIOSK'],
        active: true,
        description: 'Single entry ticket for playground access'
      },
      {
        package_id: 'pkg_5_entry_pass',
        tenant_id: tenant.tenant_id,
        store_id: store.store_id,
        name: '5-Entry Pass',
        type: 'multi',
        price: 600,
        quota_or_minutes: 5,
        visible_on: ['POS', 'KIOSK'],
        active: true,
        description: 'Multi-entry pass with 5 uses'
      },
      {
        package_id: 'pkg_2_hour_pass',
        tenant_id: tenant.tenant_id,
        store_id: store.store_id,
        name: '2-Hour Pass',
        type: 'timepass',
        price: 250,
        quota_or_minutes: 120,
        visible_on: ['POS', 'KIOSK'],
        active: true,
        description: '2-hour unlimited access pass'
      },
      {
        package_id: 'pkg_birthday_party',
        tenant_id: tenant.tenant_id,
        store_id: store.store_id,
        name: 'Birthday Party Package',
        type: 'bundle',
        price: 1500,
        quota_or_minutes: 1,
        visible_on: ['POS'],
        active: true,
        description: 'Complete birthday party package for up to 10 kids'
      }
    ];

    for (const packageData of packages) {
      const pkg = new Package(packageData);
      await pkg.save();
    }
    console.log('✓ Created demo packages');

    console.log('\n🎉 Database seeding completed successfully!');
    console.log('\n📋 Demo Credentials:');
    console.log('Tenant ID:', tenant.tenant_id);
    console.log('Store ID:', store.store_id);
    console.log('Manager Email: manager@playpark.demo');
    console.log('Manager PIN: 1234');
    console.log('\n🔐 Site Key for Device Registration:');
    console.log(`${tenant.tenant_id}:${store.store_id}:demo-secret-key`);
    console.log('\n📱 Device Tokens:');
    console.log('POS Token: pos-token-1');
    console.log('Gate Token: gate-token-1');
    console.log('Kiosk Token: kiosk-token-1');
    console.log('\n✅ Ready to start the backend server!');

  } catch (error) {
    console.error('❌ Seeding failed:', error);
    process.exit(1);
  } finally {
    await mongoose.disconnect();
  }
}

// Run seeding
seedDatabase();
