# Life OS - Financial Tracker Implementation Plan

## Goal Description
Build a modular "Life OS" starting with a **Financial Tracker**. The application will be built with **Streamlit** and **Supabase**.
**Long-term Vision**: Extend to Personal Development, Career Goals, Travel, etc.
**Future Capabilities**: AI-powered data ingestion (LangChain) for processing bills/receipts.
**Current Focus**: Minimal, useful, and aesthetic financial tracker.

## User Review Required
> [!IMPORTANT]
> **Database Setup**: I will create the necessary tables in Supabase using the SQL editor or client.
> **Credentials**: Received and will be stored in `.streamlit/secrets.toml`.

## Proposed Changes

### Configuration
#### [NEW] [.streamlit/secrets.toml](file:///c:/Users/User/OneDrive/Desktop/Personal/MIne/Personal%20Trackings/LifeOs/.streamlit/secrets.toml)
- Store Supabase URL and Key.

### Database Schema (Supabase)
**User Provided Schema** (Already Setup):
- **accounts**: `id`, `name`, `type`, `balance`, `currency`
- **categories**: `id`, `name`, `type`
- **expenses**: `id`, `date`, `amount`, `category_id`, `account_id`, `vendor`, `description`, `payment_method`, `source`, `metadata`
- **income**: `id`, `date`, `amount`, `category_id`, `account_id`, `source`, `notes`
- **savings**: `id`, `date`, `amount`, `account_id`, `category_id`, `method`, `goal_id`, `notes`
- **saving_goals**: `id`, `goal_name`, `target_amount`, `deadline`, `notes`
- **investments**: `id`, `date`, `amount`, `instrument_name`, `symbol`, `investment_type`, `units`, `price_per_unit`, `account_id`, `category_id`, `action`, `source`, `metadata`
- **investment_returns**: `id`, `investment_id`, `date`, `nav`, `market_value`, `profit_loss`
- **recurring_payments**, **budgets**, **balance_history**, **ingestion_logs**, **transaction_tags`

### SaaS Foundation (Auth & RLS)
#### [MODIFY] Database Schema (Supabase)
- [x] Enable **Row Level Security (RLS)** on all tables.
- [x] Add `user_id` column (foreign key to `auth.users`) to: `expenses`, `income`, `savings_goals`, `investments`, `accounts`, `categories`.
- [x] Create Policies: Users can only select/insert/update/delete their own rows.

#### [NEW] [pages/login.py](file:///c:/Users/User/OneDrive/Desktop/Personal/MIne/Personal%20Trackings/LifeOs/pages/login.py)
- [x] Login/Signup form using Supabase Auth.
- [x] Session management.

#### [NEW] [pages/admin.py](file:///c:/Users/User/OneDrive/Desktop/Personal/MIne/Personal%20Trackings/LifeOs/pages/admin.py)
- [x] Admin-only view (protected by role check).
- [x] View all users, system stats.

### AI Features (LangChain + Groq)
#### [NEW] [core/ai_client.py](file:///c:/Users/User/OneDrive/Desktop/Personal/MIne/Personal%20Trackings/LifeOs/core/ai_client.py)
- [x] Initialize LangChain ChatGroq client.
- [x] Support for Text and Vision models.

#### [NEW] [pages/smart_ingest.py](file:///c:/Users/User/OneDrive/Desktop/Personal/MIne/Personal%20Trackings/LifeOs/pages/smart_ingest.py)
- [x] Text Input: Paste receipt text -> JSON.
- [x] Image Input: Upload receipt image -> Vision AI -> JSON.

### Product Pivot (Web App)
#### [NEW] [database/migration_product.sql](file:///c:/Users/User/OneDrive/Desktop/Personal/MIne/Personal%20Trackings/LifeOs/database/migration_product.sql)
- [x] `profiles` table for user details.
- [x] Auto-trigger to create profile on signup.

#### [MODIFY] [pages/login.py](file:///c:/Users/User/OneDrive/Desktop/Personal/MIne/Personal%20Trackings/LifeOs/pages/login.py)
- [x] Add "Full Name" to signup.
- [x] Pass metadata to Supabase Auth.
- Define prompt templates for receipt parsing.

#### [NEW] [pages/smart_ingest.py](file:///c:/Users/User/OneDrive/Desktop/Personal/MIne/Personal%20Trackings/LifeOs/pages/smart_ingest.py)
- UI for uploading receipts/invoices (PDF/Image/Text).
- Logic to invoke AI agent and parse data into JSON.
- "Review & Save" button to insert into Supabase.

### UI Scalability
#### [MODIFY] [app.py](file:///c:/Users/User/OneDrive/Desktop/Personal/MIne/Personal%20Trackings/LifeOs/app.py)
- **Modular Sidebar**: Group pages by "Module" (Finance, Personal, Work).
- **Design System**: Refine CSS for a consistent, premium look (Cards, Typography).

### Core Logic (`core/`)
#### [MODIFY] [supabase_client.py](file:///c:/Users/User/OneDrive/Desktop/Personal/MIne/Personal%20Trackings/LifeOs/core/supabase_client.py)
- Initialize Supabase client.

#### [MODIFY] [finance_queries.py](file:///c:/Users/User/OneDrive/Desktop/Personal/MIne/Personal%20Trackings/LifeOs/core/finance_queries.py)
- Implement CRUD operations supporting foreign keys (`category_id`, `account_id`).
- Add helper functions to fetch `categories` and `accounts` for UI dropdowns.

### User Interface (`pages/` & `app.py`)
#### [MODIFY] [app.py](file:///c:/Users/User/OneDrive/Desktop/Personal/MIne/Personal%20Trackings/LifeOs/app.py)
- **Main Dashboard**: High-level summary (Net Worth, Monthly Spend).
- **Sidebar Navigation**: Designed to accommodate future modules (e.g., "Finance", "Personal Dev").

#### [MODIFY] [expenses.py](file:///c:/Users/User/OneDrive/Desktop/Personal/MIne/Personal%20Trackings/LifeOs/pages/expenses.py)
- **Add Expense**: Simple form.
- **View Expenses**: Data table with filtering.
- *Future*: "Upload Bill" button (placeholder for AI feature).

#### [MODIFY] [income.py](file:///c:/Users/User/OneDrive/Desktop/Personal/MIne/Personal%20Trackings/LifeOs/pages/income.py)
- Track income sources.

#### [MODIFY] [savings.py](file:///c:/Users/User/OneDrive/Desktop/Personal/MIne/Personal%20Trackings/LifeOs/pages/savings.py)
- Visual progress bars for goals.

#### [MODIFY] [investments.py](file:///c:/Users/User/OneDrive/Desktop/Personal/MIne/Personal%20Trackings/LifeOs/pages/investments.py)
- Portfolio overview.

#### [MODIFY] [analytics.py](file:///c:/Users/User/OneDrive/Desktop/Personal/MIne/Personal%20Trackings/LifeOs/pages/analytics.py)
- Spending breakdown and trends.

### Module: Personal Development & ROI
#### [NEW] [database/migration_personal.sql](file:///c:/Users/User/OneDrive/Desktop/Personal/MIne/Personal%20Trackings/LifeOs/database/migration_personal.sql)
- **`life_goals` Table**:
    - `id`, `user_id`, `title`, `description`, `category` (Health, Career, Social, Hobby), `target_date`, `status` (Active, Completed, Dropped).
- **`activities` Table** (The types of things you do):
    - `id`, `user_id`, `name`, `goal_id` (optional link), `default_happiness` (1-10), `return_type` (Financial, Emotional/Inner Peace, Health, Social, None), `impact_score` (1-10 estimate of overall life-value).
- **`activity_logs` Table**:
    - `id`, `user_id`, `activity_id`, `date`, `duration_minutes`, `happiness_score` (actual feeling), `impact_score` (actual value), `notes`.

#### [NEW] [pages/personal_goals.py](file:///c:/Users/User/OneDrive/Desktop/Personal/MIne/Personal%20Trackings/LifeOs/pages/personal_goals.py)
- **Goal Setting**: Create and manage high-level life goals.
- **Activity Library**: Define standard activities (e.g., "Gym", "Coding", "Netflix") with their default "ROI parameters".

#### [NEW] [pages/tracker.py](file:///c:/Users/User/OneDrive/Desktop/Personal/MIne/Personal%20Trackings/LifeOs/pages/tracker.py)
- **Daily Logger**: Quick entry form to log what you did today.
- **Sliders**: For Happiness (Current Feel) and Productivity/ROI.

#### [NEW] [pages/life_roi.py](file:///c:/Users/User/OneDrive/Desktop/Personal/MIne/Personal%20Trackings/LifeOs/pages/life_roi.py)
- **Scatter Plot**: "Happiness vs. Impact" matrix.
    - Top Right (High Happy, High Impact) = Keep doing.
    - Top Left (Low Happy, High Impact) = Grind/Discipline.
    - Bottom Right (High Happy, Low Impact) = Guilty Pleasures.
    - Bottom Left (Low Happy, Low Impact) = Eliminate.
- **Time Analysis**: Where is your time going vs. where is your value coming from?

### UI Overhaul (Top Navigation)
#### [MODIFY] [core/navigation.py](file:///c:/Users/User/OneDrive/Desktop/Personal/MIne/Personal%20Trackings/LifeOs/core/navigation.py)
- **Top Navigation Bar**: Replace sidebar with a two-tier top navigation system.
    - **Tier 1 (Modules)**: Finance | Personal Dev | AI Tools | System
    - **Tier 2 (Pages)**: Dynamic buttons based on selected module.
- **Styling**: `styles.css` (injected) for a modern, navbar look.
- **User Profile**: Move to top-right corner.

#### [MODIFY] [.streamlit/config.toml](file:///c:/Users/User/OneDrive/Desktop/Personal/MIne/Personal%20Trackings/LifeOs/.streamlit/config.toml)
- Ensure `client.showSidebarNavigation = False`.

#### [MODIFY] [app.py](file:///c:/Users/User/OneDrive/Desktop/Personal/MIne/Personal%20Trackings/LifeOs/app.py) & All Pages
- Ensure `setup_navigation()` is called.

## Verification Plan

### Automated Tests
- `python tests/test_connection.py`: Verify Supabase connection.

### Manual Verification
1.  **Setup**: `pip install streamlit supabase pandas plotly`
2.  **Run**: `streamlit run app.py`
3.  **Verify**:
    - Connect to Supabase.
    - Create an expense item.
    - Verify it appears on the dashboard.
