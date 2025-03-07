import plotly.express as px
from dash import html, dcc, Output, Input, callback, register_page
from data_loader import airport_db  # Import the global AirportDatabase object

register_page(__name__, path='/map-view')

# Dropdown options using the JSON data
airport_options = [
    {'label': f"{airport.name} ({airport.iata})", 'value': airport.iata}
    for airport in sorted(airport_db.airports.values(), key=lambda a: a.name)
]


layout = html.Div([
    html.H2("Map View - Flight Map Routing"),
    html.Label("Select an Airport:"),
    dcc.Dropdown(id='airport-dropdown', options=airport_options, placeholder="Select an airport"),

    html.Div(id='airport-info'),
    html.Div(id='airlines-info'),
    dcc.Graph(id='airport-map', 
        config={
            'scrollZoom': True,
            'displayModeBar': False,
        },
        style={'width': '100%', 'height': '500px'}
    )
])

@callback(
    [Output('airport-info', 'children'),
     Output('airlines-info', 'children'),
     Output('airport-map', 'figure')],
    [Input('airport-dropdown', 'value')]
)
def update_airport_info(selected_iata):
    airport = airport_db.get_airport(selected_iata)

    if not airport:
        return "", "", px.scatter_geo(projection="natural earth")

    # Airport Information
    airport_details = html.Div([
        html.H3(f"{airport.name}"),
        html.P(f"📍 {airport.city_name}, {airport.country}"),
        html.P(f"🌐 Coordinates: {airport.latitude}, {airport.longitude}"),
        html.P(f"🕒 Timezone: {airport.timezone}"),
        html.P(f"Elevation: {airport.elevation} meters")
    ])

    # Airlines serving the airport (carriers in all routes)
    all_carriers = set()
    for route in airport.routes:
        all_carriers.update(route.carriers)

    if not all_carriers:
        airlines_details = html.P("No airlines found for this airport.")
    else:
        airlines_list = [html.Li(f"{carrier.name} ({carrier.iata})") for carrier in all_carriers]
        airlines_details = html.Div([html.H4("Airlines Serving This Airport:"), html.Ul(airlines_list)])

    # Map
    map_fig = px.scatter_geo(
        lat=[airport.latitude],
        lon=[airport.longitude],
        text=[airport.name],
        projection="natural earth",
        title=f"Location of {airport.name}"
    )
    map_fig.update_traces(marker=dict(size=12, color="red"))
    map_fig.update_layout(
        dragmode="pan",  # Only panning allowed
        geo=dict(
            showcountries=True,
            showcoastlines=True,
            showland=True,
            landcolor="lightgray"
        )
    )

    return airport_details, airlines_details, map_fig
