-- create table accounts (
--   id              bigint generated always as identity primary key,
--   name            text not null,          -- HDFC Bank, ICICI Credit Card, Cash
--   type            text not null,          -- bank, credit_card, wallet, cash, investment
--   balance         numeric(14,2),
--   currency        text default 'EUR',
--   created_at      timestamptz default now()
-- );

create table categories (
  id              bigint generated always as identity primary key,
  name            text unique not null,
  type            text not null,   -- expense, income, investment, saving
  created_at      timestamptz default now()
);

create table expenses (
  id              bigint generated always as identity primary key,
  date            date not null,
  amount          numeric(12,2) not null,
  currency        text default 'EUR',
  category_id     bigint references categories(id),
  account_id      bigint references accounts(id),
  vendor          text,
  description     text,
  payment_method  text,             -- card, upi, bank, cash
  source          text,             -- manual, pdf, excel, sms
  metadata        jsonb,            -- OCR raw data
  created_at      timestamptz default now()
);

create table income (
  id            bigint generated always as identity primary key,
  date          date not null,
  amount        numeric(12,2) not null,
  currency      text default 'EUR',
  category_id   bigint references categories(id),
  account_id    bigint references accounts(id),
  source        text,                -- salary, freelance, project
  notes         text,
  created_at    timestamptz default now()
);

create table savings (
  id            bigint generated always as identity primary key,
  date          date not null,
  amount        numeric(12,2) not null,
  currency      text default 'EUR',
  account_id    bigint references accounts(id),
  category_id   bigint references categories(id), -- emergency fund etc
  method        text,              -- bank transfer, cash
  goal_id       bigint,            -- link to saving goals table later
  notes         text,
  created_at    timestamptz default now()
);

create table saving_goals (
  id              bigint generated always as identity primary key,
  goal_name       text not null,
  target_amount   numeric(12,2),
  deadline        date,
  notes           text,
  created_at      timestamptz default now()
);

create table investments (
  id                bigint generated always as identity primary key,
  date              date not null,
  amount            numeric(12,2) not null,      -- total invested or redeemed
  currency          text default 'EUR',
  instrument_name   text,                        -- e.g., S&P 500 ETF
  symbol            text,                        -- optional: e.g., AAPL, BTC
  investment_type   text,                        -- equity, crypto, mutual_fund, etf, fd
  units             numeric,                     -- quantity purchased
  price_per_unit    numeric(12,4),
  account_id        bigint references accounts(id),
  category_id       bigint references categories(id),
  action            text not null,               -- 'buy' or 'sell'
  source            text,                        -- broker, pdf, manual
  metadata          jsonb,
  created_at        timestamptz default now()
);

create table investment_returns (
  id                bigint generated always as identity primary key,
  investment_id     bigint references investments(id),
  date              date not null,
  nav               numeric(12,4),               -- NAV or price per unit on that date
  market_value      numeric(14,2),
  profit_loss       numeric(14,2),
  created_at        timestamptz default now()
);

create table recurring_payments (
  id              bigint generated always as identity primary key,
  name            text not null,
  amount          numeric(12,2),
  frequency       text,                         -- monthly, yearly, weekly
  category_id     bigint references categories(id),
  account_id      bigint references accounts(id),
  next_run_date   date,
  notes           text,
  created_at      timestamptz default now()
);

create table budgets (
  id              bigint generated always as identity primary key,
  month           text not null,                -- “2025-01”
  category_id     bigint references categories(id),
  budget_amount   numeric(12,2),
  created_at      timestamptz default now()
);

create table balance_history (
  id              bigint generated always as identity primary key,
  account_id      bigint references accounts(id),
  date            date not null,
  balance         numeric(14,2),
  created_at      timestamptz default now()
);

create table ingestion_logs (
  id              bigint generated always as identity primary key,
  source          text not null,         -- pdf, ocr, email, sms, excel, api
  event           text not null,         -- extracted_text, parsed_fields, inserted
  raw_data        jsonb,
  processed_data  jsonb,
  created_at      timestamptz default now()
);

create table transaction_tags (
  id              bigint generated always as identity primary key,
  expense_id      bigint references expenses(id),
  tag             text,
  created_at      timestamptz default now()
);

---------------------------------------
-- UPGRADE: INVESTMENTS TABLE
---------------------------------------

-- 1. Ensure instrument_name exists
ALTER TABLE investments
ADD COLUMN IF NOT EXISTS instrument_name TEXT;

-- 2. Symbol for stocks/ETFs/crypto
ALTER TABLE investments
ADD COLUMN IF NOT EXISTS symbol TEXT;

-- 3. Investment type (equity, mf, crypto, silver, gold, etc.)
ALTER TABLE investments
ADD COLUMN IF NOT EXISTS investment_type TEXT;

-- 4. Units (for stocks/ETFs/crypto/mutual funds)
ALTER TABLE investments
ADD COLUMN IF NOT EXISTS units NUMERIC;

-- 5. Price per unit
ALTER TABLE investments
ADD COLUMN IF NOT EXISTS price_per_unit NUMERIC(12,4);

-- 6. Metal-specific fields (for silver, gold, platinum)
ALTER TABLE investments
ADD COLUMN IF NOT EXISTS metal_weight NUMERIC;       -- grams or kg

ALTER TABLE investments
ADD COLUMN IF NOT EXISTS metal_purity NUMERIC;       -- e.g., 99.9

ALTER TABLE investments
ADD COLUMN IF NOT EXISTS metal_rate NUMERIC(12,4);   -- price per gram at purchase

-- 7. Buy or sell
ALTER TABLE investments
ADD COLUMN IF NOT EXISTS action TEXT;                -- 'buy' / 'sell'

-- 8. Link to accounts table
ALTER TABLE investments
ADD COLUMN IF NOT EXISTS account_id BIGINT REFERENCES accounts(id);

-- 9. Category link
ALTER TABLE investments
ADD COLUMN IF NOT EXISTS category_id BIGINT REFERENCES categories(id);

-- 10. Metadata (OCR / API raw info)
ALTER TABLE investments
ADD COLUMN IF NOT EXISTS metadata JSONB;


---------------------------------------
-- UPGRADE: INVESTMENT_RETURNS TABLE
---------------------------------------

-- NAV or price per gram/unit
ALTER TABLE investment_returns
ADD COLUMN IF NOT EXISTS nav NUMERIC(12,4);

-- Market value
ALTER TABLE investment_returns
ADD COLUMN IF NOT EXISTS market_value NUMERIC(14,2);

-- Profit / loss at a given date
ALTER TABLE investment_returns
ADD COLUMN IF NOT EXISTS profit_loss NUMERIC(14,2);


---------------------------------------
-- INDEXES FOR PERFORMANCE
---------------------------------------

CREATE INDEX IF NOT EXISTS idx_investments_type
ON investments(investment_type);

CREATE INDEX IF NOT EXISTS idx_investments_date
ON investments(date);

CREATE INDEX IF NOT EXISTS idx_investments_symbol
ON investments(symbol);

CREATE INDEX IF NOT EXISTS idx_investment_returns_date
ON investment_returns(date);
