from dash.react import Dash
from dash_core_components import Graph
import dash_html_components as html
import plotly
import json
import pandas as pd

df = pd.read_csv(
    'https://raw.githubusercontent.com/plotly'
    '/datasets/master/gapminderDataFiveYear.csv'
)

dash = Dash(__name__)

columnStyle = {'width': '30%', 'float': 'left', 'display': 'inline-block'}
graphStyle = {
    'height': '100vh',
    'width': '40%',
    'float': 'left',
    'display': 'inline-block'
}

def graph(df, year):
    return {
        'data': [
            {
                'x': df.lifeExp[df.year == year],
                'y': df.gdpPercap[df.year == year],
                'text': df.country[df.year == year],
                'mode': 'markers',
                'marker': {'size': 10}
            }
        ],
        'layout': {
            'title': 'Life Exp vs GDP per Capita, <b>{}</b>'.format(year),
            'margin': {'t': 80, 'r': 20, 'l': 40, 'b': 40},
            'yaxis': {'type': 'log'}
        }
    }

dash.layout = html.Div([
    html.Link(
        rel="stylesheet",
        href="https://cdnjs.cloudflare.com/ajax/libs"
             "/skeleton/2.0.4/skeleton.min.css"
    ),

    Graph(id='graph-1952', figure=graph(df, 1952), style=graphStyle),

    Graph(id='graph-2007', figure=graph(df, 2007), style=graphStyle),

    html.Div([
        html.H5('Selected Countries'),
        html.Div(id='table'),
    ], style={
        'height': '100vh',
        'overflowY': 'scroll',
        'width': '19%',
        'float': 'left',
        'display': 'inline-block'
    }),

    html.Div([
        html.H4('Hover Data'),
        html.Pre(id='hover-data'),
    ], style=columnStyle),
    html.Div([
        html.H4('Click Data'),
        html.Pre(id='click-data'),
    ], style=columnStyle),
    html.Div([
        html.H4('Selection Data'),
        html.Pre(id='selected-data'),
    ], style=columnStyle)
])

callback_data = [
    {'element': 'hover-data', 'event': 'hover', 'prop': 'hoverData'},
    {'element': 'click-data', 'event': 'click', 'prop': 'clickData'},
    {'element': 'selected-data', 'event': 'selected', 'prop': 'selectedData'}
]

for callback in callback_data:
    @dash.react(callback['element'],
                events=[
                    {'id': 'graph-1952', 'event': callback['event']},
                    {'id': 'graph-2007', 'event': callback['event']}
                ],
                state=[
                    {'id': 'graph-1952', 'prop': callback['prop']},
                    {'id': 'graph-2007', 'prop': callback['prop']}
                ])
    def update(graph1, graph2):
        return {
            'content': (
                json.dumps(graph1, sort_keys=True, indent=2) +
                '\n' +
                json.dumps(graph2, sort_keys=True, indent=2)
            )
        }


def get_selected_countries(selection):
    indices = [p['pointNumber'] for p in selection['points']]
    df_2007 = df[df.year == 2007]
    df_2007.index = range(len(df_2007))
    reduced_df = df_2007[df_2007.index.isin(indices)]
    return list(reduced_df.country)

@dash.react('graph-1952',
            events=[{'id': 'graph-2007', 'event': 'selected'}],
            state=[{'id': 'graph-2007', 'prop': 'selectedData'}])
def filter_graph(selection):
    filtered_countries = get_selected_countries(selection)
    figure = graph(df, 1952)
    countries = figure['data'][0]['text']
    figure['data'][0]['marker']['opacity'] = [
        1 if c in filtered_countries else 0.1 for c in countries
    ]
    return {'figure': figure}

@dash.react('table',
            events=[{'id': 'graph-2007', 'event': 'selected'}],
            state=[{'id': 'graph-2007', 'prop': 'selectedData'}])
def filter_graph(selection):
    filtered_countries = get_selected_countries(selection)
    return {
        'content': html.Div([html.Div(c) for c in filtered_countries])
    }


if __name__ == '__main__':
    dash.run_server(component_suites=[
        'dash_html_components',
        'dash_core_components'
    ])
