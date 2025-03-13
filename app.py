#!.\.venv\Scripts\python.exe

import dash
from dash import html, dcc, page_container, Input, Output
import dash_bootstrap_components as dbc

# Tailwind CSS for styling
external_stylesheets = ["https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css", dbc.themes.BOOTSTRAP]

# Initialize Dash app with pages enabled
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, use_pages=True)

# Layout with sidebar
app.layout = html.Div(className="flex min-h-screen", children=[
    
    # Sidebar Panel
    html.Div(className="w-64 text-white px-0 p-3 md:flex flex-col hidden", children=[
        html.H2("Sky Wings", className="text-xl mx-3 font-bold text-start text-white "),
        html.Hr(className="mx-0"),
        html.Div(id="sidebar-links", className="flex flex-col gap-2"),
    ]),

    # Main Content Area
    html.Div(className="flex-1 md:px-5", children=[ 
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
            className=f"block py-3 px-2 mx-2 text-white no-underline rounded-md {'accent-blue text-white' if pathname == '/route-view' else 'hover:bg-gray-50 no-underline hover:text-dark transition-colors duration-300'}"
        ),
        # dcc.Link(
        #     "Map View", href="/map-view",
        #     className=f"block py-3 px-2 mx-2 rounded-md {'accent-blue text-white' if pathname == '/map-view' else 'hover:bg-gray-100 hover:text-black transition-colors duration-300'}"
        # ),
        dcc.Link(
            "Table View", href="/table-view",
            className=f"block py-3 px-2 mx-2 text-white no-underline rounded-md {'accent-blue text-white' if pathname == '/table-view' else 'hover:bg-gray-50 no-underline hover:text-dark transition-colors duration-300'}"
        ),
    ]

# Add location component for tracking current page
app.layout.children.insert(0, dcc.Location(id="url", refresh=False))

if __name__ == '__main__':
    print(f"🚀 Server is now running at http://127.0.0.1:8050/route-view")
    app.run_server(debug=True)