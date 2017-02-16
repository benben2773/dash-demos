import dash
import dash_html_components as html
from dash_core_components import Graph, Dropdown, Input
import pandas as pd
import pandas_datareader.data as web
import datetime as dt


app = dash.react.Dash('my app')
app.component_suites = [
    'dash_html_components',
    'dash_core_components'
]

app.layout = html.Div([
    html.Link(
        rel="stylesheet",
        href="https://cdnjs.cloudflare.com/ajax/libs/skeleton"
             "/2.0.4/skeleton.min.css"
    ),
    html.Link(
        rel="stylesheet",
        href="https://unpkg.com/react-select@1.0.0-rc.3/dist/react-select.css"
    ),
    html.Link(
        rel="stylesheet",
        href="https://cdn.rawgit.com/chriddyp/abcbc02565dd495b676c3269240e09ca"
             "/raw/816de7d5c5d5626e3f3cac8e967070aa15da77e2/rc-slider.css"
    ),

    html.H1('hello world'),
    html.Div(id='update-text'),
    Dropdown(id='my-input', value='COKE', options=[
        {'label': 'Coke', 'value': 'COKE'},
        {'label': 'Apple', 'value': 'AAPL'},
        {'label': 'Tesla', 'value': 'TLSA'},
    ]),
    Graph(
        id='my-graph',
        figure={
            'data': [{'x': [1, 2, 3], 'y': [4, 1, 5]}]
        }
    )
])


@app.react('update-text', ['my-input'])
def update_text(input):
    input_value = input['value']
    df = web.DataReader(input['value'], 'yahoo',
                        dt.datetime(2016, 6, 1),
                        dt.datetime(2017, 2, 15))
    max_value = df.Open.max()
    min_value = df.Open.max()
    return {
        'content': html.H4(
            '{} < {} < {}'.format(min_value, input_value, max_value)
        )
    }

@app.react('my-graph', ['my-input'])
def update_graph(input):
    df = web.DataReader(input['value'], 'yahoo',
                        dt.datetime(2016, 6, 1),
                        dt.datetime(2017, 2, 15))

    return {
        'figure': {
            'data': [{
                'x': df.index,
                'open': df.Open,
                'high': df.High,
                'low': df.Low,
                'close': df.Close,
                'type': 'candlestick',
                'name': input['value']
            }],
            'layout': {
                'title': input['value']
            }
        }
    }


app.server.run(debug=True)
