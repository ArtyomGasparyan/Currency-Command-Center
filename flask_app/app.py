from flask import Flask, render_template, request, jsonify
import pandas as pd
import plotly.graph_objs as go
import plotly.io as pio
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta

# Create Flask app
app = Flask(__name__)

# Database configuration
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = '$bj9{GH!A=~]Wg?'
DB_NAME = 'currency_rates'

# Create a database connection
engine = create_engine(f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')

def get_best_rates():
    with engine.connect() as conn:
        # Fetch the highest buy rates and lowest sell rates for each currency
        queries = {
            'usd_buy': "SELECT bank_name, usd_buy FROM rate_am WHERE usd_buy = (SELECT MAX(usd_buy) FROM rate_am) ORDER BY timestamp DESC LIMIT 1",
            'usd_sell': "SELECT bank_name, usd_sell FROM rate_am WHERE usd_sell = (SELECT MIN(usd_sell) FROM rate_am) ORDER BY timestamp DESC LIMIT 1",
            'eur_buy': "SELECT bank_name, eur_buy FROM rate_am WHERE eur_buy = (SELECT MAX(eur_buy) FROM rate_am) ORDER BY timestamp DESC LIMIT 1",
            'eur_sell': "SELECT bank_name, eur_sell FROM rate_am WHERE eur_sell = (SELECT MIN(eur_sell) FROM rate_am) ORDER BY timestamp DESC LIMIT 1",
            'rur_buy': "SELECT bank_name, rur_buy FROM rate_am WHERE rur_buy = (SELECT MAX(rur_buy) FROM rate_am) ORDER BY timestamp DESC LIMIT 1",
            'rur_sell': "SELECT bank_name, rur_sell FROM rate_am WHERE rur_sell = (SELECT MIN(rur_sell) FROM rate_am) ORDER BY timestamp DESC LIMIT 1"
        }

        results = {key: conn.execute(text(query)).fetchone() for key, query in queries.items()}
    return results

@app.route('/')
def index():
    # Fetch the best rates
    best_rates = get_best_rates()
    
    # Fetch the default date range for the last 30 days
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

    return render_template('index.html', best_rates=best_rates, start_date=start_date, end_date=end_date)

@app.route('/get_bank_names')
def get_bank_names():
    try:
        # Query to get unique bank names from the rate_am table
        query = "SELECT DISTINCT bank_name FROM rate_am ORDER BY bank_name ASC"
        
        with engine.connect() as conn:
            result = conn.execute(text(query))
            banks = [row['bank_name'] for row in result]
        
        return jsonify({'banks': banks})
    except Exception as e:
        print(f"Error fetching bank names: {e}")
        return jsonify({'error': 'Failed to fetch bank names'}), 500

@app.route('/data')
def data():
    # Get start and end dates from the request
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    selected_bank = request.args.get('bank', 'all')
    selected_metric = request.args.get('metric', 'usd_buy')  # Default metric if not provided

    # # Validate date inputs
    # if not start_date or not end_date:
    #     return jsonify({'error': 'Start date and end date must be provided.'}), 400

    try:
        # Define SQL queries with parameter binding
        query_cba = text("SELECT * FROM cba WHERE Date BETWEEN :start_date AND :end_date ORDER BY Date ASC")
        params = {'start_date': start_date, 'end_date': end_date}
        
        # Adjust the query based on bank selection
        if selected_bank == 'all':
            query_banks = text(f"SELECT bank_name, DATE(timestamp) as timestamp, {selected_metric} FROM rate_am WHERE timestamp BETWEEN :start_date AND :end_date ORDER BY timestamp ASC")
        else:
            query_banks = text(f"SELECT bank_name, DATE(timestamp) as timestamp, {selected_metric} FROM rate_am WHERE bank_name = :selected_bank AND timestamp BETWEEN :start_date AND :end_date ORDER BY timestamp ASC")
            params['selected_bank'] = selected_bank

        # Execute queries with parameter binding
        with engine.connect() as conn:
            df_cba = pd.read_sql(query_cba, conn, params=params)
            df_banks = pd.read_sql(query_banks, conn, params=params)

        # # Check if DataFrames are empty
        # if df_cba.empty or df_banks.empty:
        #     return jsonify({'error': 'No data available for the selected date range.'})

        # Create Plotly traces for CBA rates
        traces_cba = [
            go.Scatter(
                x=df_cba['Date'],
                y=df_cba[currency],
                mode='lines+markers',
                name=currency
            ) for currency in ['EUR', 'GBP', 'RUB', 'USD']
        ]

        # Create Plotly traces for bank rates
        traces_banks = [
            go.Scatter(
                x=df_banks['timestamp'],
                y=df_banks[selected_metric],
                mode='lines+markers',
                name=bank
            ) for bank in df_banks['bank_name'].unique()
        ]

        # Define layouts for CBA and bank rate charts
        layout_cba = go.Layout(
            title='Exchange Rates of Currencies',
            xaxis=dict(title='Date'),
            yaxis=dict(title='Exchange Rate (AMD)'),
            template='plotly_white',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='black')
        )

        layout_banks = go.Layout(
            title='Bank Rates',
            xaxis=dict(title='Date'),
            yaxis=dict(title='Exchange Rate (AMD)'),
            template='plotly_white',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='black')
        )

        # Create figures for both charts
        fig_cba = go.Figure(data=traces_cba, layout=layout_cba)
        fig_banks = go.Figure(data=traces_banks, layout=layout_banks)

        # Convert figures to JSON format
        graph_json_cba = pio.to_json(fig_cba)
        graph_json_banks = pio.to_json(fig_banks)

        # Return JSON response
        return jsonify({'graph_json_cba': graph_json_cba, 'graph_json_banks': graph_json_banks})

    except Exception as e:
        print(f"Error fetching data: {e}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500
    
@app.route('/best_rates')
def best_rates():
    # Fetch the best rates from the database
    best_rates = get_best_rates()
    
    # Convert the best rates to a JSON serializable format
    response = {
        'usd_buy': [best_rates['usd_buy'][0], best_rates['usd_buy'][1]],
        'usd_sell': [best_rates['usd_sell'][0], best_rates['usd_sell'][1]],
        'eur_buy': [best_rates['eur_buy'][0], best_rates['eur_buy'][1]],
        'eur_sell': [best_rates['eur_sell'][0], best_rates['eur_sell'][1]],
        'rur_buy': [best_rates['rur_buy'][0], best_rates['rur_buy'][1]],
        'rur_sell': [best_rates['rur_sell'][0], best_rates['rur_sell'][1]],
    }
    
    return jsonify(response)
    
if __name__ == '__main__':
    app.run(debug=True)