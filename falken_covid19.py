import logging
import os
from typing import List, Any, Union
from urllib.error import HTTPError
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from dotenv import load_dotenv, find_dotenv
from datetime import date

from config_pk import SETUP_DATA

URL_CSV_FILES = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/' \
                'csse_covid_19_daily_reports'

# Load env file
load_dotenv(find_dotenv())

# Set log level and secret key
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'ERROR'))


def create_list_urls(_year_to_process=2020, _month_from=3):
    """
    Load all the urls of daily data of a specific year and from a specific month
    :param _year_to_process: Year to load
    :param _month_from: From this month start to load data
    :return:
    """

    if _year_to_process is None or _year_to_process == '':
        _year_to_process = 2020
    if _month_from is None or _month_from == '':
        _month_from = 3
    logging.info(f'Load a list with the CSV file names, one per every day from {_year_to_process}/{_month_from}')

    _list_urls = []
    try:
        # Get the number of the day in the current month
        # day = int(str(date.today())[-2:])
        current_day = date.today().day
        current_month = date.today().month
        logging.info(f'Current month and day: {current_month} / {current_day}')

        # Load links for every day in all the months of the year least the current month
        for month in range(int(_month_from), current_month):
            for day in range(1, 32):
                _list_urls.append(str(URL_CSV_FILES + f'/{str(month).zfill(2)}-{str(day).zfill(2)}-{_year_to_process}.csv'))

        # Add links for every day in the current month
        for day in range(1, current_day):
            _list_urls.append(str(URL_CSV_FILES + f'/{str(current_month).zfill(2)}-{str(day).zfill(2)}-{_year_to_process}.csv'))

        logging.info(f'Number of urls of data files: {len(_list_urls)}')

    except Exception as err:
        logging.error(f'Error in method create_list_urls: \n {err}')

    finally:
        return _list_urls


def load_data_urls(_list_urls):
    """
    Load the data for every url list element
    :param _list_urls: List where every element is a url to a CSV file data source
    """

    logging.info('Start to get the data from urls')
    _list_data = []
    count = 0
    try:
        for url in _list_urls:
            try:
                df = pd.read_csv(url, error_bad_lines=False)
            except HTTPError:
                logging.error(f'File not found: {url}')

            # Filter for loading only spanish data from every url
            try:
                df_spain = df[df['Country/Region'] == 'Spain']
            except KeyError:
                df_spain = df[df['Country_Region'] == 'Spain']

            np.array(df_spain)
            _list_data.append(df_spain)

            count += 1
            if count % 10 == 0:
                logging.info(f'Processing spanish data dataframes: {count}/{len(_list_urls)}')

    except Exception as err:
        logging.error(f'Error in method load_data_urls: \n {err}')

    finally:
        return _list_data


def generate_graph(_list_data):
    """
    Methos for generate the graph with the data
    :param _list_data: List of data
    """

    logging.info('Start to generate the graph')

    # Create the lists for the graphs
    list_dead_cases = []
    list_confirmed_cases = []
    list_recovered_cases = []

    # Sum the number of cases in every day
    for i in range(0, len(_list_data)):
        list_dead_cases.append((_list_data[i]['Deaths']).sum())
        list_confirmed_cases.append((_list_data[i]['Confirmed']).sum())
        list_recovered_cases.append((_list_data[i]['Recovered']).sum())

    # Generate the graph
    x = [i for i in range(0, len(list_dead_cases))]
    plt.style.use('seaborn-talk')
    plt.plot(x, list_dead_cases, color='red', label='Dead cases', linewidth=1.0)
    # plt.plot(x, list_confirmed_cases, color='green', label='Confirmed cases', linewidth=1.0)
    # plt.plot(x, list_recovered_cases, color='blue', label='Recovered cases', linewidth=1.0)
    plt.xlabel('Days')
    plt.ylabel('People number')
    plt.title('COVID-19 evolution in Spain')
    plt.grid(True)
    plt.legend(loc='upper left')
    # plt.savefig('falken_graph.png')
    plt.show()


if __name__ == '__main__':

    print(f'********* {SETUP_DATA["title"]} ********* ')

    # Create a list with the urls to a every data day
    year_to_process = input(f'Year to process (default=2020):')
    month_from = input(f'Month number to start (default=3):')
    list_urls = create_list_urls(year_to_process, month_from)

    # Transform the urls in a dataframe and after that in a list and filtering by Spain
    list_data = load_data_urls(list_urls)

    # Print several help info to confirm info
    # print(list_data[3].head())
    # print(list_data[0].info()) # Get the column info del DataFrame
    print(round(list_data[3].describe(), 2)) # Generate descriptive statistics, round to 2 decimals

    # Create the graph
    generate_graph(list_data)

