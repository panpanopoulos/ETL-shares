import os
import pandas as pd
from datetime import datetime, timedelta


def return_data_df(files_for_analysis, source_files_path):
    df_list = [pd.read_csv(source_files_path + '/' + file) for file in files_for_analysis]
    df_data = pd.concat(df_list, ignore_index=True)
    return df_data


def return_required_dates(meta_file_path, src_date_format, initial_date, today):
    df_meta_file = pd.read_csv(meta_file_path)
    processed_dates = set(
        map(lambda date: datetime.strptime(date, src_date_format).date(), df_meta_file.source_file_date))
    initial_date_dt = datetime.strptime(initial_date, src_date_format).date()
    datelist_till_today = set(
        [initial_date_dt + timedelta(days=x) for x in range(0, (today - initial_date_dt).days + 1)])
    date_to_process = min(datelist_till_today - processed_dates)
    previous_date = date_to_process - timedelta(days=1)
    if date_to_process.weekday() == 5:
        dates_with_no_data = [date_to_process, date_to_process + timedelta(days=1)]
        update_meta_file(meta_file_path, dates_with_no_data, [datetime.now().strftime('%Y-%m-%d, %H:%M:%S')] * 2)
        date_to_process += timedelta(days=2)
    return date_to_process, previous_date


def update_meta_file(meta_file_path, date_to_process, date_of_processing):
    df_meta = pd.read_csv(meta_file_path)
    df_new_row = pd.DataFrame.from_dict({'source_file_date': date_to_process, 'date_of_processing': date_of_processing})
    df_meta_new = pd.concat([df_meta, df_new_row])
    df_meta_new.to_csv(meta_file_path, index=False)


def extract(source_files_path, previous_date, date_to_process, src_date_format):
    directory_files = os.listdir(source_files_path)
    files_for_analysis = [file for file in directory_files if
                          file.startswith(previous_date.strftime(src_date_format))] +\
                         [file for file in directory_files if
                          file.startswith(date_to_process.strftime(src_date_format))]
    df_all = return_data_df(files_for_analysis, source_files_path)
    return df_all


def transform(df, columns, date_to_process, src_date_format):
    df = df.loc[:, columns]
    df.dropna(inplace=True)
    df['opening_price'] = df.sort_values(by=['Time']).groupby(['ISIN', 'Date'])['StartPrice'].transform('first')
    df['closing_price'] = df.sort_values(by=['Time']).groupby(['ISIN', 'Date'])['StartPrice'].transform('last')
    df = df.groupby(['ISIN', 'Date'], as_index=False).agg(opening_price_euro=('opening_price', 'min'),
                                                          closing_price_euro=('closing_price', 'min'),
                                                          minimum_price_euro=('MinPrice', 'min'),
                                                          maximum_price_euro=('MaxPrice', 'max'),
                                                          daily_traded_volume=('TradedVolume', 'sum'))
    df['prev_closing_price'] = df.sort_values(by=['Date']).groupby(['ISIN'])['closing_price_euro'].shift(1)
    df['change_prev_closing_%'] = (df['closing_price_euro'] - df['prev_closing_price']) / df['prev_closing_price'] * 100
    df.drop(columns=['prev_closing_price'], inplace=True)
    df = df.round(decimals=2)
    df = df[df.Date == date_to_process.strftime(src_date_format)]
    return df


def load_report(df, load_file_path, report_file_date):
    file_path = load_file_path + report_file_date + '.csv'
    df.to_csv(file_path, index=False)


def run_etl():
    SOURCE_FILES_PATH = 'source_files'
    META_FILE_PATH = 'meta_file.csv'
    LOAD_FILE_PATH = 'load_reports/'
    INITIAL_DATE = '2022-01-03'
    date_of_processing_meta = datetime.now().strftime('%Y-%m-%d, %H:%M:%S')
    src_date_format = '%Y-%m-%d'
    today = datetime.now().date()
    columns = ['ISIN', 'Date', 'Time', 'StartPrice', 'MaxPrice', 'MinPrice', 'EndPrice', 'TradedVolume']
    date_to_process, previous_date = return_required_dates(META_FILE_PATH, src_date_format, INITIAL_DATE, today)
    df_data = extract(SOURCE_FILES_PATH, previous_date, date_to_process, src_date_format)
    df_transformed = transform(df_data, columns, date_to_process, src_date_format)
    report_file_date = date_to_process.strftime(src_date_format)
    load_report(df_transformed, LOAD_FILE_PATH, report_file_date)
    update_meta_file(META_FILE_PATH, [date_to_process], [date_of_processing_meta])
