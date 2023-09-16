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

app = Dash(__name__,
          meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.2, minimum-scale=0.5,'}])
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
