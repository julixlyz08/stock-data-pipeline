import requests
from urllib.parse import urlparse, parse_qs
from pprint import pprint
import statistics
import math
import sqlite3
import os
from dotenv import load_dotenv

# -------------------------------------------------------------------
# Step 1 - Build the first API request
# -------------------------------------------------------------------

load_dotenv()

def build_api_url(symbol="INTC", function="TIME_SERIES_DAILY", api_key=None):
    if api_key is None:
        api_key = os.getenv("ALPHAVANTAGE_API_KEY")

    if not api_key:
        raise ValueError("API key not found. Check your .env file.")

    base_url = "https://www.alphavantage.co/query"

    params = {
        "function": function,
        "symbol": symbol,
        "apikey": api_key,
    }

    response_object = requests.Request(
        "GET",
        base_url,
        params=params
    ).prepare()

    print("URL built successfully. API key hidden.")
    return response_object.url

url = build_api_url()

def make_basic_request(url):
    print("\n--- SENDING REQUEST ---")
    print("Client: Intel Stock Analytics System")
    print("Server: Alpha Vantage API")
    print("Action: requests.get(url)")

    try:
        response = requests.get(url, timeout=30)
        print("Status code: ", response.status_code)

        if response.status_code == 200:
            print("Request successful.")
        else:
            print("Request failed. Status code:", response.status_code)
            return None

        return response

    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Check your internet connection.")
        return None
    except requests.exceptions.Timeout:
        print("Error: The request timed out. The server took too long to respond.")
        return None
    except requests.exceptions.RequestException as e:
        print("Error: An unexpected error occurred:", e)
        return None

def validate_response(response):
    if response is None:
        print("Validation failed: No response received.")
        return False

    if response.status_code != 200:
        print("Validation failed: Status code", response.status_code)
        return False

    try:
        data = response.json()
    except ValueError:
        print("Validation failed: Response is not valid JSON.")
        return False

    if "Time Series (Daily)" not in data:
        print("Validation failed: Time Series data not found.")
        print("API returned:", data)
        return False

    print("Validation passed: Response contains valid Time Series data.")
    return True

re = make_basic_request(url)

if re is None:
    print("Analysis stopped. Request could not be completed.")
    exit()

if not validate_response(re):
    print("Analysis stopped. Please check your API key and try again.")
    exit()

# -------------------------------------------------------------------
# Step 2 - Inspect and parse the JSON response 
# -------------------------------------------------------------------

def preview_json_structure(response):
    print("\n--- JSON PREVIEW ---")
    try:
        data = response.json()

        if "Time Series (Daily)" not in data:
            print("API rate limit reached or invalid key.")
            print("API returned:", data)
            return None

        print("Data retrieved successfully.")
        return data

    except ValueError as e:
        print("JSON parsing error:", e)
        return None

data = preview_json_structure(re)

if data is None:
    print("Analysis stopped. Please wait and try again later.")
    exit()

def inspect_top_level_structure(data):
    print("\nInspecting the parsed JSON structure:")
    print("Type of data: ", type(data))
    print("Top-level keys: ", list(data.keys()))

inspect_top_level_structure(data)

# -------------------------------------------------------------------
# Step 3 - Create calculated fields
# -------------------------------------------------------------------

def extract_daily_records(data):
    time_series = data["Time Series (Daily)"]
    dates = list(time_series.keys())[:100]

    records = []
    for date in dates:
        record = time_series[date]
        open_price  = float(record["1. open"])
        high_price  = float(record["2. high"])
        low_price   = float(record["3. low"])
        close_price = float(record["4. close"])
        volume      = int(record["5. volume"])
        records.append({
            "date": date,
            "open": open_price,
            "high": high_price,
            "low": low_price,
            "close": close_price,
            "volume": volume
        })

    print(f"\nExtracted {len(records)} daily records.")
    print(f"Most recent date: {records[0]['date']}")
    print(f"Oldest date in range: {records[-1]['date']}")

    return records

