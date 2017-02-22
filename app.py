import dash
from dash_core_components import Dropdown, Graph
from dash_html_components import Div, H3, Link

from plotly import graph_objs as go
from pandas_datareader import data as web
from datetime import datetime as dt

app = dash.react.Dash('Hello World')

# Describe the layout, or the UI, of the app
app.layout = Div([
    # Include Dropdown's CSS - Won't be necessary in upcoming version
    Link(
        rel="stylesheet",
        href="https://unpkg.com/react-select@1.0.0-rc.3/dist/react-select.css"
    ),

    H3('Hello World'),
    Dropdown(
        id='my-dropdown',
        options=[
            {'label': 'Coke', 'value': 'COKE'},
            {'label': 'Tesla', 'value': 'TSLA'},
            {'label': 'Apple', 'value': 'AAPL'}
        ],
        value='COKE'
    ),
    Graph(id='my-graph')
])

# Register a callback to update 'my-graph' component when 'my-dropdown' changes
@app.react('my-graph', ['my-dropdown'])
def update_graph(dropdown_properties):
    df = web.DataReader(
        dropdown_properties['value'], 'yahoo',
        dt(2017, 1, 1), dt.now()
    )
    return {
        'figure': go.Figure(
            data=[{
                'x': df.index,
                'y': df.Close
            }]
        )
    }

# Boiler plate
app.component_suites=[
    'dash_core_components',
    'dash_html_components'
]

# Run the server
if __name__ == '__main__':
    app.server.run(debug=True)
