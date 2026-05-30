from dash import html, callback, Input, Output
import dash_bootstrap_components as dbc

def create_header():
    return html.Div([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Span("R", className="logo-icon"),
                        html.Span("ROCK TOOLS PERU", className="logo-text")
                    ], className="header-logo")
                ], width=2),
                
                dbc.Col([
                    dbc.Nav([
                        dbc.NavLink("Dashboard", href="/dashboard", active="exact"),
                        dbc.NavLink("Contratos", href="/contratos", active="exact"),
                        dbc.NavLink("Cargas", href="/cargas", active="exact"),
                        dbc.NavLink("Resultados", href="/resultados", active="exact"),
                        dbc.NavLink("📊 Análisis", href="/analisis", active="exact"),  # ← NUEVO
                        dbc.NavLink("Maestros", href="/maestros", active="exact"),
                        dbc.NavLink("Admin", href="/admin", active="exact"),
                    ], pills=True, className="header-nav")
                ], width=8),
                
                dbc.Col([
                    html.Div([
                        html.Span(id='user-name-display', className="user-name"),
                        dbc.Button("Salir", id="logout-button", color="link", className="logout-btn")
                    ], className="header-user")
                ], width=2)
            ], align="center")
        ], fluid=True)
    ], className="main-header")

@callback(
    Output('url', 'pathname', allow_duplicate=True),
    Input('logout-button', 'n_clicks'),
    prevent_initial_call=True
)
def logout(n_clicks):
    if n_clicks:
        return '/'
    return None

@callback(
    Output('user-name-display', 'children'),
    Input('session-store', 'data')
)
def update_user(data):
    return data.get('username', '')