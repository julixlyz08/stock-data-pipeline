# Intel Stock Analytics System

A Python-based financial analytics pipeline that retrieves Intel Corporation (INTC) stock data from the Alpha Vantage API, calculates daily market metrics, classifies volatility, generates rule-based signals, and stores the processed results in SQLite.

This project was created for an applied business analytics programming project. It demonstrates API integration, JSON parsing, Python functions, algorithmic decision rules, SQL queries, and business communication.

> **Educational disclaimer:** The Buy, Sell, and Hold labels are outputs from a simple educational rules-based model. They are not investment advice or predictions of future stock performance.

## Project question

How can recent daily stock price behavior be classified by price movement, volatility level, and a basic rules-based signal so that a nontechnical stakeholder can review the results quickly?

## What the project does

The pipeline:

1. Requests daily INTC stock data from Alpha Vantage.
2. Validates the HTTP response and expected JSON structure.
3. Extracts the open, high, low, close, and volume fields.
4. Calculates daily price change, percentage change, and trading range.
5. Classifies each trading day as Low, Moderate, or High volatility.
6. Generates a Buy, Sell, or Hold signal using the movement and volatility rules.
7. Stores the processed records in a SQLite database.
8. Runs SQL queries that summarize signals, volatility, prices, and best and worst-performing days.

## Tools and technologies

- Python
- `requests` for API requests
- `python-dotenv` for secure local API-key management
- Alpha Vantage `TIME_SERIES_DAILY` API
- SQLite and SQL
- JSON data processing

## Business rules

### Price movement

- Positive: daily percentage change greater than 1%
- Negative: daily percentage change below -1%
- Neutral: daily percentage change between -1% and 1%

### Daily volatility

Daily range percentage is calculated as:

```text
(high price - low price) / open price × 100
```

- Low: range percentage below 2%
- Moderate: range percentage from 2% through 5%
- High: range percentage above 5%

### Signal

- Buy: positive movement with volatility below High
- Sell: negative movement
- Hold: neutral movement or positive movement with High volatility

The rules are intentionally simple and interpretable. They are designed to demonstrate algorithmic thinking rather than replace a professional investment model.

## Database

The SQLite database contains a table named `intc_daily_prices` with the following fields:

| Field | Description |
|---|---|
| `symbol` | Stock ticker symbol |
| `trade_date` | Trading date |
| `open_price` | Opening price |
| `high_price` | Highest price of the day |
| `low_price` | Lowest price of the day |
| `close_price` | Closing price |
| `volume` | Trading volume |
| `percent_change` | Percentage change from open to close |
| `volatility_label` | Low, Moderate, or High |
| `signal` | Buy, Sell, or Hold |

The combination of `symbol` and `trade_date` acts as the primary key to prevent duplicate records.

## SQL analysis

The project includes queries that calculate:

- Counts of Buy, Sell, and Hold signals
- Average percentage change by signal type
- The highest-volatility trading day
- All days classified as High volatility
- Average closing price across the analysis period
- Counts of days in each volatility category
- The five best-performing days
- The five worst-performing days

## Repository structure

```text
stock-data-pipeline/
├── README.md                # project overview (this file)
├── INTC_python.py           # the full pipeline: API → metrics → signals → SQLite → SQL report
├── intc_stock_data.db       # SQLite database produced by the script (see note below)
├── INTC_flowchart.png       # flowchart of the algorithm
├── project_presentation.pdf # written project report
├── requirements.txt         # Python packages needed
├── .env.example             # template for your API key
└── .gitignore
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/julixlyz08/stock-data-pipeline.git
cd stock-data-pipeline
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows, activate the environment with:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your API key locally

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Then add your own Alpha Vantage key:

```text
ALPHAVANTAGE_API_KEY=your_api_key_here
```

The `.env` file is ignored by Git and must never be uploaded to GitHub.

### 5. Run the analysis

```bash
python INTC_python.py
```

The program retrieves the most recent available records, calculates the metrics, prints a summary report, saves the processed records to SQLite, and runs the SQL analyses.

## Results

The written report covers the 100 most recent trading days ending May 8, 2026:

- INTC more than tripled, from a low close of $39.37 to $124.92 on May 8.
- 52 of 100 trading days were classified as High volatility, 46 as Moderate, and only 2 as Low.
- The system generated 49 Hold, 35 Sell, and 16 Buy signals.
- The most recent signal was **Hold**: positive momentum, but volatility too high to justify buying.

**About the database file:** `intc_stock_data.db` holds records from later runs (December 17, 2025 to May 14, 2026), so its counts differ slightly from the report. Because the script always pulls the 100 most recent trading days, running it today will produce a new, different snapshot.

## Limitations

- The signal rules use only daily price data and do not consider financial statements, news, market conditions, analyst estimates, or broader economic factors.
- The model uses fixed thresholds that may not be appropriate for every stock or time period.
- Alpha Vantage API limits can affect how frequently data can be retrieved.
- A historical signal does not guarantee future performance.
- The database is a snapshot of the records retrieved when the program was run and should be regenerated when updating the analysis.

## Future improvements

- Add technical indicators such as moving averages and RSI.
- Compare Intel with other semiconductor companies.
- Add automated data visualizations.
- Separate data collection, analysis, and reporting into reusable modules.
- Add unit tests for the business rules and data-validation functions.
- Build an interactive dashboard with Tableau or Streamlit.

## Author

Julie Loyez  
MS in Business Analytics student
