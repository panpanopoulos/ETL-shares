# ETL-shares
A data pipeline which runs automatically on a daily basis and extracts datasets of market shares minute by minute prices, transforms them to calculate specific metrics and loads a report with these metrics inside a targeted repository for a specific date.
The source data are downloaded from Deutsche Börse, the German marketplace organizer for trading shares.
The Data pipeline performs the following actions:
1. Runs an ETL process on a daily basis which is configured and scheduled via airflow
2. Extracts the all the source datasets for the targeted day according to meta_file (more info below) and aggregates them in a single dataset
3. Performs several transformations by filtering out unecessary columns, and calculates for each share:
   * The opening, closing price, minimum and maximum price 
   * the Daily traded volume for the targeted date
   * The change percentage of the closing price between the targeted date and the previous date
4. Loads a report with the aforementioned metrics for the targeted date in a repository
5. Registers in the meta file the date which was processed
6. Logging during DAG execution through airflow

Prerequisites:
1. Python
2. Docker Desktop

## Project Folder structure

1. DAG: Contains the executable code for the ETL process and the DAG which defines the DAG execution parameters
2. load_reports: Contains the targeted repository in which the daily reports are loaded after the ETL execution
3. logs: Contains the logs of the DAG's execution
4. source_files: Contains the source files generated from The Deutsche Börse (minute by minute granularity)
5. meta_file: Meta file is used to keep the records of the dates for which the ETL process has run (registered after each ETL execution). Using the meta file, the script determines the next day for which the ETL process will run
6. etl_notebook: A jupyter notebook which contains the source and the transformed data as well as the code that the ETL process runs to generate the daily report
7. The rest files include configuration for python packages dependencies (Pipfiles) and a docker compose file (docker-compose.yaml) in order to run airflow in Docker

# Source Data Format

| ISIN         | Mnemonic | SecurityDesc            | SecurityType | Currency | SecurityID |       Date |  Time | StartPrice | MaxPrice | MinPrice | EndPrice | TradedVolume | NumberOfTrades |
|:-------------|:---------|:------------------------|-------------:|---------:|-----------:|-----------:|------:|-----------:|---------:|---------:|---------:|-------------:|---------------:|
| AT0000A0E9W5 | SANT     | S+T AG O.N.             | Common stock |      EUR |    2504159 | 2022-01-03 | 08:00 |     14.760 |   14.760 |   14.750 |   14.750 |         4414 |              2 |
| DE000A0DJ6J9 | S92      | SMA SOLAR TECHNOL.AG    | Common stock |      EUR |    2504287 | 2022-01-03 | 08:00 |     37.640 |   37.660 |   37.600 |   37.660 |         1649 |              3 |
| DE000A0D6554 | NDX1     | NORDEX SE O.N.          | Common stock |      EUR |    2504290 | 2022-01-03 | 08:00 |     13.990 |   14.030 |   13.940 |   13.960 |        23011 |             36 |
| DE000A0D9PT0 | MTX      | MTU AERO ENGINES NA O.N | Common stock |      EUR |    2504297 | 2022-01-03 | 08:00 |    180.000 |  180.050 |  179.500 |  179.500 |         2308 |             22 |
| DE000A0HN5C6 | DWNI     | DEUTSCHE WOHNEN SE INH  | Common stock |      EUR |    2504314 | 2022-01-03 | 08:00 |     37.280 |   37.280 |   37.280 |   37.280 |         2897 |              1 |

# Transformed Data Format (Report)

| ISIN         | Date       | opening_price_euro | closing_price_euro | minimum_price_euro | maximum_price_euro | daily_traded_volume | change_prev_closing_% |
|:-------------|:-----------|-------------------:|-------------------:|-------------------:|-------------------:|--------------------:|----------------------:|
| AT000000STR1 | 2022-01-04 |              37.75 |              37.85 |              37.75 |              37.85 |                  27 |                  1.20 |
| AT00000FACC2 | 2022-01-04 |               7.86 |               7.79 |               7.79 |               7.95 |                 681 |                  1.83 |
| AT0000606306 | 2022-01-04 |              26.00 |              26.80 |              26.00 |              26.80 |                 339 |                  3.63 |
| AT0000609607 | 2022-01-04 |              13.78 |              13.72 |              13.72 |              13.78 |                 400 |                  0.59 |
| AT0000644505 | 2022-01-04 |             123.20 |             123.20 |             123.20 |             123.20 |                  13 |                  3.53 |

# Instructions for setting up the data pipeline
1. Clone the repository
2. Install pipenv package if not installed by "pip install pipenv"
3. Create a virtual environment by "pipenv shell"
4. Install all dependencies from pipfile by "pipenv sync"
5. Open docker desktop
6. Install/run airflow by "docker-compose up -d"
7. Go to http://localhost:8080/home and connect using airflow as both username and password
8. Enable the ETL_DAG
