BEGIN;

INSERT INTO users (email, username, password_hash, is_admin)
VALUES
    ('admin@example.com', 'admin', '$2b$12$examplehashreplaceinproduction', TRUE),
    ('user@example.com', 'demo_user', '$2b$12$examplehashreplaceinproduction', FALSE)
ON CONFLICT (email) DO NOTHING;

INSERT INTO expenses (user_id, entry_date, category, description, amount, payment_method, location, notes)
SELECT id, '2026-07-01', 'Food', 'Lunch with friends', 320.00, 'UPI', 'Campus area', 'Weekend meal'
FROM users WHERE email = 'admin@example.com'
UNION ALL
SELECT id, '2026-07-02', 'Transport', 'Auto to station', 85.00, 'Cash', 'City center', NULL
FROM users WHERE email = 'admin@example.com'
UNION ALL
SELECT id, '2026-07-03', 'Utilities', 'Mobile recharge', 499.00, 'Card', 'Online', 'Monthly recharge'
FROM users WHERE email = 'user@example.com';

INSERT INTO incomes (user_id, entry_date, source, amount, notes)
SELECT id, '2026-07-01', 'Salary', 45000.00, 'Monthly salary'
FROM users WHERE email = 'admin@example.com'
UNION ALL
SELECT id, '2026-07-01', 'Freelance', 12000.00, 'UI project'
FROM users WHERE email = 'user@example.com';

INSERT INTO budgets (user_id, month, total_amount, category, used_amount)
SELECT id, '2026-07-01', 15000.00, 'Food', 4200.00
FROM users WHERE email = 'admin@example.com'
UNION ALL
SELECT id, '2026-07-01', 5000.00, 'Transport', 1200.00
FROM users WHERE email = 'admin@example.com'
UNION ALL
SELECT id, '2026-07-01', 10000.00, NULL, 3600.00
FROM users WHERE email = 'user@example.com';

COMMIT;
