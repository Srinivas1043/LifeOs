# Life OS - Financial Tracker Walkthrough

## Overview
Your **Life OS Financial Tracker** is ready! It connects to your Supabase database and allows you to track expenses, income, savings, and investments.

## How to Run
1.  Open your terminal in VS Code.
2.  Ensure your virtual environment is active (if you use one).
3.  Run the following command:
    ```bash
    streamlit run app.py
    ```

## Getting Started
### 1. Configure Settings (First Step)
Before adding any transactions, you must set up your **Accounts** and **Categories**.
- Go to the **Settings** page (sidebar).
- **Add Accounts**: e.g., "HDFC Bank", "Cash Wallet".
- **Add Categories**: e.g., "Food" (Expense), "Salary" (Income), "Stocks" (Investment).

### 2. Add Transactions
- **Expenses**: Go to the Expenses page to log daily spending.
- **Income**: Log your salary or other income sources.
- **Investments**: Track your portfolio purchases (Stocks, Crypto, etc.).

### 3. View Analytics & Tax
# Life OS - Financial Tracker Walkthrough

## Overview
Your **Life OS Financial Tracker** is ready! It connects to your Supabase database and allows you to track expenses, income, savings, and investments.

## How to Run
1.  Open your terminal in VS Code.
2.  Ensure your virtual environment is active (if you use one).
3.  Run the following command:
    ```bash
    streamlit run app.py
    ```

## Getting Started
### 1. Configure Settings (First Step)
Before adding any transactions, you must set up your **Accounts** and **Categories**.
- Go to the **Settings** page (sidebar).
- **Add Accounts**: e.g., "HDFC Bank", "Cash Wallet".
- **Add Categories**: e.g., "Food" (Expense), "Salary" (Income), "Stocks" (Investment).

### 2. Add Transactions
- **Expenses**: Go to the Expenses page to log daily spending.
- **Income**: Log your salary or other income sources.
- **Investments**: Track your portfolio purchases (Stocks, Crypto, etc.).

### 3. View Analytics & Tax
- **Dashboard**: Real-time Net Worth and Monthly Spending.
- **Analytics**: Detailed spending trends and breakdowns.
- **Tax Center**: Track tax payments/refunds and estimate liability.
    - *Setup*: Create categories with "Tax" or "VAT" in the name (e.g., "Income Tax" as Expense).

## 🔐 SaaS & Multi-User Support
The application is now a multi-user SaaS platform.
1.  **Login/Signup**: New users must sign up.
2.  **Data Isolation**: Every user sees ONLY their own data (enforced by Row Level Security).
3.  **Admin Dashboard**: Accessible via `System > Admin` (restricted to admin email).

## 🤖 AI Features
### Smart Ingestor
Located in `AI Tools > Smart Ingestor`.
-   **Text Parsing**: Paste raw text (e.g., from an email) to extract expense details.
-   **Vision Scanning**: Upload an image of a receipt (`.jpg`, `.png`). The AI will read the date, merchant, and amount, and auto-categorize it.

## 🚀 Getting Started
1.  **Run the App**: `python -m streamlit run app.py`
2.  **Login**: Create an account.
3.  **Settings**: Go to `System > Settings` to create your Accounts and Categories.
4.  **Add Data**: Use `Finance > Expenses` or `AI Tools > Smart Ingestor`.

## 🔮 Future Roadmap
-   [ ] **Mobile App**: Build a React Native mobile frontend.
-   [ ] **Email Integration**: Forward receipts to `receipts@lifeos.com`.
-   [ ] **Subscription Billing**: Integrate Stripe for SaaS subscriptions.
- **Travel**: Plan and track trips.
