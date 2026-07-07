-- ============================================================
-- Personal Expense Analytics System
-- PostgreSQL schema for production deployment
-- ============================================================

BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ============================================================
-- USERS
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id              SERIAL PRIMARY KEY,
    email           VARCHAR(120) NOT NULL UNIQUE,
    username        VARCHAR(80) NOT NULL UNIQUE,
    password_hash   VARCHAR(256) NOT NULL,
    profile_image   VARCHAR(200),
    is_admin        BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users (username);

-- ============================================================
-- EXPENSES
-- ============================================================
CREATE TABLE IF NOT EXISTS expenses (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    entry_date      DATE NOT NULL DEFAULT CURRENT_DATE,
    category        VARCHAR(80) NOT NULL,
    description     TEXT,
    tags            VARCHAR(200),
    amount          NUMERIC(10,2) NOT NULL CHECK (amount >= 0),
    payment_method  VARCHAR(50),
    location        VARCHAR(120),
    notes           TEXT,
    attachment_path VARCHAR(200),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_expenses_user_id ON expenses (user_id);
CREATE INDEX IF NOT EXISTS idx_expenses_entry_date ON expenses (entry_date DESC);
CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses (category);
CREATE INDEX IF NOT EXISTS idx_expenses_payment_method ON expenses (payment_method);

-- keep updated_at current
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_expenses_updated_at ON expenses;
CREATE TRIGGER trg_expenses_updated_at
BEFORE UPDATE ON expenses
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

-- ============================================================
-- INCOMES
-- ============================================================
CREATE TABLE IF NOT EXISTS incomes (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    entry_date      DATE NOT NULL DEFAULT CURRENT_DATE,
    source          VARCHAR(80) NOT NULL,
    amount          NUMERIC(10,2) NOT NULL CHECK (amount >= 0),
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_incomes_user_id ON incomes (user_id);
CREATE INDEX IF NOT EXISTS idx_incomes_entry_date ON incomes (entry_date DESC);
CREATE INDEX IF NOT EXISTS idx_incomes_source ON incomes (source);

DROP TRIGGER IF EXISTS trg_incomes_updated_at ON incomes;
CREATE TRIGGER trg_incomes_updated_at
BEFORE UPDATE ON incomes
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

-- ============================================================
-- BUDGETS
-- ============================================================
CREATE TABLE IF NOT EXISTS budgets (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    month           DATE NOT NULL,
    total_amount    NUMERIC(10,2) NOT NULL CHECK (total_amount >= 0),
    category        VARCHAR(80),
    used_amount     NUMERIC(10,2) NOT NULL DEFAULT 0 CHECK (used_amount >= 0),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT budgets_month_first_day CHECK (EXTRACT(DAY FROM month) = 1)
);

CREATE INDEX IF NOT EXISTS idx_budgets_user_id ON budgets (user_id);
CREATE INDEX IF NOT EXISTS idx_budgets_month ON budgets (month DESC);
CREATE INDEX IF NOT EXISTS idx_budgets_category ON budgets (category);

DROP TRIGGER IF EXISTS trg_budgets_updated_at ON budgets;
CREATE TRIGGER trg_budgets_updated_at
BEFORE UPDATE ON budgets
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

-- ============================================================
-- NOTIFICATIONS
-- ============================================================
CREATE TABLE IF NOT EXISTS notifications (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title       VARCHAR(120) NOT NULL,
    message     TEXT NOT NULL,
    is_read     BOOLEAN NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications (user_id);

-- ============================================================
-- USER SETTINGS
-- ============================================================
CREATE TABLE IF NOT EXISTS user_settings (
    id                  SERIAL PRIMARY KEY,
    user_id             INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    currency            VARCHAR(10) NOT NULL DEFAULT 'INR',
    timezone            VARCHAR(64) NOT NULL DEFAULT 'Asia/Calcutta',
    theme               VARCHAR(32) NOT NULL DEFAULT 'system',
    email_notifications BOOLEAN NOT NULL DEFAULT TRUE,
    weekly_reports      BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_settings_user_id ON user_settings (user_id);

-- ============================================================
-- PASSWORD RESET TOKENS
-- ============================================================
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token       VARCHAR(255) NOT NULL UNIQUE,
    expires_at  TIMESTAMPTZ NOT NULL,
    used_at     TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_user_id ON password_reset_tokens (user_id);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_token ON password_reset_tokens (token);

-- ============================================================
-- EMAIL VERIFICATION TOKENS
-- ============================================================
CREATE TABLE IF NOT EXISTS email_verification_tokens (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token       VARCHAR(255) NOT NULL UNIQUE,
    expires_at  TIMESTAMPTZ NOT NULL,
    verified_at TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_email_verification_tokens_user_id ON email_verification_tokens (user_id);
CREATE INDEX IF NOT EXISTS idx_email_verification_tokens_token ON email_verification_tokens (token);

-- ============================================================
-- OPTIONAL VIEW: budget usage summary
-- ============================================================
CREATE OR REPLACE VIEW budget_summary AS
SELECT
    b.id,
    b.user_id,
    b.month,
    b.category,
    b.total_amount,
    b.used_amount,
    ROUND(
        CASE
            WHEN b.total_amount = 0 THEN 0
            ELSE (b.used_amount / b.total_amount) * 100
        END,
        2
    ) AS used_percent
FROM budgets b;

COMMIT;
