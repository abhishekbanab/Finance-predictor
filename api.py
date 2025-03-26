from flask import Flask, jsonify, render_template, request
from flask_cors import CORS 
import pandas as pd
from pred import *  

app = Flask(__name__)

CORS(app)

@app.route('/')
def home():
    return render_template('index.html')  # Serves the frontend

@app.route('/forecast', methods=['GET'])
def get_forecast():
    forecast = get_prediction()  
    forecast_data = forecast[['ds', 'yhat']].to_dict(orient='records')  
    return jsonify(forecast_data)  

@app.route('/top_expenses', methods=['GET'])
def get_top_expenses():
    return jsonify(top_expense())  # Get top 10 expenses

@app.route('/next_month', methods=['GET'])
def get_nxt_prediction():
    return jsonify(next_month_prediction())

@app.route('/piechart', methods=['GET'])
def get_piechart():
    return jsonify(piechart())

@app.route('/add-expense', methods=['POST'])
def add_expense():
    data = request.get_json()

    # Validate input
    required_fields = ["Date", "Category", "Amount", "Income/Expense"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    print(data)  # Debugging log
    response = add_expense_to_csv(data)
    
    return jsonify(response)

@app.route('/recent-transactions', methods=['GET'])
def recent_transactions():
    return jsonify(transactions())

@app.route('/monthly_expenses', methods=['GET'])
def get_monthly_expenses():
    return jsonify(calculate_monthly_expenses())

def calculate_monthly_expenses():
    try:
        # Load the expense data (Modify the file path accordingly)
        df = pd.read_csv("expense_data_1.csv", encoding="utf-8", parse_dates=["Date"])

        if df.empty:
            return {"error": "No expense data available"}

        # Ensure the Date column is in datetime format
        df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")

        # Filter only expense entries
        df = df[df["Income/Expense"] == "Expense"]

        # Extract month and year for grouping
        df["Month"] = df["Date"].dt.strftime("%B %Y")

        # Group by month and sum expenses
        monthly_data = (
            df.groupby("Month")["Amount"]
            .sum()
            .reset_index()
            .rename(columns={"Amount": "expenses"})
        )

        # Sort by actual date (since months are string-sorted otherwise)
        monthly_data["DateSort"] = pd.to_datetime(monthly_data["Month"], format="%B %Y")
        monthly_data = monthly_data.sort_values("DateSort").drop(columns=["DateSort"])

        return monthly_data.to_dict(orient="records")

    except FileNotFoundError:
        return {"error": "Expense data file not found"}

    except Exception as e:
        return {"error": str(e)}
    
@app.route('/category_expenses', methods=['GET'])
def get_category_expenses():
    try:
        df = pd.read_csv("expense_data_1.csv", encoding="utf-8", parse_dates=["Date"])

        if df.empty:
            return jsonify({"error": "No expense data available"})

        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
        df = df.dropna(subset=["Amount"])
        df["Income/Expense"] = df["Income/Expense"].astype(str).str.strip()
        df = df[df["Income/Expense"] == "Expense"]

        df["YearMonth"] = df["Date"].dt.to_period("M")
        latest_month = df["YearMonth"].max()

        while latest_month and df[df["YearMonth"] == latest_month].empty:
            latest_month -= 1  # Move to the previous month
        
        df_latest = df[df["YearMonth"] == latest_month]
        
        categories = ["Food", "Other", "Apparel", "Household", "Transportation", "Social Life"]
        category_expenses = (
            df_latest[df_latest["Category"].isin(categories)]
            .groupby("Category")["Amount"]
            .sum()
            .reindex(categories, fill_value=0)
        )

        total_spending = category_expenses.sum()
        category_percentages = (
            (category_expenses / total_spending) * 100
        ).round(2).to_dict() if total_spending > 0 else {cat: 0 for cat in categories}

        month_name = latest_month.strftime("%B %Y") if latest_month else "Unknown"
        response_data = {
            "month": month_name,
            "total_spending": total_spending,
            "category_breakdown": category_percentages
        }

        return jsonify(response_data)

    except FileNotFoundError:
        return jsonify({"error": "Expense data file not found"})

    except Exception as e:
        return jsonify({"error": str(e)})





if __name__ == '__main__':
    app.run(debug=True)
