from dash import html, dash_table, dcc, Output, Input, callback, register_page
from data_loader import airport_db  # Same shared data source

register_page(__name__, path='/table-view')

# Dropdown options for airports
airport_options = [
    {'label': f"{airport.name} ({airport.iata})", 'value': airport.iata}
    for airport in airport_db.airports.values()
]

layout = html.Div([
    html.H2("Table View - Flight Map Routing", className="text-4xl text-white font-bold my-3"),
    
    # Airport Selection Dropdown
    html.Label("Select an Airport:", className="block text-lg font-medium text-gray-100 mb-2"),
    dcc.Dropdown(
        id='airport-dropdown',
        options=airport_options,
        placeholder="Select an airport",
        className="mb-4 p-2 border border-gray-300 rounded-md"
    ),

    # Containers for tables
    html.Div(id='airport-info-table', className="mt-4"),
    html.Div(id='flight-schedule-table', className="mt-4")  # New flight schedule table
])


@callback(
    [Output('airport-info-table', 'children'),
     Output('flight-schedule-table', 'children')],  # Added flight schedule table
    [Input('airport-dropdown', 'value')]
)
def update_airport_table(selected_iata):
    airport = airport_db.get_airport(selected_iata)

    if not airport:
        return "", "", ""

    # ✅ Airport Information Table
    airport_table = dash_table.DataTable(
        columns=[{"name": "Attribute", "id": "Attribute"}, {"name": "Value", "id": "Value"}],
        data=[
            {"Attribute": "Name", "Value": airport.name},
            {"Attribute": "City", "Value": airport.city_name},
            {"Attribute": "Country", "Value": airport.country},
            {"Attribute": "Latitude", "Value": airport.latitude},
            {"Attribute": "Longitude", "Value": airport.longitude},
            {"Attribute": "Timezone", "Value": airport.timezone},
            {"Attribute": "Elevation", "Value": f"{airport.elevation} meters"}
        ],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'padding': '10px'},
        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'}
    )

    # ✅ Flight Schedule Table (Grouped by Airline & Destination)
    flight_schedule = []
    for route in airport.routes:
        for carrier in route.carriers:
            flight_schedule.append({
                "Airline": f"{carrier.name} ({carrier.iata})",
                "Destination": route.iata,
                "Departure Date": carrier.departure_date,
                "Departure Time": carrier.departure_time,
                "Arrival Date": carrier.arrival_date,
                "Arrival Time": carrier.arrival_time
            })

    if not flight_schedule:
        schedule_table = html.P("No flight schedules available for this airport.", className="text-red-500")
    else:
        schedule_table = dash_table.DataTable(
            columns=[
                {"name": "Airline", "id": "Airline"},
                {"name": "Destination", "id": "Destination"},
                {"name": "Departure Date", "id": "Departure Date"},
                {"name": "Departure Time", "id": "Departure Time"},
                {"name": "Arrival Date", "id": "Arrival Date"},
                {"name": "Arrival Time", "id": "Arrival Time"}
            ],
            data=flight_schedule,
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '10px'},
            style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'}
        )

    return airport_table, schedule_table
