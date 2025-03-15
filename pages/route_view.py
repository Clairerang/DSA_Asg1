from datetime import datetime, date, timedelta
import plotly.express as px
from dash import dcc, html, Output, Input, callback, register_page, State
from data_loader import airport_db  # Import the global AirportDatabase object
from algorithms import bfs_min_connections, yen_k_shortest_paths, astar_preferred_airline
from cal_price import get_price_for_route
import dash_bootstrap_components as dbc
import dash

todayDate = date.today() # For date selection

# Register Dash Page
register_page(__name__, path='/route-view')

# Generate dropdown options from airport database
airport_options = [
    {'label': f"{airport.name} ({airport.iata})", 'value': airport.iata}
    for airport in sorted(airport_db.airports.values(), key=lambda a: a.iata)
]

# Define filter options
filter_options = [
    {'label': "Price (Cheapest)", 'value': "shortest_path"},
    {'label': "Least Layovers", 'value': "least_layovers"},
    {'label': "Search Airline", 'value': "search_airline"},
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
layout = html.Div(className="min-h-screen gap-3 p-2 flex flex-col", children=[

    # Title
    html.H2("Hi, where would you like to go?", className="text-2xl font-bold text-white my-3"),

    # Form Section
    html.Div(className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 pb-9 pt-8 px-8 bg-white rounded-lg ", children=[
        
        # Departure Airport Selection
        html.Div(children=[
            html.Label("Select Departure Airport:", className="font-bold text-gray-700 mt-0"),
            dcc.Dropdown(id='departure-airport-dropdown', options=airport_options, placeholder="Select a departure airport",
                className="bg-white border rounded-md shadow-sm focus:ring focus:ring-blue-200")
        ]),

        # Arrival Airport Selection
        html.Div(children=[
            html.Label("Select Arrival Airport:", className="font-bold text-gray-700 mt-0"),
            dcc.Dropdown(id='arrival-airport-dropdown', options=airport_options, placeholder="Select an arrival airport",
                className="bg-white border rounded-md shadow-sm focus:ring focus:ring-blue-200")
        ]),

        html.Div(className="flex flex-1 w-max space-x-4", children=[
        
        # Departure Date Picker
        html.Div(children=[
            html.Label("Departure Date:", className="font-bold text-gray-700 mt-0"),
            dcc.DatePickerSingle(
                display_format="DD/MM/YYYY",
                id='departure-date-picker',
                placeholder="Select date",
                clearable=True,
                #min_date_allowed=todayDate,
                className="border rounded-md shadow-sm bg-white focus:ring focus:ring-blue-200"
            )
        ]),

        # Return Date Picker
        html.Div(children=[
            html.Label("Return Date:", className="font-bold text-gray-700 mt-0"),
            dcc.DatePickerSingle(
                display_format="DD/MM/YYYY",
                id='return-date-picker',
                placeholder="Select date",
                clearable=True,
                #min_date_allowed=todayDate,
                className="border rounded-md shadow-sm bg-white focus:ring focus:ring-blue-200"
            )
        ]),

    ]), 

        # Filter options
        html.Div(children=[
            html.Label("Filter by:", className="font-bold text-gray-700"),
            dcc.Dropdown(id='filter-dropdown', options=filter_options, placeholder="Filter by", value="shortest_path",
                className="bg-white border rounded-md shadow-sm focus:ring focus:ring-blue-200")
        ]),

        # Airline Multi-Select Dropdown (Dynamic Options)
        html.Div(
            id="airline-dropdown-container",
            style={"display": "none"},
                children=[
                    html.Label("Select Preferred Airlines:"),
                    dcc.Dropdown(
                        id='airline-dropdown',
                        multi=True,  # Allows multiple selections
                        placeholder="Select available airlines",
                        className="bg-white border rounded-md shadow-sm focus:ring focus:ring-blue-200"
                    ),
                ]
        ),
        

        # Map Projection Selection
        html.Div(children=[
            html.Label("Select Map View:", className="font-bold text-gray-700"),
            dcc.Dropdown(id='map-projection-dropdown', options=map_projections, 
                value="natural earth", clearable=False, placeholder="Select Map Projection",
                className="bg-white border rounded-md shadow-sm focus:ring focus:ring-blue-200")
        ]),
    ]),

    # Combined Route Information
    html.Div(id='route-info', className="bg-white p-4 rounded-lg ", children=[
        html.Div(id='route-info-content', className="mt-4"),
    ]),

    # Full-Width Map Visualization
    html.Div(className="w-full md:h-screen h-full bg-white rounded-lg  overflow-hidden", children=[
        dcc.Graph(id='route-map', className="w-full h-full whiteline-pre", 
            config={'scrollZoom': True, 'displayModeBar': False})
    ]),
])

