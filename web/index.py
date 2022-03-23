# D4SG資料英雄計畫:黨產會專案網站
# 載入套件
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State

# 載入頁面
from app import app
from page.page_index import page_index
from page.page_tokenize import page_tokenize
from page.page_word import page_word
from page.page_network import page_network


# this example that adds a logo to the navbar brand
app.layout = html.Div([

    # navbar
    dbc.Navbar(
        dbc.Container(
            [
                html.A(
                    # Use row and col to control vertical alignment of logo / brand
                    dbc.Row(
                        [
                            dbc.Col(dbc.NavbarBrand("D4SG資料英雄計畫:黨產會專案", className="ml-2")),
                        ],
                        align="center",
                        className="g-0",
                    ),
                    href="/",
                    style={"textDecoration": "none"},
                ),
                dbc.NavbarToggler(id="navbar-toggler-menu"),
                dbc.Collapse(
                    dbc.Nav(
                        [
                            dbc.NavItem(dbc.NavLink("首頁", href="/", active="exact")),
                            dbc.NavItem(dbc.NavLink("史料斷詞成果", href="/page_tokenize", active="exact")),
                            dbc.NavItem(dbc.NavLink("建議加入詞彙", href="/page_word", active="exact")),
                            dbc.NavItem(dbc.NavLink("網絡關係圖", href="/page_network", active="exact")),
                            dbc.NavItem(dbc.NavLink("數位專題", href="https://yihuai0806.github.io/cipas/index.html", active="exact", external_link=True, target="_blank")),
                        ],
                        className="ml-2", navbar=True),
                    id="navbar-collapse-menu",
                    navbar=True,
                ),
            ]
        ),
        color="dark",
        dark=True,
        className="mb-5",
    ),

    # page content
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


# toggle the collapse on small screens
@app.callback(
    Output(f"navbar-collapse-menu", "is_open"),
    [Input(f"navbar-toggler-menu", "n_clicks")],
    [State(f"navbar-collapse-menu", "is_open")])
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


# navbar link
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):

    if pathname == "/":
        return page_index
    elif pathname == "/page_tokenize":
        return page_tokenize
    elif pathname == "/page_word":
        return page_word
    elif pathname == "/page_network":
        return page_network

    # If the user tries to reach a different page, return a 404 message
    return html.Div(
        dbc.Container([
            html.H1("404: Not found.", className="display-3"),
            html.Hr(className="my-2"),
            html.P(
                f"The pathname {pathname} was not recognised..."
                ),
            ], fluid=True, className="py-3",),
        className="p-3 bg-light rounded-3",
    )


if __name__ == "__main__":

    app.run_server(debug=True, port=8050)
    # app.run_server(host='0.0.0.0', debug=False, port=8050)  # 開啟對外連線
