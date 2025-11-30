-- Enable RLS on all tables
ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE income ENABLE ROW LEVEL SECURITY;
ALTER TABLE investments ENABLE ROW LEVEL SECURITY;
ALTER TABLE saving_goals ENABLE ROW LEVEL SECURITY;
ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;

-- Add user_id column to all tables
ALTER TABLE expenses ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id);
ALTER TABLE income ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id);
ALTER TABLE investments ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id);
ALTER TABLE saving_goals ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id);
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id);
ALTER TABLE categories ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id);

-- Create RLS Policies (Users can only see/edit their own data)

-- Expenses
CREATE POLICY "Users can view own expenses" ON expenses FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own expenses" ON expenses FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own expenses" ON expenses FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own expenses" ON expenses FOR DELETE USING (auth.uid() = user_id);

-- Income
CREATE POLICY "Users can view own income" ON income FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own income" ON income FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own income" ON income FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own income" ON income FOR DELETE USING (auth.uid() = user_id);

-- Investments
CREATE POLICY "Users can view own investments" ON investments FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own investments" ON investments FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own investments" ON investments FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own investments" ON investments FOR DELETE USING (auth.uid() = user_id);

-- Savings Goals
CREATE POLICY "Users can view own savings" ON saving_goals FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own savings" ON saving_goals FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own savings" ON saving_goals FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own savings" ON saving_goals FOR DELETE USING (auth.uid() = user_id);

-- Accounts
CREATE POLICY "Users can view own accounts" ON accounts FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own accounts" ON accounts FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own accounts" ON accounts FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own accounts" ON accounts FOR DELETE USING (auth.uid() = user_id);

-- Categories
CREATE POLICY "Users can view own categories" ON categories FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own categories" ON categories FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own categories" ON categories FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own categories" ON categories FOR DELETE USING (auth.uid() = user_id);
