from dash.react import Dash
from flask import Flask
import colorlover as cl
from dash_core_components import Graph, Dropdown, Input, Slider
import dash_html_components as html
import datetime as dt
import itertools
import json
import os
import pandas as pd
import pandas_datareader.data as web
import plotly
import traceback


server = Flask(__name__)
dash = Dash(__name__, server=server)
dash.component_suites = [
    'dash_html_components',
    'dash_core_components'
]

header = html.Div([
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
    )
])

# World Bank Example
colorscale = cl.scales['9']['qual']['Paired']
df = pd.read_csv('./WDI_Data_Filtered.csv', encoding='latin1')
indicators = {
    'World view': [
        'Population density (people per sq. km of land area)',
        'GNI per capita, PPP (current international $)'
    ],
    'People': [
        'Income share held by lowest 20%',
        'Life expectancy at birth, total (years)',
        'Fertility rate, total (births per woman)',
        'Gross enrollment ratio, primary, both sexes (%)',
        'Gross enrolment ratio, secondary, both sexes (%)',
        'Prevalence of HIV, total (% of population ages 15-49)'
    ],
    'Environment': [
        'Energy use (kg of oil equivalent per capita)',
        'CO2 emissions (metric tons per capita)',
        'Electric power consumption (kWh per capita)'
    ],
    'Economy': [
        'GDP growth (annual %)',
        'Inflation, GDP deflator (annual %)',
        'Agriculture, value added (% of GDP)',
        'Industry, value added (% of GDP)',
        'Services, etc., value added (% of GDP)',
        'Exports of goods and services (% of GDP)',
        'Imports of goods and services (% of GDP)',
        'Revenue, excluding grants (% of GDP)',
        'Net lending (+) / net borrowing (-) (% of GDP)'
    ],
    'States and market': [
        'Time required to start a business (days)',
        'Domestic credit provided by financial sector (% of GDP)',
        'Tax revenue (% of GDP)',
        'Military expenditure (% of GDP)',
        'Mobile cellular subscriptions (per 100 people)',
        'Internet users (per 100 people)',
        'High-technology exports (% of manufactured exports)'
    ]
}

options = []
for k, v in indicators.iteritems():
    options.append({'label': k, 'value': k, 'disabled': True})
    for i in v:
        options.append({'label': i, 'value': i})

world_bank_layout = html.Div([
    html.H1('World Bank Development Indicators'),

    html.Div('''
        This web application is written in Plotly's Dash framework.
        Dash is a Python abstraction around Javascript and HTML.
        Altogether, this app was written in 300 lines.
    '''),

    html.Hr(),

    html.Div([
        html.Div([Graph(id='choropleth')], className="eight columns"),
        html.Div(id='table',
                 style={'height': '400px', 'overflowY': 'scroll'},
                 className="four columns"),
    ], className="row"),
    html.Div([Slider(id='year-slider')], style={'margin': 25}),
    Dropdown(id='indicator-dropdown-single',
             options=options,
             value='GDP growth (annual %)'),

    html.Hr(),

    html.H3('Indicators over Time'),

    html.Div([
        html.Label('Indicator'),
        Dropdown(
            id='indicator-dropdown',
            options=options,
            multi=True,
            value=[
                'Exports of goods and services (% of GDP)',
                'Imports of goods and services (% of GDP)'
            ]
        ),

        html.Label('Region'),
        Dropdown(
            id='region-dropdown',
            options=[{'label': i, 'value': i}
                     for i in list(df['Country Name'].unique())],
            multi=True,
            value=['Kuwait', 'United States', 'United Kingdom']
        )
    ]),

    Graph(id='indicator-time-series'),

    html.Hr(),
])