def calculate_metrics(records):
    print("\n--- CALCULATED METRICS ---")

    price_changes = []
    percent_changes = []
    daily_ranges = []

    for r in records:
        daily_price_change = r["close"] - r["open"]
        daily_percent_change = (daily_price_change / r["open"]) * 100
        daily_range = r["high"] - r["low"]
        price_changes.append(daily_price_change)
        percent_changes.append(daily_percent_change)
        daily_ranges.append(daily_range)

        print(f"{r['date']} | Change: {round(daily_price_change, 2)} | "
              f"Percent: {round(daily_percent_change, 2)}% | "
              f"Range: {round(daily_range, 2)}")
    
    avg_price_change = sum(price_changes) / len(price_changes)
    avg_percent_change = sum(percent_changes) / len(percent_changes)
    avg_daily_range = sum(daily_ranges) / len(daily_ranges)

    print(f"\nAverage price change (100 days):   {round(avg_price_change, 2)}")
    print(f"Average percent change (100 days):   {round(avg_percent_change, 2)}")
    print(f"Average daily range (100 days):      {round(avg_daily_range, 2)}")

    return price_changes, percent_changes, daily_ranges, avg_price_change, avg_percent_change, avg_daily_range

records = extract_daily_records(data)
price_changes, percent_changes, daily_ranges, avg_price_change, avg_percent_change, avg_daily_range = calculate_metrics(records)

# -------------------------------------------------------------------
# Step 4 - Design the volatility classification algorithm
# -------------------------------------------------------------------

def calculate_annualized_volatility(percent_changes):
    std_30 = statistics.stdev(percent_changes)
    annualized_vol = (std_30 / 100) * math.sqrt(252)

    print(f"\n--- ANNUALIZED VOLATILITY ---")
    print(f"30-day std dev of daily returns: {round(std_30, 4)}%")
    print(f"Annualized volatility:           {round(annualized_vol * 100, 2)}%")

    return annualized_vol

def classify_volatility(annualized_vol):
    print("\n--- VOLATILITY CLASSIFICATION ---")

    vol_pct = annualized_vol * 100

    if vol_pct < 25:
        label = "Low"
    elif vol_pct <= 50:
        label = "Moderate"
    else:
        label = "High"

    print(f"Annualized volatility: {round(vol_pct, 2)}%")
    print(f"Volatility category:   {label}")
    print(f"\nThreshold rules:")
    print(f"  Low:      annualized vol < 25%")
    print(f"  Moderate: annualized vol 25% to 50%")
    print(f"  High:     annualized vol > 50%")

    return label

annualized_vol = calculate_annualized_volatility(percent_changes)
volatility_label = classify_volatility(annualized_vol)

def generate_signal(records):
    print("\n--- BUY/SELL/HOLD SIGNALS ---")

    signals = []

    for r in records:
        daily_percent_change = (r["close"] - r["open"]) / r["open"] * 100
        daily_range_pct = (r["high"] - r["low"]) / r["open"] * 100

        if daily_percent_change > 1:
            movement = "Positive"
        elif daily_percent_change < -1:
            movement = "Negative"
        else:
            movement = "Neutral"

        if daily_range_pct > 5:
            day_volatility = "High"
        elif daily_range_pct >= 2:
            day_volatility = "Moderate"
        else:
            day_volatility = "Low"

        if movement == "Positive" and day_volatility != "High":
            signal = "Buy"
        elif movement == "Negative":
            signal = "Sell"
        else:
            signal = "Hold"

        signals.append(signal)

        print(f"{r['date']} | Percent Change: {round(daily_percent_change, 2)}% | "
              f"Movement: {movement} | Signal: {signal}")

    buy_count  = signals.count("Buy")
    sell_count = signals.count("Sell")
    hold_count = signals.count("Hold")

    print(f"\nSignal summary ({len(records)} days):")
    print(f"  Buy:  {buy_count}")
    print(f"  Sell: {sell_count}")
    print(f"  Hold: {hold_count}")

    return signals

signals = generate_signal(records)

def print_signal_preview(records, signals, days=30):
    print(f"\n--- RECENT {days}-DAY SIGNAL PREVIEW ---")
    print(f"{'Date':<12} {'Open':>8} {'Close':>8} {'Change%':>9} {'Movement':<10} {'Signal':<6}")
    print("-" * 55)

    for i, r in enumerate(records[:days]):
        daily_percent_change = (r["close"] - r["open"]) / r["open"] * 100

        if daily_percent_change > 1:
            movement = "Positive"
        elif daily_percent_change < -1:
            movement = "Negative"
        else:
            movement = "Neutral"

        print(f"{r['date']:<12} {round(r['open'], 2):>8} "
              f"{round(r['close'], 2):>8} "
              f"{round(daily_percent_change, 2):>8}% "
              f"{movement:<10} {signals[i]:<6}")

