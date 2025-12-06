-- Migration for Personal Development Module
-- Helps track Goals, Activities, and Life ROI (Happiness/Impact)

-- 1. Life Goals Table
-- High-level targets (e.g., "Run a Marathon", "Learn Spanish", "Retire by 40")
CREATE TABLE IF NOT EXISTS life_goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT CHECK (category IN ('Health', 'Career', 'Financial', 'Social', 'Hobby', 'Personal Development', 'Other')),
    target_date DATE,
    status TEXT CHECK (status IN ('Active', 'Completed', 'Dropped', 'On Hold')) DEFAULT 'Active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. Activities Table
-- The library of things you do (e.g., "Gym", "Coding", "Meditation")
-- default_happiness: Your expected happiness from this (1-10)
-- return_type: The primary type of value this generates
CREATE TABLE IF NOT EXISTS activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) NOT NULL,
    name TEXT NOT NULL,
    goal_id UUID REFERENCES life_goals(id), -- Optional link to a parent goal
    default_happiness INTEGER CHECK (default_happiness BETWEEN 1 AND 10),
    return_type TEXT CHECK (return_type IN ('Financial', 'Emotional/Inner Peace', 'Health', 'Social', 'Skill', 'None')),
    impact_score INTEGER CHECK (impact_score BETWEEN 1 AND 10), -- Estimate of overall life-value
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 3. Activity Logs Table
-- Daily log of what you actually did
CREATE TABLE IF NOT EXISTS activity_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) NOT NULL,
    activity_id UUID REFERENCES activities(id) NOT NULL,
    date DATE DEFAULT CURRENT_DATE NOT NULL,
    duration_minutes INTEGER,
    happiness_score INTEGER CHECK (happiness_score BETWEEN 1 AND 10), -- How it actually felt
    impact_score INTEGER CHECK (impact_score BETWEEN 1 AND 10), -- Actual value derived
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Enable Row Level Security (RLS)
ALTER TABLE life_goals ENABLE ROW LEVEL SECURITY;
ALTER TABLE activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_logs ENABLE ROW LEVEL SECURITY;

-- Create Policies
-- Users can only see/edit their own data

-- Life Goals Policies
CREATE POLICY "Users can view their own life_goals" ON life_goals FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own life_goals" ON life_goals FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own life_goals" ON life_goals FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete their own life_goals" ON life_goals FOR DELETE USING (auth.uid() = user_id);

-- Activities Policies
CREATE POLICY "Users can view their own activities" ON activities FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own activities" ON activities FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own activities" ON activities FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete their own activities" ON activities FOR DELETE USING (auth.uid() = user_id);

-- Activity Logs Policies
CREATE POLICY "Users can view their own activity_logs" ON activity_logs FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own activity_logs" ON activity_logs FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own activity_logs" ON activity_logs FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete their own activity_logs" ON activity_logs FOR DELETE USING (auth.uid() = user_id);
