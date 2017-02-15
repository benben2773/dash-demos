from dash.react import Dash
import dash_html_components as html
import dash_core_components
import pandas as pd
import pandas_datareader.data as web
import datetime as dt
import traceback
from flask import Flask


server = Flask(__name__)
dash = Dash(__name__, server=server)
dash.component_suites = [
    'dash_html_components',
    'dash_core_components'
]

print('test')

dash.layout = html.Div([
    html.Link(
        rel="stylesheet",
        href="https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css"
    ),
    html.H1('Yahoo Finance Stock Tickers', id='h1'),
    dash_core_components.Input(
        id='stock-ticker-input',
        placeholder='COKE',
        style={
            'fontSize': '1.5em',
            'fontWeight': 200,
            'border': 'none',
            'borderBottom': 'thin solid lightblue'
        },
        value='AAPL',
    ),
    dash_core_components.Graph(
        id='my-graph',
        figure={}
    )
])


# list of tickers
df_companies = pd.read_csv('https://raw.githubusercontent.com/'
                           'plotly/dash/master/companylist.csv')
tickers = [s.lower() for s in list(df_companies['Symbol'])]


@dash.react('my-graph', ['stock-ticker-input'])
def update_graph(stock_ticker_input):
    """ This function is called whenever the input
    'stock-ticker-input' changes.
    Query yahoo finance with the ticker input and update the graph
    'graph' with the result.
    """
    ticker = stock_ticker_input['value'].lower()
    if ticker not in tickers:
        raise Exception
    df = web.DataReader(ticker, 'yahoo', dt.datetime(2014, 1, 1),
                        dt.datetime(2015, 4, 15))
    return {
        'figure': {
            'data': [{
                'x': df.index,
                'y': df['Close']
            }],
            'layout': {
                'yaxis': {'title': 'Close'},
                'margin': {'b': 50, 'r': 10, 'l': 60, 't': 0}
            }
        }
    }

if __name__ == '__main__':
    dash.run_server()
