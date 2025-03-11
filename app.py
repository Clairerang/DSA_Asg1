import dash
from dash import html, dcc, page_container, callback, Input, Output

# Tailwind CSS for styling
external_stylesheets = ["https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css"]

# Initialize Dash app with pages enabled
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, use_pages=True)

# Layout with sidebar
app.layout = html.Div(className="flex min-h-screen", children=[
    
    # Sidebar Panel
    html.Div(className="w-64 text-white px-0 p-3", children=[
        html.H2("Flight Routing System", className="text-xl mx-3 font-bold text-start text-white "),
        html.Hr(className="mx-0"),
        html.Div(id="sidebar-links", className="flex flex-col gap-2"),
    ]),

    # Main Content Area
    html.Div(className="flex-1 px-5", children=[ 
        # Page Container for Routing
        page_container
    ])
])

# Callback to update active route styling
@app.callback(
    Output("sidebar-links", "children"),
    Input("url", "pathname")  # Track URL changes
)
def update_active_link(pathname):
    # Define links with conditional classes
    return [
        dcc.Link(
            "Route View", href="/route-view",
            className=f"block py-3 px-2 mx-2 rounded-md {'accent-blue text-white' if pathname == '/route-view' else 'hover:bg-gray-100 hover:text-black transition-colors duration-300'}"
        ),
        # dcc.Link(
        #     "Map View", href="/map-view",
        #     className=f"block py-3 px-2 mx-2 rounded-md {'accent-blue text-white' if pathname == '/map-view' else 'hover:bg-gray-100 hover:text-black transition-colors duration-300'}"
        # ),
        dcc.Link(
            "Table View", href="/table-view",
            className=f"block py-3 px-2 mx-2 rounded-md {'accent-blue text-white' if pathname == '/table-view' else 'hover:bg-gray-100 hover:text-black transition-colors duration-300'}"
        ),
    ]

# Add location component for tracking current page
app.layout.children.insert(0, dcc.Location(id="url", refresh=False))

if __name__ == '__main__':
    app.run_server(debug=True)