# Callback to compute the route
@callback(
    [Output('route-info', 'children'),
     Output('route-map', 'figure')],
    [Input('departure-airport-dropdown', 'value'),
     Input('arrival-airport-dropdown', 'value'),
     Input('departure-date-picker', 'date'),  
     Input('return-date-picker', 'date'),  
     Input('filter-dropdown', 'value'),
     Input('map-projection-dropdown', 'value'),
     Input('airline-dropdown', 'value'),]  
)
def update_route_map(departure_iata, arrival_iata, depart_date, return_date, filter_option, projection_type, airline_type):
    if not departure_iata or not arrival_iata:
        return "⚠️ Please select both departure and destination airports.", px.scatter_geo(projection=projection_type)

    dep_airport = airport_db.get_airport(departure_iata)
    arr_airport = airport_db.get_airport(arrival_iata)

    if not dep_airport or not arr_airport:
        return "Invalid airport selection", px.scatter_geo(projection=projection_type)
    
    def toDateTime(date_str):
        if date_str:
            return datetime.strptime(date_str, "%Y-%m-%d")
        return None
    
    # Format the dates (convert from string)
    def format_date(date):
        if date:
            return date.strftime("%d %B %Y") 
        return "Not Selected"

    formatted_depart_date = format_date(toDateTime(depart_date))
    formatted_return_date = format_date(toDateTime(return_date)) if return_date else "One-way trip"

    # ✅ Date validation: Ensure departure date is not after the return date
    if toDateTime(depart_date) and toDateTime(return_date) and toDateTime(depart_date) > toDateTime(return_date):
        return html.Div([
            html.H3("❌ Date Error", className="text-lg font-bold text-red-600"),
            html.P("⚠️ The departure date cannot be later than the return date.", className="text-gray-700")
        ], className="p-4 bg-red-100 border-l-4 border-red-500 rounded-md"), px.scatter_geo(projection=projection_type)

    route = None
    # Find shortest path using BFS
    if filter_option == "least_layovers":
        route = bfs_min_connections(departure_iata, arrival_iata)
    elif filter_option == "shortest_path":
        route = yen_k_shortest_paths(departure_iata, arrival_iata)
        if route:
            route = route[0]
    elif filter_option == "search_airline":
        if airline_type:
            route = astar_preferred_airline(departure_iata, arrival_iata, airline_type)
            if route:
                route = route[0]
    # else:
    #     # If no filter or cheapest price selected, find direct shortest route
    #     departure_airport = airport_db.get_airport(departure_iata)
    #     if departure_airport and any(route.iata == arrival_iata for route in departure_airport.routes):
    #         route = [departure_iata, arrival_iata]  # Direct flight exists
    #     else:
    #         route = None  # No direct route available

    if not route:
        return f"❌ No route available from {dep_airport.name} to {arr_airport.name}.", px.scatter_geo(projection=projection_type)

    def filter_routes_by_date(route, selected_depart_date, selected_return_date):

        if not selected_depart_date and not selected_return_date:
            return route.carriers  # Return all carriers in this route
        
        available_carriers = []
        
        for carrier in route.carriers:
            if carrier.departure_date == selected_depart_date:
                if selected_return_date is None or carrier.arrival_date == selected_return_date:
                    available_carriers.append(carrier)

        return available_carriers

    def calculate_route_details(route, airport_db):
        total_distance = 0
        total_est_price = 0
        route_details = []
        filtered_route = []

        for i in range(len(route) - 1):
            segment_start_iata, segment_end_iata = route[i], route[i + 1]

            # Fetch Airport objects
            segment_start_airport = airport_db.get_airport(segment_start_iata)
            segment_end_airport = airport_db.get_airport(segment_end_iata)

            if not segment_start_airport or not segment_end_airport:
                continue  # Skip invalid airports

            # Find the route from segment_start to segment_end
            route_info = next((r for r in segment_start_airport.routes if r.iata == segment_end_iata), None)

            if route_info:
                available_carriers = filter_routes_by_date(route_info, depart_date, return_date)

                if not available_carriers:
                    continue  # Skip routes with no available flights on selected date

                # Get airline names & Seats Left
                carrier_names = " | ".join( f"{carrier.name}: {carrier.seats_remaining} seats left" for carrier in available_carriers ) if available_carriers else "Unknown Airline"
                
                distance = route_info.km
                total_distance += distance

                price = get_price_for_route(segment_start_airport, segment_end_airport)
                total_est_price += price

                route_details.append(html.Div(className="p-3 border-b border-gray-300", children=[
                html.H4(f"✈️ {segment_start_airport.name} ({segment_start_iata}) → {segment_end_airport.name} ({segment_end_iata})",
                        className="font-semibold text-lg"),
                
                html.Div(className="flex flex-wrap justify-between text-sm text-gray-700", children=[
                    html.Div(children=[
                        html.P(f"Distance: {distance} km"),
                        html.P(f"Estimated Price: ${price:.2f}")
                    ]),
                    html.Div(children=[
                        html.P(f"🛫 Departure: {segment_start_airport.name}"),
                        html.P(f"🛬 Arrival: {segment_end_airport.name}")
                    ])
                ]),

                html.P(f"Airline(s): {carrier_names}", className="text-sm text-gray-600"),
            ]))

            filtered_route.append(route[i])
        
        filtered_route.append(route[-1])

        return total_distance, route_details, total_est_price, filtered_route

    total_distance, route_details, estimated_price, filtered_route = calculate_route_details(route,airport_db)
    
    if not route_details:
        return f"❌ No route available from {dep_airport.name} to {arr_airport.name} on {formatted_depart_date} to {formatted_return_date}.", px.scatter_geo(projection=projection_type)

    # layovers = len(route) - 1 if len(route_details) == len(route) - 1 else len(route_details)
    route_info_content = html.Div([

    html.Div(children=[
        html.Div(className="flex items-center justify-between", children=[
            html.Div(children=[
                html.H3("Sky Wings", className="text-lg font-bold"),
                html.P(f"Flight {filtered_route[0]} → {filtered_route[-1]}", className="text-gray-600"),
            ]),
            html.Div(children=[
                html.P(f"${estimated_price:.2f}", className="text-xl font-bold text-green-600"),
                html.P("per person", className="text-sm text-gray-500")
            ])
        ]),

        html.Div(className="border-t my-3 border-gray-300"),  # Horizontal line
        
        html.Div(className="flex justify-between text-sm text-gray-700", children=[
            html.Div(children=[
                html.P("🛫 Departure:", className="font-semibold"),
                html.P(f"{dep_airport.name} ({dep_airport.iata})"),
                html.P(f"{formatted_depart_date}"),
                # html.P(f"Time: {depart_date[-5:]}")
            ]),
            html.Div(children=[
                html.P("🛬 Arrival:", className="font-semibold"),
                html.P(f"{arr_airport.name} ({arr_airport.iata})"),
                html.P(f"{formatted_return_date}"),
                # html.P(f"Time: {return_date[-5:] if return_date else 'N/A'}")
            ])
        ]),

        html.Div(className="mt-2 text-gray-700", children=[
            html.P(f"🕒 Number of stop(s): {len(route) - 1} ", className="font-semibold"),
            html.P(f"📍 Total Distance: {total_distance} km"),
        ]),

        # html.Div(className="mt-3 text-sm text-gray-500", children=[
        #     html.P(f"Only {8} seats left at this price!", className="text-red-600"),
        # ]),
        dbc.Accordion([dbc.AccordionItem([*route_details], title="Route Details")]),
        
        ]
    ),
        
    ], className="rounded-lg p-3")

    # Map visualization with selected projection
    route_fig = px.line_geo(
        lat=[dep_airport.latitude] + [airport_db.get_airport(i).latitude for i in route[1:-1]] + [arr_airport.latitude],
        lon=[dep_airport.longitude] + [airport_db.get_airport(i).longitude for i in route[1:-1]] + [arr_airport.longitude],
        text=[dep_airport.name] + [airport_db.get_airport(i).name for i in route[1:-1]] + [arr_airport.name],
        projection=projection_type  # Dynamic projection type
    )

    # Customize map style
    route_fig.update_traces(
        line=dict(dash="dash", width=2, color="blue"),
        mode="lines+markers+text",
        marker=dict(size=10, color=["red"] + ["blue"] * (len(route) - 2) + ["green"]),
        textposition="top center"
    )
    
    def get_route_title(formatted_depart_date, formatted_return_date):
        if formatted_return_date in ["One-way trip", "Not Selected"]:
            route_title = f"Flight Route from {dep_airport.name} to {arr_airport.name} on a one-way trip"
        else:
            route_title = f"Flight Route from {dep_airport.name} to {arr_airport.name} on {formatted_depart_date} to {formatted_return_date}"
        return route_title

    route_fig.update_layout(
        dragmode="pan",
        geo=dict(showland=True),
        title= get_route_title(formatted_depart_date, formatted_return_date),
    )

    return route_info_content, route_fig


