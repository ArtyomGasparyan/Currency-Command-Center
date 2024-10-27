import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
from mysql_magic import MySQLHandler

def fetch_exchange_rates(url):
    """
    Fetches the exchange rates from the given URL and returns a DataFrame with a timestamp.
    
    Parameters:
    url (str): The URL of the page to scrape.

    Returns:
    pd.DataFrame: A DataFrame containing the bank names, buy rates, sell rates, and timestamp.
    """
    # Make a request to fetch the content of the page
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to reach the site. Status code: {response.status_code}")
        return pd.DataFrame()

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the main section where rates are likely located
    main_section = soup.find('main', class_='pt-4 pb-8 md:pb-12')

    # Check if the main section is found
    if not main_section:
        print("Main section not found.")
        return pd.DataFrame()
    else:
        print("Main section found.")

    # Extract buying rates based on the class for buy rates
    buy_rate_elements = main_section.find_all('div', class_='relative flex z-1 items-center h-full')
    buy_rates = [rate.text.strip() for rate in buy_rate_elements if rate.text.strip()]

    # Extract selling rates based on the class for sell rates
    sell_rate_elements = main_section.find_all('div', class_='relative z-1 flex items-center h-full')
    sell_rates = [rate.text.strip() for rate in sell_rate_elements if rate.text.strip()]

    # List of banks in the correct order
    banks = [
        'HSBC Bank Armenia', 'VTB Bank (Armenia)', 'ArmSwissBank', 'Armeconombank', 
        'Artsakhbank', 'Fast Bank', 'Evocabank', 'Mellat Bank', 'Inecobank', 
        'ID Bank', 'Byblos Bank Armenia', 'Ameriabank', 'Ardshinbank', 'AraratBank', 
        'Acba bank', 'AMIO Bank', 'Converse Bank', 'Unibank'
    ]

    # Prepare a list to hold the data
    data = []

    # Assuming each bank has three buy rates (USD, EUR, RUR) and three sell rates (USD, EUR, RUR)
    buy_rate_index = 0
    sell_rate_index = 0

    for bank in banks:
        try:
            # Get buy rates
            buy_usd_rate = buy_rates[buy_rate_index]
            buy_eur_rate = buy_rates[buy_rate_index + 1]
            buy_rur_rate = buy_rates[buy_rate_index + 2]

            # Get sell rates
            sell_usd_rate = sell_rates[sell_rate_index]
            sell_eur_rate = sell_rates[sell_rate_index + 1]
            sell_rur_rate = sell_rates[sell_rate_index + 2]

            # Append the data
            data.append({
                'bank_name': bank,
                'usd_buy': buy_usd_rate,
                'eur_buy': buy_eur_rate,
                'rur_buy': buy_rur_rate,
                'usd_sell': sell_usd_rate,
                'eur_sell': sell_eur_rate,
                'rur_sell': sell_rur_rate,
                'timestamp': datetime.now()  # Add timestamp
            })

            buy_rate_index += 3
            sell_rate_index += 3

        except IndexError:
            print(f"Not enough rates to assign for {bank}. Check the rates list or adjust the hard-coded logic.")

    # Convert the data into a DataFrame without an index
    df = pd.DataFrame(data)

    return df


def fetch_exchange_rates_csv(url):
    """
    Fetches the exchange rates data from the CSV link provided by the Central Bank of Armenia.

    Parameters:
    url (str): The URL of the CSV file to fetch.

    Returns:
    pd.DataFrame: A DataFrame containing the exchange rates data.
    """
    try:
        # Read the CSV file directly into a DataFrame, adjusting for header misalignment
        df = pd.read_csv(url, header=1)  # Setting header=1 assumes the correct headers start from the second row
        
        # Drop any columns with NaN values that could result from misalignment issues
        df.dropna(axis=1, how='all', inplace=True)
        
        # Ensure correct column names for Date, EUR, GBP, RUB, and USD
        df.columns = ['Date', 'EUR', 'GBP', 'RUB', 'USD']

        # Convert Date column to datetime format
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')

        # Reset the index if you want the Date column as part of the DataFrame without being the index
        df.reset_index(drop=True, inplace=True)

        print("CSV data successfully retrieved and columns aligned.")
        return df
    except Exception as e:
        print(f"An error occurred while fetching the CSV data: {e}")
        return pd.DataFrame()

def build_csv_url(date_from, date_to, iso_codes="EUR,GBP,RUB,USD"):
    """
    Constructs the URL to fetch the exchange rates CSV for the specified date range and currencies.

    Parameters:
    date_from (str): The start date in 'YYYY-MM-DD' format.
    date_to (str): The end date in 'YYYY-MM-DD' format.
    iso_codes (str): The ISO codes of the currencies to fetch (default is "EUR,GBP,RUB,USD").

    Returns:
    str: The constructed URL.
    """
    base_url = "https://api.cba.am/ExchangeRatesToCSV.ashx"
    return f"{base_url}?DateFrom={date_from}&DateTo={date_to}&ISOCodes={iso_codes}"


def main():
    # Define the URL of the page to scrape
    url = "https://www.rate.am/hy/armenian-dram-exchange-rates/banks"
    
    # Fetch the exchange rates and get the DataFrame
    df = fetch_exchange_rates(url)

    # Print the DataFrame
    if not df.empty:
        print(df)
    else:
        print("No data to display.")

    # Initialize the MySQL handler
    mysql_handler = MySQLHandler(host='localhost', user='root', password='$bj9{GH!A=~]Wg?', database='currency_rates')

    # Upsert data into the table 'exchange_rates'
    mysql_handler.upsert_data(df, 'rate_am', check_columns=['timestamp','bank_name'])

    # Calculate the last 5 days date range
    date_to = datetime.now().strftime('%Y-%m-%d')
    date_from = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')

    # Construct the CSV URL
    csv_url = build_csv_url(date_from, date_to)
    print(csv_url)

    # Fetch the CSV data and get the DataFrame
    df_cba = fetch_exchange_rates_csv(csv_url)

    # Print the DataFrame
    if not df_cba.empty:
        print(df_cba.head())  # Print the first few rows of the DataFrame
    else:
        print("No data to display.")

    mysql_handler.upsert_data(df_cba, 'cba', check_columns=['Date'])


if __name__ == "__main__":
    main()
