import json
from collections import deque
import plotly.express as px
from dash import dcc, html, Output, Input, State, callback, register_page
from data_loader import airport_db  # Import the global AirportDatabase object
from datetime import datetime

# Register Dash Page
register_page(__name__, path='/route-view')

# Load airport data
with open('airline_routes.json', 'r') as file:
    airports = json.load(file)

# Generate dropdown options from airport database
airport_options = [
    {'label': f"{airport['name']} ({iata})", 'value': iata}
    for iata, airport in airports.items()
]

# Define filter options
extra_options = [
    {'label': "Price (Cheapest)", 'value': "price_cheapest"},
    {'label': "Shortest Path", 'value': "shortest_path"},
]

# Available map projections for the dropdown
map_projections = [
    {"label": "Natural Earth", "value": "natural earth"},
    {"label": "Equirectangular", "value": "equirectangular"},
    {"label": "Orthographic", "value": "orthographic"},
    {"label": "Mercator", "value": "mercator"},
    {"label": "Azimuthal Equal Area", "value": "azimuthal equal area"},
    {"label": "Robinson", "value": "robinson"}
]

# Layout
layout = html.Div(className="min-h-screen flex flex-col md:gap-3 p-4 ", children=[

    # Title
    html.H2("Flight Path Visualization", className="text-2xl sm:text-4xl font-bold text-white text-start mb-3"),

    # Form Section (Responsive Grid)
    html.Div(className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 bg-white p-4 sm:p-6 rounded-lg", children=[

        # Departure Airport Selection
        html.Div(children=[
            html.Label("Select Departure Airport:", className="font-bold text-gray-700"),
            dcc.Dropdown(id='departure-airport-dropdown', options=airport_options, placeholder="Select a departure airport",
                className="bg-white border rounded-md shadow-sm focus:ring focus:ring-blue-200")
        ]),

        # Arrival Airport Selection
        html.Div(children=[
            html.Label("Select Arrival Airport:", className="font-bold text-gray-700"),
            dcc.Dropdown(id='arrival-airport-dropdown', options=airport_options, placeholder="Select an arrival airport",
                className="bg-white border rounded-md shadow-sm focus:ring focus:ring-blue-200")
        ]),

        # Date Pickers (Responsive Stack)
        html.Div(className="grid grid-cols-2 gap-3 ", children=[

            # Departure Date Picker
            html.Div(className="md:flex-1 flex-none", children=[
                html.Label("Departure Date:", className="font-bold text-gray-700"),
                dcc.DatePickerSingle(
                    display_format="DD/MM/YYYY",
                    id='departure-date-picker',
                    placeholder="Select date",
                    clearable=True,
                    className="border rounded-md shadow-sm bg-white focus:ring focus:ring-blue-900 w-max"
                )
            ]),

            # Return Date Picker
            html.Div(className="md:flex-1 flex-none", children=[
                html.Label("Return Date:", className="font-bold text-gray-700"),
                dcc.DatePickerSingle(
                    display_format="DD/MM/YYYY",
                    id='return-date-picker',
                    placeholder="Select date",
                    clearable=True,
                    className="border rounded-md shadow-sm bg-white focus:ring focus:ring-blue-900 w-max"
                )
            ]),
        ]),

        # Filter Options
        html.Div(children=[
            html.Label("Filter by:", className="font-bold text-gray-700"),
            dcc.Dropdown(id='filter-dropdown', options=extra_options, placeholder="Filter by",
                className="bg-white border rounded-md shadow-sm focus:ring focus:ring-blue-200")
        ]),

        # Map Projection Selection
        html.Div(children=[
            html.Label("Select Map View:", className="font-bold text-gray-700"),
            dcc.Dropdown(id='map-projection-dropdown', options=map_projections, 
                value="natural earth", clearable=False, placeholder="Select Map Projection",
                className="bg-white border rounded-md shadow-sm focus:ring focus:ring-blue-200")
        ]),

        # Search Button (Full-Width on Small Screens)
        html.Div(className="flex flex-1 justify-center sm:justify-start", children=[
            html.Button("Search Route", id="search-button",
                        className="bg-blue-600 text-white font-bold px-4 py-2 rounded-lg mt-4 w-full sm:w-auto hover:bg-blue-700 transition"),
        ]),
    ]),

    # Route Information Section
    html.Div(id='route-info', className="bg-white p-5 rounded-lg mt-4 shadow-md"),

    # Full-Width Map Visualization
    html.Div(className="w-full bg-white rounded-lg overflow-hidden mt-4", children=[
        dcc.Graph(id='route-map', className="w-full h-full", config={'scrollZoom': True, 'displayModeBar': False})
    ])
])

# BFS Algorithm to find minimum layovers
def bfs_min_connections(airports, start, goal):
    queue = deque([(start, [start])])
    visited = set()

    while queue:
        current, path = queue.popleft()

        if current == goal:
            return path

        visited.add(current)

        for route in airports[current].get('routes', []):
            neighbor = route['iata']
            if neighbor in airports and neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    return None

# Callback to compute the route
@callback(
    [Output('route-info', 'children'),
     Output('route-map', 'figure')],
    [Input('search-button', 'n_clicks')],
    [State('departure-airport-dropdown', 'value'),
     State('arrival-airport-dropdown', 'value'),
     State('departure-date-picker', 'date'),  
     State('return-date-picker', 'date'),  
     State('filter-dropdown', 'value'),
     State('map-projection-dropdown', 'value')]  
)
def update_route_map(n_clicks, departure_iata, arrival_iata, depart_date, return_date, filter_option, projection_type):

    if not n_clicks:
        return "⚠️ Please select both departure and destination airports.", px.scatter_geo(projection=projection_type)

    if not departure_iata or not arrival_iata:
        return "⚠️ Please select both departure and destination airports.", px.scatter_geo(projection=projection_type)

    dep_airport = airport_db.get_airport(departure_iata)
    arr_airport = airport_db.get_airport(arrival_iata)

    if not dep_airport or not arr_airport:
        return "Invalid airport selection", px.scatter_geo(projection=projection_type)

    # Flight Route Visualization
    route_fig = px.line_geo(
        lat=[dep_airport.latitude, arr_airport.latitude],
        lon=[dep_airport.longitude, arr_airport.longitude],
        text=[dep_airport.name, arr_airport.name],
        projection=projection_type
    )

    route_fig.update_traces(
        line=dict(dash="dash", width=2, color="blue"),
        mode="lines+markers+text",
        marker=dict(size=10, color=["red", "green"]),
        textposition="top center"
    )

    route_fig.update_layout(
        geo=dict(showland=True),
        title=f"Flight Route from {dep_airport.name} to {arr_airport.name}"
    )

    return html.Div(f"✅ Route Found: {dep_airport.name} → {arr_airport.name}"), route_fig