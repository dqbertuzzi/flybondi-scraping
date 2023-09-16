import os
import numpy as np
import pandas as pd
import requests
from datetime import datetime
from bs4 import BeautifulSoup as bs
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# Constants
CLIENT_SECRET_FILE = 'client_secrets.json'
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']
SHEET_ID = #Change SHEET_ID
file_id = #Change file_id
parents = #Change parents

def get_prices(dep_date, ret_date):
    url = f'https://flybondi.com/br/search/results?adults=1&children=0&currency=BRL&departureDate={dep_date}&fromCityCode=SAO&infants=0&returnDate={ret_date}&toCityCode=BUE&utm_origin=calendar'
    page = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'})
    soup = bs(page.text, 'html.parser')
    
    div_prices = soup.find_all('div', attrs={'class': 'jsx-4043887309 flex flex-column flex-auto items-center mr1-m mr2-ns mw4l w-50 w-33-l ph2 pa0-ns'})
    
    departure_price = float(div_prices[0].find('span', attrs={'class': "jsx-2642904360"}).text.replace("R$", "")[:-2].replace(".", "") + '.' + div_prices[0].find('span', attrs={'class': "jsx-2642904360"}).text.replace("R$", "")[-2:])
    return_price = float(div_prices[1].find('span', attrs={'class': "jsx-2642904360"}).text.replace("R$", "")[:-2].replace(".", "") + '.' + div_prices[1].find('span', attrs={'class': "jsx-2642904360"}).text.replace("R$", "")[-2:])
    total = departure_price + return_price
    
    return [np.round(total, 2), dep_date, ret_date]

def append_data(total, dep_date, ret_date):
    data_frame = pd.read_csv("dataFrame.csv", sep=';')
    data_frame = pd.concat([data_frame, pd.DataFrame({'Preco': [total],
                                                      'DataPesquisada': [date],
                                                      'IdaVolta': pd.to_datetime(dep_date).strftime("%d/%m/%Y") + " - " + pd.to_datetime(ret_date).strftime("%d/%m/%Y")})],
                           ignore_index=True)
    data_frame.to_csv("dataFrame.csv", index=False, sep=';')

def create_service(client_secret_file, api_name, api_version, *scopes, prefix=''):
    creds = None
    working_dir = os.getcwd()
    token_dir = 'token files'
    token_file = f'token_{api_name}_{api_version}{prefix}.json'

    if not os.path.exists(os.path.join(working_dir, token_dir)):
        os.mkdir(os.path.join(working_dir, token_dir))

    if os.path.exists(os.path.join(working_dir, token_dir, token_file)):
        creds = Credentials.from_authorized_user_file(os.path.join(working_dir, token_dir, token_file), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(os.path.join(working_dir, token_dir, token_file), 'w') as token:
            token.write(creds.to_json())

    try:
        service = build(api_name, api_version, credentials=creds, static_discovery=False)
        print(api_name, api_version, 'service created successfully')
        return service
    except Exception as e:
        print(e)
        print(f'Failed to create service instance for {api_name}')
        os.remove(os.path.join(working_dir, token_dir, token_file))
        return None

data_frame = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv", dtype={'Preco': float,
                                                                                                      'DataPesquisada': str,
                                                                                                      'IdaVolta': str})
data_frame.to_csv("dataFrame.csv", index=False, sep=';')

date = datetime.now().strftime("%d/%m %H:%M")

dates = [('2023-12-15', '2023-12-21'), ('2023-12-16', '2023-12-22'), ('2023-12-17', '2023-12-23')]
for dep_date, ret_date in dates:
    total, dep_date, ret_date = get_prices(dep_date=dep_date, ret_date=ret_date)
    append_data(total, dep_date, ret_date)

service = create_service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
file = os.path.join(os.getcwd(), 'dataFrame.csv')

file_metadata = {
    'name': 'dataFrame.csv',
    'parents': parents
}

file_content = MediaFileUpload('dataFrame.csv')

service.files().update(
    fileId=file_id,
    media_body=file_content
).execute()
