import dash
from dash_html_components import *
from dash_core_components import Graph
import json
import plotly.plotly as py

app = dash.react.Dash('Hover')

app.layout = Div([
    H2('Hover'),
    Graph(
        id='graph',
        figure=py.get_figure("https://plot.ly/~jackp/17498/")
    ),
    Div(content='', id='dom_state', style={'display': 'none'}),
])


# Capture the last hover'd data in the dom
@app.react('dom_state',
           events=[{'id': 'graph', 'event': 'hover'}],
           state=[{'id': 'graph', 'event': 'hoverData'}])
def update_dom_state(hoverData):
    return {'content': json.dumps(hoverData)}


# When you click on a point, pull the last hover
@app.react('update_name',
           events=[{'id': 'graph', 'event': 'click'}],
           state=[
                {'id': 'dom_state', 'prop': 'content'}
           ])
def update_name(hoverData, content):
    print hoverData, content
    return {'content': json.dumps(hoverData)}


app.component_suites = [
    'dash_html_components',
    'dash_core_components'
]

if __name__ == '__main__':
    app.server.run(debug=True)
