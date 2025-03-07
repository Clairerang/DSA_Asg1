import pandas as pd
import plotly.express as px
from dash import html, dcc, Output, Input, callback, register_page

# Register this page with Dash
register_page(__name__, path='/map-view')

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
    html.H2("Map View - Flight Map Routing"),

    html.Label("Select an Airport:"),
    dcc.Dropdown(
        id='airport-dropdown',
        options=airport_options,
        placeholder="Select an airport"
    ),

    html.Div(id='airport-info'),
    html.Div(id='airlines-info'),
    dcc.Graph(id='airport-map')
])

@callback(
    [Output('airport-info', 'children'),
     Output('airlines-info', 'children'),
     Output('airport-map', 'figure')],
    [Input('airport-dropdown', 'value')]
)
def update_airport_info(selected_iata):
    if not selected_iata:
        return "", "", px.scatter_geo(projection="natural earth")

    airport = airports_df[airports_df['IATA'] == selected_iata].iloc[0]

    airport_details = html.Div([
        html.H3(f"Airport: {airport['Airport Name']}"),
        html.P(f"Location: {airport['City']}, {airport['Country']}"),
        html.P(f"Coordinates: {airport['Latitude']}, {airport['Longitude']}"),
        html.P(f"Timezone: {airport['Timezone']}")
    ])

    related_routes = routes_df[(routes_df['Departure Airport IATA'] == selected_iata) |
                               (routes_df['Arrival Airport IATA'] == selected_iata)]

    airlines_serving = related_routes.merge(
        airlines_df, on='Airline ID', how='left'
    ).dropna(subset=['Airline Name'])

    if airlines_serving.empty:
        airlines_details = html.P("No airlines found for this airport.")
    else:
        airlines_list = [
            html.Li(f"{row['Airline Name']} ({row['Airline IATA']})")
            for _, row in airlines_serving.drop_duplicates(subset=['Airline ID']).iterrows()
        ]
        airlines_details = html.Div([html.H4("Airlines Serving This Airport:"), html.Ul(airlines_list)])

    map_fig = px.scatter_geo(
        lat=[airport['Latitude']],
        lon=[airport['Longitude']],
        text=[airport['Airport Name']],
        projection="natural earth",
        title=f"Location of {airport['Airport Name']}"
    )

    map_fig.update_traces(marker=dict(size=12, color="red"))
    map_fig.update_geos(showcountries=True, showcoastlines=True, showland=True, landcolor="lightgray")

    return airport_details, airlines_details, map_fig
