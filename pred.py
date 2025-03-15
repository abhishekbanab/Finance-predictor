import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet
from sklearn.linear_model import LinearRegression
import numpy as np
# Load and preprocess dataset
  # Corrected file path
def load_and_preprocess():
    df = pd.read_csv("expense_data_1.csv")  # Load dataset inside the function
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')  # Convert Date to datetime
    df = df[df['Income/Expense'] == 'Expense']  # Keep only expenses
    df = df[['Date', 'Amount']].dropna()  # Keep relevant columns and drop NaNs
    df = df.rename(columns={'Date': 'ds', 'Amount': 'y'})  # Rename for Prophet
    return df

def get_prediction():
    df = load_and_preprocess()  # Ensure preprocessed data is used

    if df.empty:
        print("No valid data for forecasting")
        return {"error": "No valid expense data for forecasting"}

    print("Training Prophet model...")
    
    # Initialize and fit Prophet model
    model = Prophet()
    model.fit(df)

    # Create future dataframe for predictions
    future = model.make_future_dataframe(periods=30)  # Predict next 30 days
    forecast = model.predict(future)
    return forecast  # Return forecast instead of plotting inside function

def top_expense():
    top_expenses = df.nlargest(10, 'Amount')
    print(top_expenses.head())
    #top_expenses=top_expenses.drop('Currency',axis=1)
   # print(top_expenses)
    return top_expenses
def next_month_prediction():
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    # Filter only expense entries
    df_expense = df[df['Income/Expense'] == 'Expense'].copy()

    # Extract Year-Month for grouping
    df_expense['YearMonth'] = df_expense['Date'].dt.to_period('M')

    # Aggregate total expenses per month
    monthly_expense = df_expense.groupby('YearMonth')['Amount'].sum().reset_index()

    # Convert period to datetime format for modeling
    monthly_expense['YearMonth'] = monthly_expense['YearMonth'].astype(str)
    monthly_expense['YearMonth'] = pd.to_datetime(monthly_expense['YearMonth'])

    # Prepare data for prediction (X: month index, y: expense)
    monthly_expense['MonthIndex'] = np.arange(len(monthly_expense)).reshape(-1, 1)
    X = monthly_expense[['MonthIndex']]
    y = monthly_expense['Amount']

    # Train a simple linear regression model
    model = LinearRegression()
    model.fit(X, y)

    # Predict next month's expense (Ensure it's passed as a NumPy array)
    next_month_index = np.array([[monthly_expense['MonthIndex'].max() + 1]])
    predicted_expense = model.predict(next_month_index)[0]
    return round(predicted_expense,3)
    # Print predicted expense
def process_expense_data():
    

    # Filter out income-related entries
    income_categories = ["Salary", "Allowance", "Monthly Income", "Petty Cash"]
    df_expense = df[(df['Income/Expense'] == 'Expense') & (~df['Category'].isin(income_categories))]

    # Define categories for expense classification
    expense_categories = ["Food", "Household", "Education", "Transportation"]
    df_expense["Category"] = df_expense["Category"].apply(lambda x: x if x in expense_categories else "Others")

    # Aggregate expenses by category
    category_expenses = df_expense.groupby("Category")["Amount"].sum().to_dict()
def piechart():
    # Check if 'Income/Expense' and 'Category' columns exist
    if 'Income/Expense' not in df.columns or 'Category' not in df.columns:
        return {"error": "Required columns are missing"}

    # Filter out income-related entries
    income_categories = ["Salary", "Allowance", "Monthly Income", "Petty Cash"]
    df_expense = df[(df['Income/Expense'].str.lower() == 'expense') & (~df['Category'].isin(income_categories))]

    # Define categories for expense classification
    expense_categories = ["Food", "Household", "Education", "Transportation"]
    df_expense["Category"] = df_expense["Category"].apply(lambda x: x if x in expense_categories else "Others")

    # Aggregate expenses by category
    category_expenses = df_expense.groupby("Category")["Amount"].sum().to_dict()
    print(category_expenses)
    return category_expenses if category_expenses else {"error": "No expense data found"}
def add_expense_to_csv(expense_data):
    try:
        # Load existing data

        # Convert new entry to DataFrame
        new_entry = pd.DataFrame([expense_data])

        # Append new entry
        df = pd.concat([df, new_entry], ignore_index=True)

        # Save back to CSV
        df.to_csv(r"expense_data_1.csv", index=False)

        return {"message": "Expense added successfully"}
    except Exception as e:
        return {"error": str(e)}
def transactions(n=5):
    try:
        df = df.dropna(subset=['Date'])
        recent_transactions = df.sort_values(by='Date', ascending=False).head(n)
        return recent_transactions.to_dict(orient='records')
    except Exception as e:
        return {"error": str(e)}
get_prediction()