import dash
from dash import html, dcc, page_container

# Initialize the multi-page Dash app
app = dash.Dash(__name__, use_pages=True)

app.layout = html.Div([
    html.H1("Flight Map Routing System"),
    dcc.Link('Map View | ', href='/map-view'),
    dcc.Link('Table View', href='/table-view'),
    html.Hr(),
    page_container  # This renders the content from the selected page
])

if __name__ == '__main__':
    app.run_server(debug=False)
