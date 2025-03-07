import pandas as pd
from dash import html, dash_table, dcc, Output, Input, callback, register_page

# Register this page with Dash
register_page(__name__, path='/table-view')

# Load datasets
airlines_df = pd.read_csv("./Sample Data/Airline Sample.csv")  # Your airline dataset
airports_df = pd.read_csv("./Sample Data/Airport Sample.csv")  # Your airport dataset
routes_df = pd.read_csv("./Sample Data/Route Sample.csv")      # Your routes dataset

airlines_df.replace("\\N", pd.NA, inplace=True)

airport_options = [
    {'label': f"{row['Airport Name']} ({row['IATA']})", 'value': row['IATA']}
    for _, row in airports_df.iterrows()
]

layout = html.Div([
    html.H2("Table View - Flight Map Routing"),

    html.Label("Select an Airport:"),
    dcc.Dropdown(
        id='airport-dropdown',
        options=airport_options,
        placeholder="Select an airport"
    ),

    html.Div(id='airport-info-table'),
    html.Div(id='airlines-info-table')
])

@callback(
    [Output('airport-info-table', 'children'),
     Output('airlines-info-table', 'children')],
    [Input('airport-dropdown', 'value')]
)
def update_airport_table(selected_iata):
    if not selected_iata:
        return "", ""

    airport = airports_df[airports_df['IATA'] == selected_iata].iloc[0]

    airport_table = dash_table.DataTable(
        columns=[
            {"name": "Attribute", "id": "Attribute"},
            {"name": "Value", "id": "Value"}
        ],
        data=[
            {"Attribute": "Airport Name", "Value": airport['Airport Name']},
            {"Attribute": "City", "Value": airport['City']},
            {"Attribute": "Country", "Value": airport['Country']},
            {"Attribute": "Latitude", "Value": airport['Latitude']},
            {"Attribute": "Longitude", "Value": airport['Longitude']},
            {"Attribute": "Timezone", "Value": airport['Timezone']}
        ],
        style_table={'margin-bottom': '20px'}
    )

    related_routes = routes_df[(routes_df['Departure Airport IATA'] == selected_iata) |
                               (routes_df['Arrival Airport IATA'] == selected_iata)]

    airlines_serving = related_routes.merge(
        airlines_df, on='Airline ID', how='left'
    ).dropna(subset=['Airline Name'])

    if airlines_serving.empty:
        airlines_table = html.P("No airlines found for this airport.")
    else:
        airlines_table = dash_table.DataTable(
            columns=[
                {"name": "Airline Name", "id": "Airline Name"},
                {"name": "Airline IATA", "id": "Airline IATA"}
            ],
            data=airlines_serving[["Airline Name", "Airline IATA"]].drop_duplicates().to_dict('records'),
            style_table={'margin-bottom': '20px'}
        )

    return airport_table, airlines_table