@dash.react('indicator-time-series', ['indicator-dropdown', 'region-dropdown'])
def update_graph(indicator_dropdown, region_dropdown):
    indicators = indicator_dropdown['value']
    regions = region_dropdown['value']
    years = [str(i) for i in range(1960, 2017)]

    figure = plotly.tools.make_subplots(
        rows=len(indicators), cols=1, subplot_titles=indicators,
        shared_xaxes=True, vertical_spacing=0.03
    )
    figure['layout']['height'] = 300 * len(indicators)
    figure['layout']['margin'] = {'l': 20, 't': 40, 'r': 0, 'b': 0, 'pad': 0}
    figure['layout']['legend'] = {'x': 0, 'y': 1, 'bgcolor': 'rgba(255, 255, 255, 0.5)'}

    fdf = df[
        df['Indicator Name'].isin(indicators) &
        df['Country Name'].isin(regions)
    ]

    for indicator in indicators:
        df_indicator = fdf[(fdf['Indicator Name'] == indicator)]
        for region in regions:
            color = colorscale[regions.index(region) % len(colorscale)]
            try:
                row = df_indicator[
                        (df_indicator['Country Name'] == region)
                    ].ix[:, '1960':].irow(0).tolist()
            except:
                row = []
            trace = {
                'x': years,
                'y': row,
                'name': region,
                'legendgroup': region,
                'showlegend': True if indicators.index(indicator) == 0 else False,
                'marker': {'size': 10, 'color': color},
                'line': {'width': 3, 'color': color},
                'mode': 'lines+markers',
                'connectgaps': True
            }

            figure.append_trace(trace, indicators.index(indicator) + 1, 1)

    return {'figure': figure}
    fdf = df[df['Indicator Name'] == indicator]

@dash.react('year-slider', ['indicator-dropdown-single'])
def update_slider(indicator_dropdown):
    indicator = indicator_dropdown['value']
    fdf = df[df['Indicator Name'] == indicator]
    available_years = [
        year for year in range(1960, 2017)
        if not fdf[str(year)].isnull().values.all()
    ]

    return {
        'value': available_years[-1],
        'marks': {year: str(year) if (i%5 == 0 or len(available_years) < 10) else ''
                  for i, year in enumerate(available_years)},
        'step': None,
        'min': min(available_years),
        'max': max(available_years)
    }


@dash.react('choropleth', ['indicator-dropdown-single', 'year-slider'])
def update_choropleth(indicator_dropdown, year_slider):
    indicator = indicator_dropdown['value']
    year = str(year_slider['value'])
    fdf = df[df['Indicator Name'] == indicator]
    return {'figure': {
        'data': [{
            'type': 'choropleth',
            'locations': fdf['Country Name'],
            'z': fdf[year],
            'locationmode': 'country names',
            'colorscale': 'Viridis',
            'colorbar': {
                'x': 1,
                'len': 0.5,
                'outlinewidth': 0,
                'xpad': 0, 'ypad': 0,
                'thickness': 10
            }
        }],
        'layout': {
            'margin': {'l': 0, 'r': 0, 't': 0, 'b': 0, 'pad': 0},
            'geo': {'showframe': False},
            'width': '100%'
        }
    }}


@dash.react('table', ['indicator-dropdown-single', 'year-slider'])
def update_table(indicator_dropdown, year_slider):
    indicator = indicator_dropdown['value']
    year = str(year_slider['value'])
    fdf = df[df['Indicator Name'] == indicator]\
        .sort_values(year, ascending=False)
    countries = fdf['Country Name'].tolist()
    values = fdf[year].tolist()
    return {'content': html.Table(
        [html.Tr([html.Th('Country'), html.Th(indicator)])] +
        [html.Tr([
            html.Td(country), html.Td(str(value))
        ]) for country, value in zip(countries, values)]
    )}


# Stock Tickers Example
stock_ticker_layout = html.Div([
    html.H1('Yahoo Finance Stock Tickers', id='h1'),
    Input(
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
    Graph(
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


dash.layout = html.Div([
    header, world_bank_layout, stock_ticker_layout
])

if __name__ == '__main__':
    dash.server.run(debug=True)
