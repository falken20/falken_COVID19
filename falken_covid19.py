import logging
import os
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

from dotenv import load_dotenv, find_dotenv
from datetime import date

# Load env file
load_dotenv(find_dotenv())

# Set log level and secret key
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'ERROR'))


if __name__ == '__main__':
    # Get the number of the today day
    day = int(str(date.today())[-2:])

    # Get the data for every month
    url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data' \
          '/csse_covid_19_daily_reports '
    list_urls = []

    # Add links for every day data in September
    for i in range(1, 31):
        if i <= 9:
            list_urls.append(str(url + f'/09-0{i}-2020.csv'))
        else:
            list_urls.append(str(url + f'/09-{i}-2020.csv'))
    # Add links for every day in the current month
    for i in range(1,day):
        if i <= 9:
            list_urls.append(str(url + f'/10-0{i}-2020.csv'))
        else:
            list_urls.append(str(url + f'/10-{i}-2020.csv'))

    logging.info('Start to get the data from urls')
    # Transform the urls in a dataframe and these in a list
    list_data = []
    for i in list_urls:
        df = pd.read_csv(i)
        df_spain = df[df['Country_Region'] == 'Spain']
        np.array(df_spain)
        list_data.append(df_spain)
    print(list_data[3].head())

    # Get the column info del DataFrame
    print(list_data[0].info())

    # Generate descriptive statistics, round to 2 decimals
    print(round(list_data[3].describe(), 2))

    # Create the lists for the graphs
    list_dead_cases = []
    list_confirmed_cases = []
    list_recovered_cases = []

    # Sum the number of cases in every day
    for i in range(0, len(list_data)):
        list_dead_cases.append((list_data[i]['Deaths']).sum())
        list_confirmed_cases.append((list_data[i]['Confirmed']).sum())
        list_recovered_cases.append((list_data[i]['Recovered']).sum())

    print(len(list_dead_cases), list_dead_cases)
    print(len(list_confirmed_cases), list_confirmed_cases)
    print(len(list_recovered_cases), list_recovered_cases)

    # Create the graph
    x = [i for i in range(0, len(list_dead_cases))]
    plt.style.use('seaborn-talk')
    plt.plot(x, list_dead_cases, color='red', label='Dead cases', linewidth=1.0)
    plt.plot(x, list_confirmed_cases, color='green', label='Confirmed cases', linewidth=1.0)
    plt.plot(x, list_recovered_cases, color='blue', label='Recovered cases', linewidth=1.0)
    plt.xlabel('Days')
    plt.ylabel('People number')
    plt.title('COVID-19 evolution in Spain')
    plt.grid(True)
    plt.legend(loc='upper left')
    # plt.savefig('corona.png')
    plt.show()