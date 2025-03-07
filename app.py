import dash
from dash import html, dcc, page_container

app = dash.Dash(__name__, use_pages=True)

app.layout = html.Div(className="container", children=[
    html.H1("Flight Map Routing System"),
    
    html.Div(className="section", children=[
        dcc.Link('🌍 Map View', href='/map-view', style={'margin-right': '20px'}),
        dcc.Link('📊 Table View', href='/table-view')
    ]),

    html.Hr(),

    page_container
])

if __name__ == '__main__':
    app.run_server(debug=True)
