import json
from collections import deque
import plotly.express as px
from dash import dcc, html, Output, Input, callback, register_page
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
layout = html.Div(className="min-h-screen gap-3 flex flex-col", children=[
    
    # Title
    html.H2("Flight Path Visualization", className="text-4xl font-bold text-white my-3"),

    # Form Section
    html.Div(className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 bg-white p-6 rounded-lg ", children=[
        
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

        html.Div(className="flex flex-1 w-max space-x-4", children=[
        
        # Departure Date Picker
        html.Div(children=[
            html.Label("Departure Date:", className="font-bold text-gray-700"),
            dcc.DatePickerSingle(
                display_format="DD/MM/YYYY",
                id='departure-date-picker',
                placeholder="Select date",
                clearable=True,
                className="border rounded-md shadow-sm bg-white focus:ring focus:ring-blue-200"
            )
        ]),

        # Return Date Picker
        html.Div(children=[
            html.Label("Return Date:", className="font-bold text-gray-700"),
            dcc.DatePickerSingle(
                display_format="DD/MM/YYYY",
                id='return-date-picker',
                placeholder="Select date",
                clearable=True,
                className="border rounded-md shadow-sm bg-white focus:ring focus:ring-blue-200"
            )
        ]),

        # html.Div(children=[
        #     html.Label("Trip Type:", className="font-bold text-gray-700"),
        #     dcc.Checklist(
        #         id='one-way-toggle',
        #         options=[{'label': 'One-Way Flight', 'value': 'one_way'}],
        #         value=[],
        #         className="text-gray-900 font-medium mt-2"
        #     )
        # ]),
    ]),


        # Filter options
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
    ]),

    # Route Validation Message
    # html.Div(id='route-validation', className="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4 rounded-md my-4"),

    # Combined Route Information
    html.Div(id='route-info', className="bg-white p-5 rounded-lg "),

    # Full-Width Map Visualization
    html.Div(className="w-full h-screen bg-white rounded-lg  overflow-hidden", children=[
        dcc.Graph(id='route-map', className="w-full h-full", 
            config={'scrollZoom': True, 'displayModeBar': False})
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
    [Input('departure-airport-dropdown', 'value'),
     Input('arrival-airport-dropdown', 'value'),
     Input('departure-date-picker', 'date'),  
     Input('return-date-picker', 'date'),  
     Input('filter-dropdown', 'value'),
     Input('map-projection-dropdown', 'value')]  
)
def update_route_map(departure_iata, arrival_iata, depart_date, return_date, filter_option, projection_type):
    if not departure_iata or not arrival_iata:
        return "⚠️ Please select both departure and destination airports.", px.scatter_geo(projection=projection_type)

    dep_airport = airport_db.get_airport(departure_iata)
    arr_airport = airport_db.get_airport(arrival_iata)

    if not dep_airport or not arr_airport:
        return "Invalid airport selection", px.scatter_geo(projection=projection_type)
    
    # Format the dates (convert from string)
    def format_date(date_str):
        if date_str:
            return datetime.strptime(date_str, "%Y-%m-%d").strftime("%B %d, %Y")  # E.g., "March 11, 2025"
        return "Not Selected"

    formatted_depart_date = format_date(depart_date)
    formatted_return_date = format_date(return_date) if return_date else ""

    # ✅ Date validation: Ensure departure date is not after the return date
    if formatted_depart_date and formatted_return_date and formatted_depart_date > formatted_return_date:
        return html.Div([
            html.H3("❌ Date Error", className="text-lg font-bold text-red-600"),
            html.P("⚠️ The departure date cannot be later than the return date.", className="text-gray-700")
        ], className="p-4 bg-red-100 border-l-4 border-red-500 rounded-md"), px.scatter_geo(projection=projection_type)

    # Find shortest path using BFS
    if filter_option == "shortest_path":
        route = bfs_min_connections(airports, departure_iata, arrival_iata)
    else:
        # If no filter or cheapest price selected, find direct shortest route
        route = [departure_iata, arrival_iata] if any(r['iata'] == arrival_iata for r in airports[departure_iata]['routes']) else None

    if not route:
        return f"❌ No route available from {dep_airport.name} to {arr_airport.name}.", px.scatter_geo(projection=projection_type)

    # Calculate total distance and stops
    total_distance = 0
    route_details = []

    for i in range(len(route) - 1):
        segment_start, segment_end = route[i], route[i + 1]
        route_info = next((r for r in airports[segment_start]['routes'] if r['iata'] == segment_end), None)

        if route_info:
            carrier_names = ', '.join(carrier['name'] for carrier in route_info.get('carriers', [])) or "Unknown Airline"
            distance = route_info['km']
            total_distance += distance
            route_details.append(html.P(f"✈️ {segment_start} → {segment_end} | {distance} km | Airline(s): {carrier_names}", className="text-gray-700"))

    # Calculate estimated price (Assume $0.10 per km)
    estimated_price = round(total_distance * 0.10, 2)

    # Combined Route Information
    route_info_content = html.Div([
        html.H3("✅ Route Found", className="text-lg font-bold text-green-600"),
        html.P(f"📍 Total Distance: {total_distance} km", className="font-semibold"),
        html.P(f"✈️ Number of Layovers: {len(route) - 1}", className="font-semibold"),
        html.P(f"💰 Estimated Price: ${estimated_price}", className="font-semibold"),
        html.H4("🛫 Flight Route Details", className="font-bold mt-4"),
        *route_details
    ], className=" p-2 rounded-md my-3 ")

    # Map visualization with selected projection
    route_fig = px.line_geo(
        lat=[dep_airport.latitude] + [airports[i]['latitude'] for i in route[1:-1]] + [arr_airport.latitude],
        lon=[dep_airport.longitude] + [airports[i]['longitude'] for i in route[1:-1]] + [arr_airport.longitude],
        text=[dep_airport.name] + [airports[i]['name'] for i in route[1:-1]] + [arr_airport.name],
        projection=projection_type  # Dynamic projection type
    )

    # Customize map style
    route_fig.update_traces(
        line=dict(dash="dash", width=2, color="blue"),
        mode="lines+markers+text",
        marker=dict(size=10, color=["red"] + ["blue"] * (len(route) - 2) + ["green"]),
        textposition="top center"
    )

    route_fig.update_layout(
        dragmode="pan",
        geo=dict(showland=True),
        title=f"Flight Route from {dep_airport.name} to {arr_airport.name} on {formatted_depart_date} to {formatted_return_date}"
    )

    return route_info_content, route_fig