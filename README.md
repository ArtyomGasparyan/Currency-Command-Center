# Currency Command Center

#### Video Demo: [Watch Here](<https://www.youtube.com/watch?v=Imezl3FmhxkS>)

#### Description:
This project is a web application that visualizes Armenian currency rates from various banks and the Central Bank of Armenia (CBA). The application fetches data from `rate.am` and CBA, processes it, and displays interactive charts that allow users to track and compare exchange rates over time. The application is built using Flask, Plotly, and MySQL for the backend.

## Features
- **Visualize Exchange Rates:** View interactive charts for USD, EUR, and RUB exchange rates over time.
- **Best Rates Display:** Display banks offering the best buy and sell rates for each currency.
- **Date Filters:** Filter data by selecting a custom date range.
- **Bank and Metric Filters:** Choose specific banks and metrics (e.g., USD Buy, USD Sell) to view on the charts.
- **Responsive UI:** User-friendly interface with a modern look and feel.
- **Splash Screen:** An animated introduction with fintech visuals to enhance user experience.

## Installation

### Prerequisites
- Python 3.11
- MySQL
- Pip

### Step-by-Step Guide

1. **Clone the Repository:**

2. **Install Required Python Packages:**
    ```python
    pip install -r requirements.txt
    ```

3. **Setup MySQL Database**

    ***Create a MySQL database named `currency_rates`.***

    ***Use the following schema to create the necessary tables:***

   **cba Table:**
   ```sql
   CREATE TABLE cba (
     Date DATE,
     EUR FLOAT,
     GBP FLOAT,
     RUB FLOAT,
     USD FLOAT
   );
   ```

   ***rate_am Table:***
   ```sql
    CREATE TABLE rate_am (
    bank_name VARCHAR(256),
    usd_buy FLOAT,
    eur_buy FLOAT,
    rur_buy FLOAT,
    usd_sell FLOAT,
    eur_sell FLOAT,
    rur_sell FLOAT,
    timestamp DATETIME
    );
    ```
## Environment Configuration

Set up a `.env` file with the following variables:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=currency_rates
```

## Run the Application

To start the application, run the following command in your terminal:

```bash
python app.py
```

## Project Structure

- **app.py**: Main application script with Flask routes and backend logic.
- **templates/index.html**: HTML template with embedded JavaScript for rendering charts.
- **static/videos/background.mp4**: Video file used in the splash screen.
- **requirements.txt**: Python dependencies required for the project.
- **mysql_magic.py**: Contains the `MySQLHandler` class for database interactions.
- **project.py**: Main data gathering engine from rate.am and CBA.
- **test_project.py**: Pytest test cases to validate the application functions.

## Key Components

### Backend

- **Flask**: Handles HTTP requests and renders templates.
- **SQLAlchemy**: Database connection and query execution.
- **Pandas**: Data manipulation and processing.

### Frontend

- **Plotly**: Interactive charts for visualizing data.
- **jQuery**: Handles asynchronous requests and DOM manipulation.

## How to Use

1. **Navigate to the Application**: Open your browser.

2. **Set Date Filters**: Use the date inputs to filter the data by a specific range.

3. **Select Bank and Metric**: Choose a bank and metric (e.g., USD Buy) to view on the right chart.

4. **View Best Rates**: The best rates section at the top shows the banks offering the best rates for each currency.

## Acknowledgements

- **Plotly**: For the interactive charting library used in the project.
- **Flask**: For the web framework that powers the application.
- **rate.am and the Central Bank of Armenia (CBA)**: For providing the currency data used in the application.






