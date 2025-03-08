import dash
from dash import html, dcc, page_container

external_stylesheets = ["https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, use_pages=True)

app.layout = html.Div(className="container", children=[
    html.H1("Flight Map Routing System", className="text-4xl font-bold text-red-500"),
    
    html.Div(className="section", children=[
        dcc.Link('🌍 Map View', href='/map-view', style={'margin-right': '20px'}),
        dcc.Link('📊 Table View', href='/table-view')
    ]),

    html.Hr(),

    page_container
])

if __name__ == '__main__':
    app.run_server(debug=True)
