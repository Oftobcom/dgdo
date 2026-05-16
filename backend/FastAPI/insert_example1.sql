-- =====================================================
-- DG Do — Seed Data (MVP)
-- PostgreSQL + PostGIS
-- =====================================================

-- =====================================================
-- 1. USERS (unified identity)
-- =====================================================
INSERT INTO users (id, role, phone, email, password_hash, is_active) VALUES
('11111111-1111-1111-1111-111111111111', 'passenger', '+12345678901', 'alice@example.com',       'hash_alice', true),
('22222222-2222-2222-2222-222222222222', 'passenger', '+12345678902', 'bob@example.com',         'hash_bob',   true),
('33333333-3333-3333-3333-333333333333', 'driver',    '+12345678903', 'carol_driver@example.com','hash_carol', true),
('44444444-4444-4444-4444-444444444444', 'driver',    '+12345678904', 'dave_driver@example.com', 'hash_dave',  true),
('55555555-5555-5555-5555-555555555555', 'admin',     '+12345678905', 'admin@example.com',       'hash_admin', true);

-- =====================================================
-- 2. PASSENGERS
-- =====================================================
INSERT INTO passengers (user_id, full_name, rating) VALUES
('11111111-1111-1111-1111-111111111111', 'Alice Passenger', 4.9),
('22222222-2222-2222-2222-222222222222', 'Bob Passenger',   4.7);

-- =====================================================
-- 3. DRIVERS
-- =====================================================
INSERT INTO drivers (user_id, full_name, license_number, is_verified, rating) VALUES
('33333333-3333-3333-3333-333333333333', 'Carol Driver', 'LIC123456', true,  4.8),
('44444444-4444-4444-4444-444444444444', 'Dave Driver',  'LIC789012', false, 4.5);

-- =====================================================
-- 4. ADMINS
-- =====================================================
INSERT INTO admins (user_id, full_name, admin_level) VALUES
('55555555-5555-5555-5555-555555555555', 'Admin User', 'super');

-- =====================================================
-- 5. VEHICLES
-- =====================================================
INSERT INTO vehicles (id, driver_id, brand, model, plate_number, color, is_active) VALUES
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '33333333-3333-3333-3333-333333333333', 'Toyota', 'Camry', 'ABC123', 'Silver', true),
('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', '44444444-4444-4444-4444-444444444444', 'Honda',  'Civic', 'XYZ789', 'Red',    true);

-- =====================================================
-- 6. DRIVER_STATUS (realtime state)
-- BUG FIX: Dave trip 'accepted' holatida → 'on_trip' bo'lishi kerak,
--          Carol trip 'completed' → 'available' to'g'ri edi.
-- =====================================================
INSERT INTO driver_status (driver_id, status, current_location, updated_at) VALUES
('33333333-3333-3333-3333-333333333333', 'available', ST_SetSRID(ST_MakePoint(69.2401, 41.3815), 4326), now()),
('44444444-4444-4444-4444-444444444444', 'on_trip',   ST_SetSRID(ST_MakePoint(69.2500, 41.3900), 4326), now());

-- =====================================================
-- 7. TRIPS
-- =====================================================
INSERT INTO trips (
    id, passenger_id, driver_id, status,
    pickup_location, dropoff_location,
    estimated_fare, final_fare,
    requested_at, accepted_at, completed_at, cancelled_at
) VALUES
-- Trip 1: completed (Alice → Carol)
('77777777-7777-7777-7777-777777777777',
 '11111111-1111-1111-1111-111111111111',
 '33333333-3333-3333-3333-333333333333',
 'completed',
 ST_SetSRID(ST_MakePoint(69.2401, 41.3815), 4326),
 ST_SetSRID(ST_MakePoint(69.2800, 41.4000), 4326),
 12.50, 12.50,
 '2025-01-15 10:00:00', '2025-01-15 10:01:00', '2025-01-15 10:20:00', NULL),

-- Trip 2: accepted (Bob → Dave)
('88888888-8888-8888-8888-888888888888',
 '22222222-2222-2222-2222-222222222222',
 '44444444-4444-4444-4444-444444444444',
 'accepted',
 ST_SetSRID(ST_MakePoint(69.2500, 41.3900), 4326),
 ST_SetSRID(ST_MakePoint(69.2600, 41.3950), 4326),
 8.00, NULL,
 '2025-01-16 14:30:00', '2025-01-16 14:32:00', NULL, NULL),

