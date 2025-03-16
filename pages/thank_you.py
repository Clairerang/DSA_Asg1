from dash import dcc, html, register_page, Input, Output, State, callback
import dash_bootstrap_components as dbc
import random
from weasyprint import HTML

# Register the thank you page
register_page(__name__, path='/thank-you')

# Function to generate a random booking reference
def generate_booking_reference():
    return "SKY-" + ''.join(str(random.randint(0, 9)) for _ in range(8))

# Layout for thank you page
layout = html.Div(className="min-h-screen flex flex-col justify-center items-center bg-gray-100", children=[
    dcc.Store(id='selected-route-data', storage_type='local'),
    dcc.Store(id='passenger-info', storage_type='session'),

    # Title
   html.H2(id="thank-you-title", className="text-3xl font-bold text-center mb-4"), 

    # Confirmation message
    html.Div(className="rounded-lg text-center ", children=[
        html.P("We've sent a confirmation email with your booking details.", className="text-gray-700 mb-4"),
        html.P(id="booking-reference", className="font-bold text-lg mb-6"),
        
        # Buttons
        html.Div(className="grid md:grid-cols-2 grid-cols-1 ", children=[
            dcc.Link(
                dbc.Button("Return to Home", color="", className=""),
                href="/route-view"
            ),
            html.Button("Download Booking Details", id="download-pdf", className="bg-blue-600 hover:bg-blue-800 text-white font-bold py-2 px-4 rounded"),
        ])
    ]),

    # Hidden link for PDF download
    dcc.Download(id="download-booking"),
])
# Callback to populate the page dynamically
@callback(
    [Output("thank-you-title", "children"),
     Output("booking-reference", "children")],
    [Input("selected-route-data", "data"),
     Input("passenger-info", "data")]
)
def update_page(flight_data, passenger_data):
    if not passenger_data:
        return "Thank you! Your booking is confirmed!", "Booking Reference: N/A"

    booking_reference = generate_booking_reference()
    first_name = passenger_data.get('first_name', 'Guest')
    last_name = passenger_data.get('last_name', '')

    return (
        f"Thank you {first_name}. {" "}Your booking is confirmed!",
        f"Booking Reference: {booking_reference}"
    )

# Callback to generate and download booking details as PDF
@callback(
    Output("download-booking", "data"),
    Input("download-pdf", "n_clicks"),
    [State("selected-route-data", "data"),
     State("passenger-info", "data")],
    prevent_initial_call=True
)

def download_booking(n_clicks, flight_data, passenger_data):
    if not flight_data or not passenger_data:
        return None

    booking_reference = generate_booking_reference()

    booking_details_html = f"""
     <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 40px;
                width: 100vw;
                height: 100vh;
            }}
            .container {{
                border: 1px solid #000;
                padding: 20px;
            }}
            .title {{
                font-size: 24px;
                font-weight: bold;
                text-align: center;
                margin-bottom: 20px;
            }}
            .section-title {{
                font-weight: bold;
                background-color: #f0f0f0;
                padding: 5px;
                margin-top: 20px;
            }}
            .info-table {{
                width: 100%;
                border-collapse: collapse;
            }}
            .info-table td {{
                padding: 8px;
                border-bottom: 1px solid #ddd;
            }}
            .price-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            .price-table td {{
                padding: 8px;
                border-bottom: 1px solid #ddd;
            }}
            .total {{
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="title">e-Ticket Receipt & Itinerary</div>

            <div class="section-title">PASSENGER AND TICKET INFORMATION</div>
            <table class="info-table">
                <tr><td>Passenger Name:</td><td>{passenger_data.get('first_name', '')} {passenger_data.get('last_name', '')}</td></tr>
                <tr><td>Email:</td><td>{passenger_data.get('email', '')}</td></tr>
                <tr><td>Phone:</td><td>{passenger_data.get('phone', '')}</td></tr>
                <tr><td>Booking Reference:</td><td>{booking_reference}</td></tr>
                <tr><td>Issued By/Date:</td><td>{flight_data.get('departure_date', 'Not selected')}</td></tr>
            </table>

            <div class="section-title">TRAVEL INFORMATION</div>
            <table class="info-table">
                <tr><td>Flight:</td><td>SKY 123</td></tr>
                <tr><td>Departure:</td><td>{flight_data.get('departure_airport', {}).get('name', '')} ({flight_data.get('departure_airport', {}).get('iata', '')})</td></tr>
                <tr><td>Arrival:</td><td>{flight_data.get('arrival_airport', {}).get('name', '')} ({flight_data.get('arrival_airport', {}).get('iata', '')})</td></tr>
                <tr><td>Departure Date:</td><td>{flight_data.get('departure_date', 'Not selected')}</td></tr>
                <tr><td>Return Date:</td><td>{flight_data.get('return_date', 'Not selected')}</td></tr>
                <tr><td>Number of Stops:</td><td>{flight_data.get('num_stops', 0)}</td></tr>
            </table>

            <div class="section-title">FARE AND ADDITIONAL INFORMATION</div>
            <table class="price-table">
                <tr><td>Base Fare:</td><td>${flight_data.get('estimated_price', 0):.2f}</td></tr>
                <tr><td>GST (9%):</td><td>${flight_data.get('estimated_price', 0) * 0.09:.2f}</td></tr>
                <tr class="total"><td>Total Price:</td><td>${flight_data.get('estimated_price', 0) * 1.09:.2f}</td></tr>
            </table>
        </div>
    </body>
    </html>
    """

    pdf_path = "/tmp/booking_details.pdf"

    # Convert formatted HTML to PDF using WeasyPrint
    HTML(string=booking_details_html).write_pdf(pdf_path)

    return dcc.send_file(pdf_path)