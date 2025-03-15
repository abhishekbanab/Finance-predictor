from flask import Flask, jsonify, render_template,request
from pred import *  
app = Flask(__name__)

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
    top_expenses = top_expense()  # Call function to get top 10 expenses
    return jsonify(top_expenses)
@app.route('/next_month', methods=['GET'])
def get_nxt_prediction():
    prediction=next_month_prediction()
    return jsonify(prediction)
@app.route('/piechart',methods=['GET'])
def get_piechart():
    pie_data=piechart()
    return jsonify(pie_data)
@app.route('/add-expense', methods=['POST'])
def add_expense():
    data = request.get_json()

    # Validate input
    required_fields = ["Date", "Category", "Amount", "Income/Expense"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    # Pass data to model function
    print(data)
    response = add_expense_to_csv(data)
    
    return jsonify(response)
@app.route('/recent-transactions', methods=['GET'])
def recent_transactions():
    transaction = transactions()
    return jsonify(transaction)
if __name__ == '__main__':
    app.run(debug=True)
