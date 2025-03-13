from datetime import datetime, date, timedelta
import plotly.express as px
from dash import dcc, html, Output, Input, callback, register_page
from data_loader import airport_db  # Import the global AirportDatabase object
from algorithms import bfs_min_connections, yen_k_shortest_paths
from cal_price import get_price_for_route

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
    html.H2("Flight Path Visualization", className="text-2xl font-bold text-white my-3"),

    # Form Section
    html.Div(className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 p-2 gap-4 bg-white p-6 rounded-lg ", children=[
        
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
                #min_date_allowed=todayDate,
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
                #min_date_allowed=todayDate,
                className="border rounded-md shadow-sm bg-white focus:ring focus:ring-blue-200"
            )
        ]),

    ]),
        # html.Div(children=[
        #      # Search Button
        #     html.Button("Search Route", id="search-button", className="bg-blue-600 text-white font-bold px-4 py-2 rounded-lg mt-4 hover:bg-blue-700 transition"),
        # ],className="flex fl"),

        # Filter options
        html.Div(children=[
            html.Label("Filter by:", className="font-bold text-gray-700"),
            dcc.Dropdown(id='filter-dropdown', options=filter_options, placeholder="Filter by", value="shortest_path",
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
     Input('map-projection-dropdown', 'value')]  
)
def update_route_map(departure_iata, arrival_iata, depart_date, return_date, filter_option, projection_type):
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

    # Find shortest path using BFS
    if filter_option == "least_layovers":
        route = bfs_min_connections(departure_iata, arrival_iata)
    elif filter_option == "shortest_path":
        route = yen_k_shortest_paths(departure_iata, arrival_iata)
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
        """
        Filters the available routes based on departure date.
        
        Args:
            route (Route): The route object containing carriers.
            selected_depart_date (str): The selected departure date (YYYY-MM-DD).
            selected_return_date (str): The selected return date (YYYY-MM-DD) or None.

        Returns:
            list: A filtered list of available carriers for the selected date.
        """

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
                
                # Get airline names
                carrier_names = ', '.join(f"{carrier.name} | Seat(s): {carrier.seats_remaining}" for carrier in available_carriers) or "Unknown Airline"
                
                distance = route_info.km
                total_distance += distance

                price = get_price_for_route(segment_start_airport, segment_end_airport)
                total_est_price += price

                route_details.append(html.P(
                    f"✈️ {segment_start_airport.name} ({segment_start_iata}) → {segment_end_airport.name} ({segment_end_iata}) | "
                    f"{distance} km | Airline(s): {carrier_names}",
                    className="text-gray-700"
                ))

                filtered_route.append(route[i])

        return total_distance, route_details, total_est_price, filtered_route

    total_distance, route_details, estimated_price, filtered_route = calculate_route_details(route,airport_db)
    
    if not route_details:
        return f"❌ No route available from {dep_airport.name} to {arr_airport.name} on {formatted_depart_date} to {formatted_return_date}.", px.scatter_geo(projection=projection_type)

    
    route_status = "✅ Route Found" if len(route_details) == len(route) - 1 else "⚠️ Partial Route Found"
    layovers = len(route) - 1 if len(route_details) == len(route) - 1 else len(route_details)

    route_info_content = html.Div([
        html.H3(route_status, className="text-lg font-bold text-green-600"),
        html.P(f"📍 Total Distance: {total_distance} km", className="font-semibold"),
        html.P(f"✈️ Number of Layovers: {layovers}", className="font-semibold"),
        html.P(f"💰 Estimated Price: ${estimated_price:.2f}", className="font-semibold"),
        html.H4("🛫 Flight Route Details", className="font-bold mt-4"),
        *route_details
    ], className="p-2 rounded-md my-3")


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