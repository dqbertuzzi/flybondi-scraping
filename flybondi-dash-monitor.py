from datetime import datetime
import pandas as pd
from dash import Dash, html
import plotly.express as px
from dash import Dash, html, dash_table, dcc, callback, Output, Input

sheet_id = "18hHWaMBcvorBC9TRqBhG2HcGKpRZBdgZh3OqPw8ASus"
dataFrame = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv", dtype={'Preco':float,
                                                                                                       'DataPesquisada':str,
                                                                                                       'IdaVolta':str})

app = Dash(__name__)

# App layout
app.layout = html.Div([
    html.Div(children='Monitor de Preços Flybondi - São Paulo x Buenos Aires'),
    html.Hr(),
    html.Div(children='Escolha Data de Ida e Volta:'),
    html.Br(),
    dcc.RadioItems(options=dataFrame['IdaVolta'].unique(), value=dataFrame['IdaVolta'].unique()[0], id='my-final-radio-item-example'),
    dcc.Graph(figure={}, id='my-final-graph-example'),
    dcc.Interval(
    id='interval-component',
        interval=1*1000,
        n_intervals=0
    )
])

# Add controls to build the interaction
@callback(
    Output(component_id='my-final-graph-example', component_property='figure'),
    Input(component_id='my-final-radio-item-example', component_property='value')
)

def update_graph(col_chosen):
    sheet_id = "18hHWaMBcvorBC9TRqBhG2HcGKpRZBdgZh3OqPw8ASus"
    dataFrame = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv", dtype={'Preco':float,
                                                                                                       'DataPesquisada':str,
                                                                                                       'IdaVolta':str})
    
    
    fig = px.bar(dataFrame[dataFrame['IdaVolta']==col_chosen], x='DataPesquisada', y='Preco')
    return fig

if __name__ == '__main__':
    app.run(debug=True)