print_signal_preview(records, signals, days=30)

# -------------------------------------------------------------------
# Step 5 - Print a report
# -------------------------------------------------------------------

def print_summary_report(records, signals, volatility_label, annualized_vol):
    print("\n" + "=" * 60)
    print("       INTEL CORPORATION (INTC) - ANALYTICS REPORT")
    print("=" * 60)

    total_days = len(records)
    most_recent = records[0]
    oldest = records[-1]

    buy_count  = signals.count("Buy")
    sell_count = signals.count("Sell")
    hold_count = signals.count("Hold")

    avg_close = sum(r["close"] for r in records) / total_days
    highest_close = max(r["close"] for r in records)
    lowest_close  = min(r["close"] for r in records)

    most_recent_signal = signals[0]
    most_recent_change = (most_recent["close"] - most_recent["open"]) / most_recent["open"] * 100

    print(f"\nAnalysis period:      {oldest['date']} to {most_recent['date']}")
    print(f"Total days analyzed:  {total_days}")

    print(f"\n--- PRICE SUMMARY ---")
    print(f"Most recent close:    ${round(most_recent['close'], 2)}")
    print(f"Average close price:  ${round(avg_close, 2)}")
    print(f"Highest close:        ${round(highest_close, 2)}")
    print(f"Lowest close:         ${round(lowest_close, 2)}")

    print(f"\n--- VOLATILITY SUMMARY ---")
    print(f"Annualized volatility: {round(annualized_vol * 100, 2)}%")
    print(f"Volatility category:   {volatility_label}")
    if volatility_label == "High":
        print("Interpretation: Intel's stock has shown unusually large price")
        print("swings over this period, indicating elevated risk.")
    elif volatility_label == "Moderate":
        print("Interpretation: Intel's stock has shown normal price movement")
        print("typical for a large technology company.")
    else:
        print("Interpretation: Intel's stock has been relatively stable")
        print("with small price movements over this period.")

    print(f"\n--- SIGNAL SUMMARY ---")
    print(f"Buy signals:   {buy_count} days ({round(buy_count / total_days * 100, 1)}%)")
    print(f"Sell signals:  {sell_count} days ({round(sell_count / total_days * 100, 1)}%)")
    print(f"Hold signals:  {hold_count} days ({round(hold_count / total_days * 100, 1)}%)")

    print(f"\n--- MOST RECENT DAY ({most_recent['date']}) ---")
    print(f"Price change:  {round(most_recent_change, 2)}%")
    print(f"Signal:        {most_recent_signal}")

    print(f"\n--- BUSINESS RECOMMENDATION ---")
    if most_recent_signal == "Buy":
        print("The system generated a BUY signal for the most recent trading day.")
        print("Price movement was positive and volatility was within normal range.")
    elif most_recent_signal == "Sell":
        print("The system generated a SELL signal for the most recent trading day.")
        print("Price movement was negative, suggesting downward momentum.")
    else:
        print("The system generated a HOLD signal for the most recent trading day.")
        print("Conditions were mixed or volatility was too high to recommend action.")

    print("\nNote: This report is for educational purposes only and does")
    print("not constitute real financial or investment advice.")
    print("=" * 60)

print_summary_report(records, signals, volatility_label, annualized_vol)

# -------------------------------------------------------------------
# Step 6 - Store processed data in a SQL database
# -------------------------------------------------------------------

DB_FILE = "intc_stock_data.db"

def create_database(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    print("\nConnected to SQLite database:", db_file)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS intc_daily_prices (
        symbol           TEXT,
        trade_date       TEXT,
        open_price       REAL,
        high_price       REAL,
        low_price        REAL,
        close_price      REAL,
        volume           INTEGER,
        percent_change   REAL,
        volatility_label TEXT,
        signal           TEXT,
        PRIMARY KEY (symbol, trade_date)
    )
    """)
    print("Table intc_daily_prices is ready.")
    return conn, cursor

def insert_records(conn, cursor, records, signals):
    inserted_count = 0

    for i, r in enumerate(records):
        percent_change = (r["close"] - r["open"]) / r["open"] * 100
        daily_range_pct = (r["high"] - r["low"]) / r["open"] * 100

        if daily_range_pct > 5:
            day_volatility = "High"
        elif daily_range_pct >= 2:
            day_volatility = "Moderate"
        else:
            day_volatility = "Low"

        cursor.execute("""
        INSERT OR REPLACE INTO intc_daily_prices
        (symbol, trade_date, open_price, high_price, low_price,
        close_price, volume, percent_change, volatility_label, signal)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "INTC",
            r["date"],
            r["open"],
            r["high"],
            r["low"],
            r["close"],
            r["volume"],
            round(percent_change, 4),
            day_volatility,
            signals[i]
        ))
        inserted_count += 1

    conn.commit()
    print(f"Inserted {inserted_count} records into the database.")
    return inserted_count

