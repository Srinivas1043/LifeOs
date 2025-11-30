-- Create Exchange Rates Table
CREATE TABLE IF NOT EXISTS exchange_rates (
    currency_code TEXT PRIMARY KEY,
    rate_to_eur NUMERIC NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert Default Rates (Base: EUR)
INSERT INTO exchange_rates (currency_code, rate_to_eur) VALUES
('EUR', 1.0),
('USD', 0.92),
('GBP', 1.17),
('INR', 0.011)
ON CONFLICT (currency_code) DO UPDATE SET rate_to_eur = EXCLUDED.rate_to_eur;

-- Enable RLS on exchange_rates (Public read, Admin write)
ALTER TABLE exchange_rates ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Everyone can read rates" ON exchange_rates FOR SELECT USING (true);

-- Add Currency Columns to Transactions
ALTER TABLE expenses ADD COLUMN IF NOT EXISTS currency TEXT DEFAULT 'EUR';
ALTER TABLE expenses ADD COLUMN IF NOT EXISTS amount_eur NUMERIC;

ALTER TABLE income ADD COLUMN IF NOT EXISTS currency TEXT DEFAULT 'EUR';
ALTER TABLE income ADD COLUMN IF NOT EXISTS amount_eur NUMERIC;

ALTER TABLE investments ADD COLUMN IF NOT EXISTS currency TEXT DEFAULT 'EUR';
ALTER TABLE investments ADD COLUMN IF NOT EXISTS amount_eur NUMERIC;
