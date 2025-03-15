import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, callback, register_page

# Register checkout page
register_page(__name__, path="/checkout")

# Define GST rate (9%)
GST_RATE = 0.09

# Layout
layout = html.Div(className="min-h-screen flex flex-col px-6 py-8", children=[
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='selected-route-data', storage_type='session'),  # Stores selected flight details
    dcc.Store(id='passenger-info', storage_type='session'),  # Stores passenger details (used in Thank You page)

    html.Div(id="checkout-content", className="bg-white p-6 rounded-lg shadow-md"),
])

# Callback to generate checkout page content
@callback(
    Output('checkout-content', 'children'),
    Input('selected-route-data', 'data')
)
def populate_checkout(route_data):
    if not route_data:
        return html.Div([
            html.H3("No flight selected", className="text-xl font-bold text-red-500"),
            html.P("Please go back and select a flight to continue.", className="text-gray-700"),
        ])

    # Extract flight details
    departure_airport = route_data.get('departure_airport', {})
    arrival_airport = route_data.get('arrival_airport', {})
    total_distance = route_data.get('total_distance', 0)
    base_price = route_data.get('estimated_price', 0)
    departure_date = route_data.get('departure_date', 'Not selected')
    return_date = route_data.get('return_date', 'Not selected')
    num_stops = route_data.get('num_stops', 0)

    # Calculate GST and total
    gst_amount = base_price * GST_RATE
    total_price = base_price + gst_amount

    return html.Div([
        html.Div(className="mb-6", children=[
            html.H3("Booking Summary", className="text-2xl font-bold mb-3"),
            html.Div(className="grid grid-cols-2 gap-4 mb-4", children=[
                html.Div(children=[
                    html.P("From:", className="font-semibold text-gray-700"),
                    html.P(f"{departure_airport.get('name', '')} ({departure_airport.get('iata', '')})"),
                ]),
                html.Div(children=[
                    html.P("To:", className="font-semibold text-gray-700"),
                    html.P(f"{arrival_airport.get('name', '')} ({arrival_airport.get('iata', '')})"),
                ]),
            ]),
            html.Div(className="grid grid-cols-2 gap-4 mb-4", children=[
                html.Div(children=[
                    html.P("Departure Date:", className="font-semibold text-gray-700"),
                    html.P(departure_date),
                ]),
                html.Div(children=[
                    html.P("Return Date:", className="font-semibold text-gray-700"),
                    html.P(return_date),
                ]),
            ]),
            html.P(f"Total Distance: {total_distance} km", className="text-gray-700 mb-1"),
            html.P(f"Number of Stops: {num_stops}", className="text-gray-700"),
        ]),

        # Passenger Details Form
        html.Div(className="bg-gray-50 p-5 rounded-lg shadow-md mb-6", children=[
            html.H3("Passenger Details", className="text-2xl font-bold mb-4"),
            html.Div(className="grid grid-cols-1 md:grid-cols-2 gap-4", children=[
                html.Div(children=[
                    html.Label("First Name", className="block text-gray-700 font-bold mb-2"),
                    dcc.Input(id="first-name", type="text", placeholder="Enter your first name",
                              className="w-full p-2 border border-gray-300 rounded"),
                ]),
                html.Div(children=[
                    html.Label("Last Name", className="block text-gray-700 font-bold mb-2"),
                    dcc.Input(id="last-name", type="text", placeholder="Enter your last name",
                              className="w-full p-2 border border-gray-300 rounded"),
                ]),
                html.Div(children=[
                    html.Label("Email", className="block text-gray-700 font-bold mb-2"),
                    dcc.Input(id="email", type="email", placeholder="Enter your email",
                              className="w-full p-2 border border-gray-300 rounded"),
                ]),
                html.Div(children=[
                    html.Label("Phone", className="block text-gray-700 font-bold mb-2"),
                    dcc.Input(id="phone", type="tel", placeholder="Enter your phone number",
                              className="w-full p-2 border border-gray-300 rounded"),
                ]),
            ]),
        ]),

        # Price Breakdown + Payment Button
        html.Div(className="bg-gray-100 p-6 rounded-lg shadow-md", children=[
            html.H3("Price Breakdown", className="text-xl font-bold mb-4"),
            
            html.Div(className="flex justify-between mb-2", children=[
                html.P("Base Fare:", className="font-semibold"),
                html.P(f"${base_price:.2f}")
            ]),
            
            html.Div(className="flex justify-between mb-2", children=[
                html.P("GST (9%):", className="font-semibold text-gray-600"),
                html.P(f"${gst_amount:.2f}", className="text-gray-600")
            ]),

            html.Hr(className="my-2"),

            html.Div(className="flex justify-between text-lg font-bold", children=[
                html.P("Total:"),
                html.P(f"${total_price:.2f}", className="text-green-600")
            ]),

            # Error message inside the card
            html.Div(id="error-message", className="text-red-500 font-semibold mt-4 text-start", style={"display": "none"}),

            # Buttons
            html.Div(className="grid grid-cols-2 mt-4 gap-4 text-center justify-center items-center", children=[
                dcc.Link(
                    html.Button("Back to Flight Selection", className="text-dark font-bold py-2 px-4 rounded"),
                    href="/route-view"
                ),
                html.Button("Proceed to Payment", id="payment-button", className="bg-green-700 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"),
            ]),
        ]),
    ])

# Callback to validate input and store passenger details in session storage
@callback(
    [Output('url', 'pathname', allow_duplicate=True),
     Output('error-message', 'children'),
     Output('error-message', 'style'),
     Output('passenger-info', 'data')],  # Store passenger details
    Input('payment-button', 'n_clicks'),
    [State('first-name', 'value'),
     State('last-name', 'value'),
     State('email', 'value'),
     State('phone', 'value')],
    prevent_initial_call=True
)
def proceed_to_payment(n_clicks, first_name, last_name, email, phone):
    if n_clicks:
        if not first_name or not last_name or not email or not phone:
            return (dash.no_update, "❌ Please fill in all fields before proceeding.", {}, dash.no_update)

        # Store passenger details in session storage
        passenger_data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone
        }

        return ('/thank-you', "", {"display": "none"}, passenger_data)

    return dash.no_update