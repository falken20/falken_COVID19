import logging
import os
import sys
from urllib.error import HTTPError

import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from dotenv import load_dotenv, find_dotenv
from datetime import date

# Heat map
import folium
import math
from folium.plugins import HeatMap

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
                _list_urls.append(
                    str(URL_CSV_FILES + f'/{str(month).zfill(2)}-{str(day).zfill(2)}-{_year_to_process}.csv'))

        # Add links for every day in the current month
        for day in range(1, current_day):
            _list_urls.append(
                str(URL_CSV_FILES + f'/{str(current_month).zfill(2)}-{str(day).zfill(2)}-{_year_to_process}.csv'))

        logging.info(f'Number of urls of data files: {len(_list_urls)}')

    except Exception as err:
        logging.error(f'Error in method create_list_urls: \n {err}')

    finally:
        return _list_urls


def load_data_urls(_list_urls, _only_spain):
    """
    Load the data for every url list element
    :param _only_spain: For filtering by Spain or Global
    :param _list_urls: List where every element is a url to a CSV file data source
    """

    logging.info(f'Start to get the data from urls ({"Spain" if _only_spain else "Global"})')

    _list_data = []
    count = 0
    try:
        for url in _list_urls:
            try:
                df_data = pd.read_csv(url, error_bad_lines=False)
            except HTTPError:
                logging.error(f'File not found: {url}')

            # If the user want to filter for loading only spanish data from every url
            if _only_spain:
                try:
                    df_data = df_data[df_data['Country/Region'] == 'Spain']
                except KeyError:
                    # The old files had another name in the column
                    df_data = df_data[df_data['Country_Region'] == 'Spain']

            np.array(df_data)
            _list_data.append(df_data)

            count += 1
            if count % 10 == 0:
                logging.info(f'Processing {"Spain" if _only_spain else "Global"}: {count}/{len(_list_urls)}')

    except Exception as err:
        logging.error(f'Error in method load_data_urls: \n {err}')

    finally:
        return _list_data


def generate_data_lists(_list_data):
    """
    Method for generate several lists for dead data, confirmed cases and recovered cases
    :param _list_data:
    :return: Three lists with separated data
    """

    logging.info('Start to generate the different lists for dead, confirmed and recovered data')

    # Create the lists for the graphs
    _list_dead_cases = []
    _list_confirmed_cases = []
    _list_recovered_cases = []

    # Sum the number of cases in every day
    for i in range(0, len(_list_data)):
        _list_dead_cases.append((_list_data[i]['Deaths']).sum())
        _list_confirmed_cases.append((_list_data[i]['Confirmed']).sum())
        _list_recovered_cases.append((_list_data[i]['Recovered']).sum())

    return _list_dead_cases, _list_confirmed_cases, _list_recovered_cases


def generate_graph(_list_data, _label, _color, _only_spain):
    """
    Method for generate the graph with the data
    :param _only_spain: For filtering by Spain or Global
    :param _color: Color for the line in the graph
    :param _label: Label to show in the plot
    :param _list_data: List of data to show
    """

    logging.info(f'Start to generate the graph of {_label}')

    # Generate the graph
    x = [i for i in range(0, len(_list_data))]
    plt.style.use('seaborn-talk')
    plt.plot(x, _list_data, color=_color, label=_label, linewidth=1.0)
    plt.xlabel('Days')
    plt.ylabel('People number')
    plt.title(f'COVID-19 Evolution {"Spain" if _only_spain else "Global"}')
    plt.grid(True)
    plt.legend(loc='upper left')
    # plt.savefig('falken_graph.png')
    plt.show()


def generate_heat_map(_list_data, _only_spain):
    """
    Method to generate a heat map with all the values
    :param _only_spain: For filtering by Spain or Global
    :param _list_data: List of values for every day
    """

    logging.info('Start to generate the heat map')

    try:
        heat_map = folium.Map(location=[43, 0],
                              zoom_start=f'{5 if _only_spain else 3}',
                              tiles='Stamen Toner',
                              width=f'{"50%" if _only_spain else "100%"}',
                              height=f'{"80%" if _only_spain else "100%"}')
        location = []

        for c in range(0, len(list_data)):
            for lat, lon in zip(list_data[c]['Latitude'], list_data[c]['Longitude']):
                if math.isnan(lat) or math.isnan(lon):
                    pass
                else:
                    location.append([lat, lon])

        HeatMap(location, radius=16).add_to(heat_map)
        heat_map.save(f'heatMap_{"Spain" if _only_spain else "Global"}.html')

        logging.info('Heat map successfully generated in html')

    except Exception as err:
        logging.error(f'ERROR in generate_heat_map at line {sys.exc_info()[2].tb_lineno}: \n '
                      f'{err} \n '
                      f'{list_data[c]}')


if __name__ == '__main__':

    print(f'********* {SETUP_DATA["title"]} ********* ')

    # Create a list with the urls to a every data day
    year_to_process = input(f'Year to process (default=2020):')
    month_from = input(f'Month number to start (default=3):')
    list_urls = create_list_urls(year_to_process, month_from)

    only_spain = input(f'Show data only for Spain(default Yes):')
    if only_spain.upper() == "NO" or only_spain.upper() == "N":
        only_spain = False
    else:
        only_spain = True

    # Transform the urls in a dataframe and after that in a list and filtering by Spain or Global
    list_data = load_data_urls(list_urls, only_spain)

    # Print several help info to confirm info
    # print(list_data[3].head())
    # print(list_data[0].info()) # Get the column info del DataFrame
    # print(round(list_data[3].describe(), 2))  # Generate descriptive statistics for a day, round to 2 decimals

    # Unify the column name for Latitude and Longitude because at the beginning the name was different
    logging.info('Unify the column name for Latitude and Longitude')
    for c in range(0, len(list_data)):
        list_data[c].rename(columns={'Lat': 'Latitude'}, inplace=True)
        list_data[c].rename(columns={'Long_': 'Longitude'}, inplace=True)

    # Get different lists for every kind of data, dead, confirmed cases and recovered cases
    dead_cases, confirmed_cases, recovered_cases = generate_data_lists(list_data)

    # Create the graphs
    generate_graph(dead_cases, 'Dead cases', 'red', only_spain)
    generate_graph(confirmed_cases, 'Confirmed cases', 'black', only_spain)
    generate_graph(recovered_cases, 'Recovered cases', 'blue', only_spain)

    # Generate summary table
    resume_data = \
        {'Dead cases': dead_cases[len(dead_cases) - 1],
         'Confirmed cases': confirmed_cases[len(confirmed_cases) - 1],
         'Recovered cases': recovered_cases[len(recovered_cases) - 1],
         'Mortality tax':
             round(dead_cases[len(dead_cases) - 1] / confirmed_cases[len(confirmed_cases) - 1] * 100, 2),
         'Recovered tax':
             round(recovered_cases[len(recovered_cases) - 1] / confirmed_cases[len(confirmed_cases) - 1] * 100, 2)
         }

    resume_data = pd.DataFrame(data=resume_data, index=[0])
    logging.info(f'Summary table ({"Spain" if only_spain else "Global"}): \n {resume_data}')

    # Generate heat map
    generate_heat_map(list_data, only_spain)
