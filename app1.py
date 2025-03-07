import pandas as pd
import dash
from dash import html, dcc, Output, Input
import plotly.express as px

# Initialize Dash app
app = dash.Dash(__name__)

# Load datasets
airlines_df = pd.read_csv("./Sample Data/Airline Sample.csv")  # Your airline dataset
airports_df = pd.read_csv("./Sample Data/Airport Sample.csv")  # Your airport dataset
routes_df = pd.read_csv("./Sample Data/Route Sample.csv")      # Your routes dataset

# Convert \N (missing values) to NaN
airlines_df.replace("\\N", pd.NA, inplace=True)

# Prepare dropdown options (airport names + IATA code)
airport_options = [
    {'label': f"{row['Airport Name']} ({row['IATA']})", 'value': row['IATA']}
    for _, row in airports_df.iterrows()
]

# Dash Layout
app.layout = html.Div([
    html.H1("Flight Map Routing - Airport & Airlines Information"),

    html.Label("Select an Airport:"),
    dcc.Dropdown(
        id='airport-dropdown',
        options=airport_options,
        value=None,
        placeholder="Select an airport"
    ),

    html.Div(id='airport-info'),
    html.Div(id='airlines-info'),
    dcc.Graph(id='airport-map')  # World map with airport location
])

# Callback to update airport info, airline list, and world map
@app.callback(
    [Output('airport-info', 'children'),
     Output('airlines-info', 'children'),
     Output('airport-map', 'figure')],
    [Input('airport-dropdown', 'value')]
)
def update_airport_info(selected_iata):
    if not selected_iata:
        # Return empty map (just the world outline) if no airport is selected
        empty_fig = px.scatter_geo(projection="natural earth")
        return "", "", empty_fig

    # Lookup selected airport details
    airport = airports_df[airports_df['IATA'] == selected_iata].iloc[0]

    # Airport information display
    airport_details = html.Div([
        html.H3(f"Airport: {airport['Airport Name']}"),
        html.P(f"Location: {airport['City']}, {airport['Country']}"),
        html.P(f"Coordinates: {airport['Latitude']}, {airport['Longitude']}"),
        html.P(f"Timezone: {airport['Timezone']}")
    ])

    # Find routes to/from the selected airport
    related_routes = routes_df[(routes_df['Departure Airport IATA'] == selected_iata) |
                               (routes_df['Arrival Airport IATA'] == selected_iata)]

    # Merge routes with airline details
    airlines_serving = related_routes.merge(
        airlines_df, on='Airline ID', how='left'
    ).dropna(subset=['Airline Name'])

    # List airlines serving the airport
    if airlines_serving.empty:
        airlines_details = html.P("No airlines found for this airport.")
    else:
        airlines_list = [
            html.Li(f"{row['Airline Name']} ({row['Airline IATA']})")
            for _, row in airlines_serving.drop_duplicates(subset=['Airline ID']).iterrows()
        ]
        airlines_details = html.Div([
            html.H4("Airlines Serving This Airport:"),
            html.Ul(airlines_list)
        ])

    # Create world map with the selected airport's location
    map_fig = px.scatter_geo(
        lat=[airport['Latitude']],
        lon=[airport['Longitude']],
        text=[airport['Airport Name']],
        projection="natural earth",  # World map projection
        title=f"Location of {airport['Airport Name']}"
    )

    map_fig.update_traces(marker=dict(size=12, color="red"))  # Make marker more visible
    map_fig.update_geos(
        showcountries=True,  # Show country boundaries
        showcoastlines=True,  # Show coastlines
        showland=True,  # Show land areas
        landcolor="lightgray"
    )

    return airport_details, airlines_details, map_fig


if __name__ == '__main__':
    app.run_server(debug=True)