import plotly.express as px
from dash import html, dcc, Output, Input, callback, register_page
from data_loader import airport_db  # Import the global AirportDatabase object

register_page(__name__, path='/route-view')

# Dropdown options sorted alphabetically
airport_options = [
    {'label': f"{airport.name} ({airport.iata})", 'value': airport.iata}
    for airport in sorted(airport_db.airports.values(), key=lambda a: a.name)
]

layout = html.Div([
    html.H2("Route View - Flight Path Visualization", className="text-4xl font-bold text-black"),

    # Departure Airport Selection
    html.Label("Select Departure Airport:"),
    dcc.Dropdown(id='departure-airport-dropdown', options=airport_options, placeholder="Select a departure airport"),

    # Arrival Airport Selection
    html.Label("Select Arrival Airport:"),
    dcc.Dropdown(id='arrival-airport-dropdown', options=airport_options, placeholder="Select an arrival airport"),

    # Route Validation Message
    html.Div(id='route-validation', style={'font-weight': 'bold', 'margin-top': '10px', 'color': 'red'}),

    # Information Divs
    html.Div(id='route-info'),
    
    # Map Visualization with a line between the two locations
    dcc.Graph(id='route-map',
        config={'scrollZoom': True, 'displayModeBar': False},
        style={'width': '100%', 'height': '500px'}
    )
])

@callback(
    [Output('route-validation', 'children'),  # Displays if route exists
     Output('route-info', 'children'),
     Output('route-map', 'figure')],
    [Input('departure-airport-dropdown', 'value'),
     Input('arrival-airport-dropdown', 'value')]
)
def update_route_map(departure_iata, arrival_iata):
    # Ensure both airports are selected
    if not departure_iata or not arrival_iata:
        return "", "", px.scatter_geo(projection="natural earth")

    dep_airport = airport_db.get_airport(departure_iata)
    arr_airport = airport_db.get_airport(arrival_iata)

    if not dep_airport or not arr_airport:
        return "Invalid airport selection", "Invalid airport selection", px.scatter_geo(projection="natural earth")

    # Check if a direct route exists
    possible_routes = [route for route in dep_airport.routes if route.iata == arrival_iata]

    if not possible_routes:
        route_validation_msg = f"❌ No direct flight available from {dep_airport.name} to {arr_airport.name}."
    else:
        # Get airlines that operate the route
        serving_airlines = set()
        for route in possible_routes:
            for carrier in route.carriers:
                serving_airlines.add(f"{carrier.name} ({carrier.iata})")

        airline_list = html.Ul([html.Li(airline) for airline in serving_airlines])

        if serving_airlines:
            route_validation_msg = html.Div([
                html.Span(f"✅ Direct flights available from {dep_airport.name} to {arr_airport.name}."),
                html.H4(f"Airlines serving this route [{len(serving_airlines)}]:"),
                airline_list
            ])
        else:
            route_validation_msg = f"❌ No airlines currently operate flights from {dep_airport.name} to {arr_airport.name}."

    # Route Information
    route_details = html.Div([
        html.H3("Flight Route Details"),
        html.P(f"✈ Departure: {dep_airport.name} ({dep_airport.iata}) - {dep_airport.city_name}, {dep_airport.country}"),
        html.P(f"🎯 Arrival: {arr_airport.name} ({arr_airport.iata}) - {arr_airport.city_name}, {arr_airport.country}"),
        html.P(f"🌐 Distance: TBD (Need actual data source for distance)")
    ])

    # Map with line_geo (draw route if it exists)
    route_fig = px.line_geo(
        lat=[dep_airport.latitude, arr_airport.latitude],
        lon=[dep_airport.longitude, arr_airport.longitude],
        projection="natural earth",
    )
    
    # Add a dashed line style
    route_fig.update_traces(
        line=dict(dash="dash", width=2, color="blue"),
        mode="lines+markers",
        marker=dict(size=10, color=["red", "green"])  # Red for departure, Green for arrival
    )

    route_fig.update_layout(
        dragmode="pan",
        geo=dict(
            showland=True,
        ),
        title=f"Flight Route from {dep_airport.name} to {arr_airport.name}"
    )

    return route_validation_msg, route_details, route_fig
