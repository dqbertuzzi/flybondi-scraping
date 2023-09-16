from datetime import datetime
import pandas as pd
from dash import Dash, html
import plotly.express as px
from dash import Dash, html, dash_table, dcc, callback, Output, Input

sheet_id = "18hHWaMBcvorBC9TRqBhG2HcGKpRZBdgZh3OqPw8ASus"
dataFrame = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv", dtype={'Preco':float,
                                                                                                       'DataPesquisada':str,
                                                                                                       'IdaVolta':str})

dff=dataFrame.to_dict('records')

def getPrices(depDate, retDate):
    import numpy as np
    import requests
    
    url = f'https://flybondi.com/br/search/results?adults=1&children=0&currency=BRL&departureDate={depDate}&fromCityCode=SAO&infants=0&returnDate={retDate}&toCityCode=BUE&utm_origin=calendar'

    page = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'})

    soup = bs(page.text, 'html.parser')
    
    div_prices = soup.find_all('div', attrs={'class':'jsx-4043887309 flex flex-column flex-auto items-center mr1-m mr2-ns mw4l w-50 w-33-l ph2 pa0-ns'})
    
    departurePrice = float(div_prices[0].find('span', attrs={'class':"jsx-2642904360"}).text.replace("R$", "")[:-2].replace(".","")+'.'+div_prices[0].find('span', attrs={'class':"jsx-2642904360"}).text.replace("R$", "")[-2:])
    returnPrice = float(div_prices[1].find('span', attrs={'class':"jsx-2642904360"}).text.replace("R$", "")[:-2].replace(".","")+'.'+div_prices[1].find('span', attrs={'class':"jsx-2642904360"}).text.replace("R$", "")[-2:])
    total = departurePrice + returnPrice
    
    return [np.round(total,2), depDate, retDate]

def appendData(df, total, depDate, retDate, date):
    dataFrame = pd.concat([df, pd.DataFrame({'Preco':[total],
                                                'DataPesquisada':[date],
                                                'IdaVolta':pd.to_datetime(depDate).strftime("%d/%m/%Y") + " - "+ pd.to_datetime(retDate).strftime("%d/%m/%Y")})],
                      ignore_index=True)
    return dataFrame

app = Dash(__name__,
          meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5,'}])

# App layout
app.layout = html.Div([
    dcc.Store(id="storage", storage_type="memory", data=dff),
    html.Div(children='Monitor de Preços Flybondi - São Paulo x Buenos Aires'),
    html.Br(),
    html.Button("Atualizar os dados",id='refresh-button', n_clicks=0),
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
        date = datetime.now().strftime("%d/%m %H:%M")
        sheet_id = "18hHWaMBcvorBC9TRqBhG2HcGKpRZBdgZh3OqPw8ASus"
        dataFrame = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv", dtype={'Preco':float,
                                                                                                       'DataPesquisada':str,
                                                                                                       'IdaVolta':str})

        dates = [('2023-12-15', '2023-12-21'), ('2023-12-16', '2023-12-22'), ('2023-12-17', '2023-12-23')]
        for dep_date, ret_date in dates:
            total, dep_date, ret_date = getPrices(depDate=dep_date, retDate=ret_date)
            dataFrame = appendData(dataFrame, total, dep_date, ret_date, date=date)
        
    return dataFrame.to_dict('records')
        
@callback(
    Output(component_id='my-final-graph-example', component_property='figure'),
    Input(component_id='my-final-radio-item-example', component_property='value'),
    Input("storage", "data"),
    Input(component_id='refresh-button', component_property='n_clicks')
)
def update_graph(col_chosen, stored_dataframe, n_clicks):
    def improve_text_position(x):
        positions = ['top center', 'bottom center']  # you can add more: left center ...
        return [positions[i % len(positions)] for i in range(len(x))]
    
   
    dff = pd.DataFrame.from_records(stored_dataframe)
    
    fig = px.line(dff[dff['IdaVolta']==col_chosen], x='DataPesquisada', y='Preco',
                  text="Preco", color_discrete_sequence =['#25291C'],
                 labels={"Preco":"Preço (R$)", "DataPesquisada":"Data/Hora Pesquisada"}, title="Histórico de Preços")
    fig.update_traces(marker=dict(size=12),
                      line=dict(width=3),
                      textposition=improve_text_position(dff[dff['IdaVolta']==col_chosen]['Preco']),
                      textfont_size=14)
    fig.update(layout_yaxis_range = [dff[dff['IdaVolta']==col_chosen]['Preco'].min()-8,dff[dff['IdaVolta']==col_chosen]['Preco'].max()+8])
    fig.update_xaxes(range=[-1, len(dff[dff['IdaVolta']==col_chosen]['DataPesquisada'].unique())])

    
    return fig


if __name__ == '__main__':
    app.run(debug=True)
