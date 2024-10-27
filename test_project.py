from project import build_csv_url, fetch_exchange_rates, fetch_exchange_rates_csv
import pandas as pd

def test_build_csv_url():
    assert build_csv_url('2024-09-01', '2024-09-11') == "https://api.cba.am/ExchangeRatesToCSV.ashx?DateFrom=2024-08-01&DateTo=2024-09-11&ISOCodes=EUR,GBP,RUB,USD"

def test_fetch_exchange_rates_csv():
    df = fetch_exchange_rates_csv("https://api.cba.am/ExchangeRatesToCSV.ashx?DateFrom=2024-09-01&DateTo=2024-09-11&ISOCodes=EUR,GBP,RUB,USD")
    assert isinstance(df, pd.DataFrame), "Expected a DataFrame"
    assert 'Date' in df.columns, "Expected 'Date' column in DataFrame"
    assert not df.empty, "Expected DataFrame not to be empty"

def test_fetch_exchange_rates():
    df = fetch_exchange_rates("https://www.rate.am/hy/armenian-dram-exchange-rates/banks")
    assert isinstance(df, pd.DataFrame), "Expected a DataFrame"
    assert 'timestamp' in df.columns, "Expected 'Date' column in DataFrame"
    assert not df.empty, "Expected DataFrame not to be empty"