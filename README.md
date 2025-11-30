# 🧬 Life OS - Personal Finance Platform

A modern, AI-powered financial web application. Built for individuals to track their wealth, analyze spending, and manage their life.

## 🌟 Features

### 💰 Finance Module
-   **Expense & Income Tracking**: Log transactions with detailed categories and accounts.
-   **Investment Portfolio**: Track stocks, crypto, and other assets with real-time P&L.
-   **Savings Goals**: Set and monitor progress towards financial goals.
-   **Tax Center**: Track tax payments and estimate liabilities.
-   **Advanced Analytics**: Interactive charts, Profit & Loss statements, and net worth tracking.
-   **Smart Features**: Support for "Tikkie" payments and loan tagging.

### 🤖 AI Tools
-   **Smart Ingestor**: 
    -   **Text Parsing**: Paste unstructured text (emails, messages) to auto-extract transaction details.
    -   **Vision AI**: Upload receipt images (`.jpg`, `.png`) to automatically extract date, merchant, and amount using Llama 3.2 Vision.

### 🔐 SaaS Foundation
-   **Multi-User Support**: Secure Sign-up and Login via Supabase Auth.
-   **Data Privacy**: Row Level Security (RLS) ensures users only see their own data.
-   **Admin Dashboard**: System overview and user management (restricted access).

## 🛠️ Tech Stack
-   **Frontend**: Streamlit (Python)
-   **Backend**: Supabase (PostgreSQL + Auth)
-   **AI**: LangChain + Groq (Llama 3)
-   **Visualization**: Plotly Express

## 🚀 Getting Started

### Prerequisites
-   Python 3.10+
-   A Supabase project
-   A Groq API Key

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/Srinivas1043/LifeOs.git
    cd LifeOs
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Secrets**
    Create a file `.streamlit/secrets.toml`:
    ```toml
    [supabase]
    url = "YOUR_SUPABASE_URL"
    key = "YOUR_SUPABASE_ANON_KEY"

    [groq]
    api_key = "YOUR_GROQ_API_KEY"
    ```

4.  **Run the App**
    ```bash
    python -m streamlit run app.py
    ```

## 📖 Usage Guide

1.  **Sign Up**: Create a new account on the Login page.
2.  **Setup**: Go to `System > Settings` to define your **Accounts** (e.g., Bank, Cash) and **Categories** (e.g., Food, Salary).
3.  **Add Data**: 
    -   Manual: Use `Finance > Expenses/Income`.
    -   AI: Use `AI Tools > Smart Ingestor` to scan receipts.
4.  **Analyze**: Check the Dashboard and Analytics pages for insights.

## 🛡️ Security
-   This project uses **Row Level Security (RLS)**.
-   API Keys are stored in `.streamlit/secrets.toml` and are **NOT** tracked by git.

## 📄 License
MIT License
