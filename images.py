from dash.react import Dash
from dash_core_components import Graph
import dash_html_components as html
import plotly
import pandas as pd

dash = Dash(__name__)

fig = plotly.plotly.get_figure("https://plot.ly/~jackp/17498/")
df = pd.read_csv('http://bit.ly/2mcrq5b')

dash.layout = html.Div([
    html.Link(
        rel="stylesheet",
        href="https://cdnjs.cloudflare.com/ajax/libs/skeleton"
             "/2.0.4/skeleton.min.css"
    ),
    html.Div([
        html.Div([
            Graph(id='graph', figure=fig, style={'width': '100%'}),
        ], className='eight columns'),
        html.Div([
            html.H3(id='info'),
            html.Img(id='img')
        ], className='four columns')
    ], className='row')
])


@dash.react('info',
            events=[{'id': 'graph', 'event': 'hover'}],
            state=[{'id': 'graph', 'prop': 'hoverData'}])
def display_molecule(clickData):
    print clickData
    pn = clickData['points'][0]['pointNumber']
    return {'content': str(fig['data'][0]['text'][pn])}


@dash.react('img',
            events=[{'id': 'graph', 'event': 'hover'}],
            state=[{'id': 'graph', 'prop': 'hoverData'}])
def display_image(clickData):
    pn = clickData['points'][0]['pointNumber']
    molecule_name = str(fig['data'][0]['text'][pn]).strip()
    DB_ID = df.loc[df['NAME'] == molecule_name]['PAGE'].to_string().split('/')[-1]
    src_tag = 'https://www.drugbank.ca/structures/' + DB_ID + '/thumb.svg'
    return {'src': src_tag}


if __name__ == '__main__':
    dash.component_suites = [
        'dash_core_components',
        'dash_html_components'
    ]
    dash.server.run(debug=True)