-- Trip 3: requested (Alice, hali haydovchi yo'q)
('99999999-9999-9999-9999-999999999999',
 '11111111-1111-1111-1111-111111111111',
 NULL,
 'requested',
 ST_SetSRID(ST_MakePoint(69.2401, 41.3815), 4326),
 ST_SetSRID(ST_MakePoint(69.3000, 41.4200), 4326),
 15.00, NULL,
 '2025-01-17 09:00:00', NULL, NULL, NULL);

-- =====================================================
-- 8. MATCHING_EVENTS
-- =====================================================
INSERT INTO matching_events (id, trip_id, driver_id, result, created_at) VALUES
('cccccccc-cccc-cccc-cccc-cccccccccccc',
 '77777777-7777-7777-7777-777777777777',
 '33333333-3333-3333-3333-333333333333',
 'accepted', '2025-01-15 10:00:30'),

('dddddddd-dddd-dddd-dddd-dddddddddddd',
 '88888888-8888-8888-8888-888888888888',
 '44444444-4444-4444-4444-444444444444',
 'accepted', '2025-01-16 14:31:00'),

-- Trip 3: Carol'ga taklif qilindi, hali javob yo'q
('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee',
 '99999999-9999-9999-9999-999999999999',
 '33333333-3333-3333-3333-333333333333',
 'offered', '2025-01-17 09:00:10');

-- =====================================================
-- 9. WALLETS
-- =====================================================
INSERT INTO wallets (id, user_id, owner_type, balance, currency, is_active) VALUES
('aaaaaaaa-1111-1111-1111-111111111111', '11111111-1111-1111-1111-111111111111', 'passenger', 50.00,  'TJS', true),
('aaaaaaaa-2222-2222-2222-222222222222', '22222222-2222-2222-2222-222222222222', 'passenger', 30.00,  'TJS', true),
('aaaaaaaa-3333-3333-3333-333333333333', '33333333-3333-3333-3333-333333333333', 'driver',    120.00, 'TJS', true),
('aaaaaaaa-4444-4444-4444-444444444444', '44444444-4444-4444-4444-444444444444', 'driver',    80.00,  'TJS', true);

-- =====================================================
-- 10. WALLET_TRANSACTIONS
-- =====================================================
INSERT INTO wallet_transactions (
    id, wallet_id, trip_id, type, status,
    amount, currency, balance_before, balance_after, description, created_at
) VALUES
-- Alice (passenger) to'lovi
('bbbbbbbb-1111-1111-1111-111111111111',
 'aaaaaaaa-1111-1111-1111-111111111111',
 '77777777-7777-7777-7777-777777777777',
 'payment', 'success',
 12.50, 'TJS', 62.50, 50.00,
 'Payment for trip 77777777', '2025-01-15 10:21:00'),

-- Carol (driver) daromadi
('bbbbbbbb-3333-3333-3333-333333333333',
 'aaaaaaaa-3333-3333-3333-333333333333',
 '77777777-7777-7777-7777-777777777777',
 'driver_earning', 'success',
 12.50, 'TJS', 107.50, 120.00,
 'Earning for trip 77777777', '2025-01-15 10:21:00');

-- =====================================================
-- 11. PAYMENTS
-- =====================================================
INSERT INTO payments (id, trip_id, wallet_transaction_id, amount, currency, payment_method, status, created_at) VALUES
('ffffffff-ffff-ffff-ffff-ffffffffffff',
 '77777777-7777-7777-7777-777777777777',
 'bbbbbbbb-1111-1111-1111-111111111111',
 12.50, 'TJS', 'wallet', 'success',
 '2025-01-15 10:21:00');
 
-- =====================================================
-- 12. REVIEWS
-- =====================================================
INSERT INTO reviews (id, trip_id, reviewer_id, reviewee_id, rating, comment, created_at) VALUES
-- Alice → Carol (yo'lovchi haydovchini baholaydi)
('aaaaaaaa-1111-aaaa-1111-aaaaaaaa1111',
 '77777777-7777-7777-7777-777777777777',
 '11111111-1111-1111-1111-111111111111',
 '33333333-3333-3333-3333-333333333333',
 5, 'Great ride, very professional',
 '2025-01-15 10:25:00'),

-- Carol → Alice (haydovchi yo'lovchini baholaydi)
('aaaaaaaa-2222-aaaa-2222-aaaaaaaa2222',
 '77777777-7777-7777-7777-777777777777',
 '33333333-3333-3333-3333-333333333333',
 '11111111-1111-1111-1111-111111111111',
 5, 'Polite and punctual passenger',
 '2025-01-15 10:26:00');

-- =====================================================
-- 13. AUDIT_LOG
-- =====================================================
INSERT INTO audit_log (id, user_id, action, entity_type, entity_id, created_at) VALUES
('bbbbbbbb-2222-bbbb-2222-bbbbbbbb2222',
 '55555555-5555-5555-5555-555555555555',
 'TRIP_CREATED', 'Trip',
 '77777777-7777-7777-7777-777777777777', now()),

('cccccccc-3333-cccc-3333-cccccccc3333',
 '55555555-5555-5555-5555-555555555555',
 'PAYMENT_VERIFIED', 'Payment',
 'ffffffff-ffff-ffff-ffff-ffffffffffff', now()),

('dddddddd-4444-dddd-4444-dddddddd4444',
 '55555555-5555-5555-5555-555555555555',
 'TRIP_CREATED', 'Trip',
 '88888888-8888-8888-8888-888888888888', now()),

('eeeeeeee-5555-eeee-5555-eeeeeeee5555',
 '55555555-5555-5555-5555-555555555555',
 'TRIP_CREATED', 'Trip',
 '99999999-9999-9999-9999-999999999999', now());
