from dash import html, dash_table, dcc, Output, Input, callback, register_page
from data_loader import airport_db  # Same shared data source

register_page(__name__, path='/table-view')

airport_options = [
    {'label': f"{airport.name} ({airport.iata})", 'value': airport.iata}
    for airport in airport_db.airports.values()
]

layout = html.Div([
    html.H2("Table View - Flight Map Routing"),
    html.Label("Select an Airport:"),
    dcc.Dropdown(id='airport-dropdown', options=airport_options, placeholder="Select an airport"),

    html.Div(id='airport-info-table'),
    html.Div(id='airlines-info-table')
])

@callback(
    [Output('airport-info-table', 'children'),
     Output('airlines-info-table', 'children')],
    [Input('airport-dropdown', 'value')]
)
def update_airport_table(selected_iata):
    airport = airport_db.get_airport(selected_iata)

    if not airport:
        return "", ""

    # Airport Information Table
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
        ]
    )

    # Airlines Table
    all_carriers = set()
    for route in airport.routes:
        all_carriers.update(route.carriers)

    if not all_carriers:
        airlines_table = html.P("No airlines found for this airport.")
    else:
        airlines_table = dash_table.DataTable(
            columns=[{"name": "Airline Name", "id": "Airline Name"}, {"name": "IATA", "id": "IATA"}],
            data=[{"Airline Name": carrier.name, "IATA": carrier.iata} for carrier in all_carriers]
        )

    return airport_table, airlines_table
