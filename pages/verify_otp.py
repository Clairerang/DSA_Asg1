from dash import dcc, html, register_page, Input, Output, State, callback
import dash_bootstrap_components as dbc
import dash

# Register the OTP verification page
register_page(__name__, path='/verify-otp')

# Layout for OTP Verification Page
layout = html.Div(className="min-h-screen flex flex-col justify-center items-center bg-gray-100", children=[
    dcc.Store(id='otp-storage', storage_type='session'),  # Store OTP from session
    dcc.Store(id='email-storage', storage_type='session'),  # Store user email for validation

    html.H2("OTP Verification", className="text-3xl font-bold text-gray-900 mb-6"),

    html.Div(className="bg-white p-6 rounded-lg shadow-md w-96", children=[
        html.Label("Enter the 6-digit OTP sent to your email:", className="block font-bold mb-2"),
        dcc.Input(id="otp-input", type="text", className="w-full p-2 border border-gray-300 rounded text-center",
                  placeholder="Enter 6-digit OTP", maxLength=6, inputMode="numeric"),

        html.Button("Verify OTP", id="verify-otp-btn", className="mt-4 bg-blue-600 text-white font-bold px-4 py-2 rounded w-full"),

        html.Div(id="otp-message", className="text-red-500 font-semibold mt-2 text-center"),
    ]),

    dcc.Location(id="redirect-url", refresh=True),  # Hidden URL for redirection
])

# Callback to verify OTP and redirect if correct
@callback(
    [Output("otp-message", "children"),
     Output("redirect-url", "pathname")],
    Input("verify-otp-btn", "n_clicks"),
    [State("otp-input", "value"),
     State("otp-storage", "data"),
     State("email-storage", "data")],
    prevent_initial_call=True
)
def verify_otp(n_clicks, user_otp, stored_otp, email):
    if not user_otp or len(user_otp) != 6:
        return "❌ OTP must be exactly 6 digits.", dash.no_update

    if not stored_otp or user_otp != stored_otp:
        return "❌ Invalid OTP. Try again.", dash.no_update

    return "✅ OTP Verified! Redirecting...", "/thank-you"