def close_database(conn):
    conn.close()
    print("\nDatabase connection closed.")

# -------------------------------------------------------------------
# Step 7 - SQL queries
# -------------------------------------------------------------------

def query_signal_counts(cursor):
    print("\n1. Count of Buy, Sell, and Hold signals:")
    cursor.execute("""
    SELECT signal, COUNT(*) AS count
    FROM intc_daily_prices
    GROUP BY signal
    ORDER BY count DESC
    """)
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]} days")

def query_avg_change_by_signal(cursor):
    print("\n2. Average percent change by signal type:")
    cursor.execute("""
    SELECT signal, ROUND(AVG(percent_change), 4) AS avg_percent_change
    FROM intc_daily_prices
    GROUP BY signal
    ORDER BY avg_percent_change DESC
    """)
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]}%")

def query_highest_volatility_day(cursor):
    print("\n3. Highest volatility day:")
    cursor.execute("""
    SELECT trade_date, close_price, percent_change, volatility_label
    FROM intc_daily_prices
    ORDER BY ABS(percent_change) DESC
    LIMIT 1
    """)
    for row in cursor.fetchall():
        print(f"   {row[0]} | Close: ${row[1]} | Change: {row[2]}% | {row[3]}")

def query_high_volatility_days(cursor):
    print("\n4. All High volatility days:")
    cursor.execute("""
    SELECT trade_date, close_price, percent_change, volatility_label
    FROM intc_daily_prices
    WHERE volatility_label = 'High'
    ORDER BY trade_date DESC
    """)
    for row in cursor.fetchall():
        print(f"   {row[0]} | Close: ${row[1]} | Change: {row[2]}%")

def query_avg_closing_price(cursor):
    print("\n5. Average closing price over the full period:")
    cursor.execute("""
    SELECT ROUND(AVG(close_price), 2) AS avg_close_price
    FROM intc_daily_prices
    """)
    row = cursor.fetchone()
    print(f"   Average close: ${row[0]}")

def query_volatility_category_counts(cursor):
    print("\n6. Count of days by volatility category:")
    cursor.execute("""
    SELECT volatility_label, COUNT(*) AS count
    FROM intc_daily_prices
    GROUP BY volatility_label
    ORDER BY count DESC
    """)
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]} days")

def query_best_performing_days(cursor):
    print("\n7. Top 5 best performing days:")
    cursor.execute("""
    SELECT trade_date, open_price, close_price, percent_change, signal
    FROM intc_daily_prices
    ORDER BY percent_change DESC
    LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"   {row[0]} | Open: ${row[1]} | Close: ${row[2]} | Change: {row[3]}% | {row[4]}")

def query_worst_performing_days(cursor):
    print("\n8. Top 5 worst performing days:")
    cursor.execute("""
    SELECT trade_date, open_price, close_price, percent_change, signal
    FROM intc_daily_prices
    ORDER BY percent_change ASC
    LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"   {row[0]} | Open: ${row[1]} | Close: ${row[2]} | Change: {row[3]}% | {row[4]}")

# --- RUN ALL QUERIES ---
conn, cursor = create_database(DB_FILE)
insert_records(conn, cursor, records, signals)

print("\n--- SQL QUERY RESULTS ---")
query_signal_counts(cursor)
query_avg_change_by_signal(cursor)
query_highest_volatility_day(cursor)
query_high_volatility_days(cursor)
query_avg_closing_price(cursor)
query_volatility_category_counts(cursor)
query_best_performing_days(cursor)
query_worst_performing_days(cursor)

close_database(conn)
print("\nDatabase saved at:", os.path.abspath(DB_FILE))