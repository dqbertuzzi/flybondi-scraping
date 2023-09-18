from datetime import datetime, timezone, timedelta
import pandas as pd
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import plotly.express as px
from bs4 import BeautifulSoup as bs
import numpy as np
import requests
from concurrent.futures import ThreadPoolExecutor

sheet_id = "18hHWaMBcvorBC9TRqBhG2HcGKpRZBdgZh3OqPw8ASus"
dataFrame = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv", dtype={'Preco':float,
                                                                                                       'DataPesquisada':str,
                                                                                                       'IdaVolta':str})

dff=dataFrame.to_dict('records')
scraper = FlightPriceScraper(sheet_id)

class FlightPriceScraper:
    def __init__(self, sheet_id):
        self.sheet_id = sheet_id
        
    def getPrices(self, depDate, retDate, soup):
        div_prices = soup.find_all('div', class_='jsx-4043887309 flex flex-column flex-auto items-center mr1-m mr2-ns mw4l w-50 w-33-l ph2 pa0-ns')
        departure_price = float(div_prices[0].find('span', class_="jsx-2642904360").text.replace("R$", "")[:-2].replace(".", "") + '.' + div_prices[0].find('span', class_="jsx-2642904360").text.replace("R$", "")[-2:])
        return_price = float(div_prices[1].find('span', class_="jsx-2642904360").text.replace("R$", "")[:-2].replace(".", "") + '.' + div_prices[1].find('span', class_="jsx-2642904360").text.replace("R$", "")[-2:])
        
        total = departure_price + return_price
        
        return np.round(total, 2), depDate, retDate
    
    def appendData(self, df, total, depDate, retDate, date):
        new_data = {'Preco': [total],
            'DataPesquisada': [date],
            'IdaVolta': [pd.to_datetime(depDate).strftime("%d/%m/%Y") + " - " + pd.to_datetime(retDate).strftime("%d/%m/%Y")]}
        
        return pd.concat([df, pd.DataFrame(new_data)], ignore_index=True)
    
    def fetch_flight_prices(self, depDate, retDate):
        url = f'https://flybondi.com/br/search/results?adults=1&children=0&currency=BRL&departureDate={depDate}&fromCityCode=SAO&infants=0&returnDate={retDate}&toCityCode=BUE&utm_origin=calendar'
        page = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'})
        soup = bs(page.text, 'html.parser')
        total, depDate, retDate = scraper.getPrices(depDate, retDate, soup)
        
        return total, depDate, retDate

app = Dash(__name__,
          meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5,'}])

server = app.server

# App layout
app.layout = html.Div([
    dcc.Store(id="storage", storage_type="memory", data=dff),
    html.Div(children='Monitor de Preços Flybondi - São Paulo x Buenos Aires'),
    html.Br(),
    html.Button("Atualizar os dados (Isso pode levar alguns minutos)",id='refresh-button', n_clicks=0),
    html.Hr(),
    html.Div(children='Escolha Data de Ida e Volta:'),
    html.Br(),
    dcc.Dropdown(options=['15/12/2023 - 21/12/2023', '16/12/2023 - 22/12/2023', '17/12/2023 - 23/12/2023'],
                 value='15/12/2023 - 21/12/2023',
                 id='my-final-radio-item-example'),
    dcc.Graph(figure={}, id='my-final-graph-example')
])

# Add controls to build the interaction
@callback(
    Output(component_id='storage', component_property='data'),
    Input(component_id='refresh-button', component_property='n_clicks'),
    prevent_initial_call=True
)
def refresh_data(n_clicks):
    if n_clicks:
        date = (datetime.now(timezone.utc) - timedelta(hours=3)).strftime('%d/%m %H:%M')
        sheet_id = "18hHWaMBcvorBC9TRqBhG2HcGKpRZBdgZh3OqPw8ASus"
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        data_frame = pd.read_csv(url, dtype={'Preco': float, 'DataPesquisada': str, 'IdaVolta': str}, parse_dates=['DataPesquisada'])
    
        dates = [('2023-12-15', '2023-12-21'), ('2023-12-16', '2023-12-22'), ('2023-12-17', '2023-12-23')]
        
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(lambda date_pair: scraper.fetch_flight_prices(*date_pair), dates))
    
        for total, depDate, retDate in results:
            data_frame = scraper.appendData(data_frame, total, depDate, retDate, date=date)
        
    return data_frame.to_dict('records')
        
@callback(
    Output(component_id='my-final-graph-example', component_property='figure'),
    Input(component_id='my-final-radio-item-example', component_property='value'),
    Input("storage", "data"),
    Input(component_id='refresh-button', component_property='n_clicks')
)
def update_graph(col_chosen, stored_dataframe, n_clicks):
    dff = pd.DataFrame.from_records(stored_dataframe)
    dff['DataPesquisada'] = [i.replace(year=2023) for i in pd.to_datetime(dff['DataPesquisada'], format='%d/%m %H:%M')]
    
    fig = px.line(dff[dff['IdaVolta']==col_chosen], x='DataPesquisada', y='Preco',
                   color_discrete_sequence =['#25291C'],
                 labels={"Preco":"Preço (R$)", "DataPesquisada":"Data/Hora Pesquisada"}, title="Histórico de Preços", markers=True, range_x=[(datetime.now(timezone.utc) - timedelta(days=3)),(datetime.now(timezone.utc) + timedelta(hours=12))])
    #
    fig.update_traces(marker=dict(size=8),
                  line=dict(width=3))
    fig.update(layout_yaxis_range = [dff[dff['IdaVolta']==col_chosen]['Preco'].min()-8,dff[dff['IdaVolta']==col_chosen]['Preco'].max()+8])

    fig.add_scatter(x = [fig.data[0].x[-1]], y = [fig.data[0].y[-1]],
                     mode = 'markers + text',
                     marker = {'color':'black', 'size':14},
                     showlegend = False,
                     text = [fig.data[0].y[-1]],
                     textposition='top center')
    fig.update_traces(textfont_size=14)
    fig.update_xaxes(rangeslider_visible=True)


    return fig


if __name__ == '__main__':
    app.run(debug=True)
