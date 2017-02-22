import dash
import dash_html_components as dhc
import dash_core_components as dcc
import plotly.plotly as py
import pandas as pd
df = pd.read_csv('http://bit.ly/2mcrq5b')
fig = py.get_figure("https://plot.ly/~jackp/17498/")

app = dash.react.Dash('Dash for Drug Discovery')

text_style = dict( fontFamily='sans-serif', fontWeight=300, color='#444' )
td_style = dict( border='1px solid #888', width='25%', verticalAlign='middle', height=100 )

app.layout = dhc.Div([
        dhc.H2('Dash for Drug Discovery', style=text_style),
        dhc.Table([
            [ dhc.Tr([dhc.Th('Structure', style={}),
                      dhc.Th('Name', style={}),
                      dhc.Th('Description', style={}),
                      dhc.Th('Molecular Weight', style={})])] +
            [ dhc.Td( [dhc.Img( src="https://www.drugbank.ca/structures/DB01000/thumb.svg" , id='img1' )], style=td_style ) ] +
            [ dhc.Td( 'Cyclacillin', id='p1', style=td_style ) ] +
            [ dhc.Td( 'A cyclohexylamido analog of penicillanic acid....', id='p2', style=td_style ) ] +
            [ dhc.Td( '341.4260', id='p3', style=td_style ) ],
            style = dict( width='100%', fontFamily='sans-serif', fontWeight=300, color='#444' ),
        ]),
        dcc.Graph(id='plot1', figure=fig),
    ])

@app.react('img1', events=[{'id': 'plot1', 'event': 'click'},], state=[{'id': 'plot1', 'prop': 'clickData'}])
def update_molecule_image( clickData ):
    pn = clickData['points'][0]['pointNumber']
    molecule_name = str(fig['data'][0]['text'][pn]).strip()
    DB_ID = df.loc[df['NAME'] == molecule_name]['PAGE'].to_string().split('/')[-1]
    src_tag = 'https://www.drugbank.ca/structures/' + DB_ID + '/thumb.svg'
    return {'src': src_tag}

app.component_suites = [
    'dash_html_components',
    'dash_core_components'
]

if __name__ == '__main__':
    app.server.run()