@callback(
    [Output('airline-dropdown', 'options'),
     Output('airline-dropdown-container', 'style')],
    [Input('departure-airport-dropdown', 'value'),
     Input('arrival-airport-dropdown', 'value'),
     Input('filter-dropdown', 'value')]
)
def update_airline_options(departure_iata, arrival_iata, filter_options):
    """Generates airline options based on selected departure & arrival airports and shows/hides the dropdown."""
    if filter_options != "search_airline":
        return [], {"display": "none"}
    
    if not departure_iata or not arrival_iata:
        return [], {"display": "none"}  # Keep hidden if not both selected

    departure_airport = airport_db.get_airport(departure_iata)
    if not departure_airport:
        return [], {"display": "none"}


    unique_carrier = get_unique_carrier()
    # Convert to dropdown options
    airline_options = [{'label': f"{unique_carrier[iata]} ({iata})", 'value': iata} for iata in unique_carrier.keys()]

    # Show dropdown only if airlines are found
    style = {"display": "block"} if airline_options else {"display": "none"}
    
    return airline_options, style

def get_unique_carrier():
    unique_carrier = {}  # Dictionary to store unique IATA -> Name mapping

    for airport in airport_db.airports.values():
        for route in airport.routes:
            for carrier in route.carriers:
                unique_carrier[carrier.iata] = carrier.name  # Store IATA -> Name mapping
    return unique_carrier 