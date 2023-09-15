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

app = Dash(__name__)
server = app.server

app.layout = html.Div([
    dcc.Store(id="storage", storage_type="memory", data=dff),
    #dcc.Interval(id="timer", interval=1000*60, n_intervals=0),
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
        sheet_id = "18hHWaMBcvorBC9TRqBhG2HcGKpRZBdgZh3OqPw8ASus"
        dataFrame = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv", dtype={'Preco':float,
                                                                                                       'DataPesquisada':str,
                                                                                                       'IdaVolta':str})
        
    return dataFrame.to_dict('records')
        
@callback(
    Output(component_id='my-final-graph-example', component_property='figure'),
    Input(component_id='my-final-radio-item-example', component_property='value'),
    Input("storage", "data"),
    Input(component_id='refresh-button', component_property='n_clicks')
)
def update_graph(col_chosen, stored_dataframe, n_clicks):
    dff = pd.DataFrame.from_records(stored_dataframe)
        
    fig = px.bar(dff[dff['IdaVolta']==col_chosen], x='DataPesquisada', y='Preco',
                 labels={"Preco":"Preço (R$)", "DataPesquisada":"Data/Hora Pesquisada"}, text_auto=True,
                 title="Histórico de Preços")
    fig.update_traces(width=.2)
    return fig


if __name__ == '__main__':
    app.run(debug=True)
