# 首頁
from app import app
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import os

page_index = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Center(html.H3("首頁說明")),
        ])
    ]),
])

# # 主頁面內容
# page_index = dbc.Container([

#     dbc.Row([
#         dbc.Col([
#             html.Center(html.H3("使用說明"))
#         ])
#     ], className="row mb-3"),

#     dbc.Row([
#         dbc.Col([
#             html.P("按下更新資源目錄按鈕，更新目前可以使用的資源:"),
#             dbc.Button("更新資源目錄", id="resource_refresh", color="primary")
#         ])
#     ], className="row mb-3"),

#     dbc.Row([
#         dbc.Col([
#             html.P("請選擇要分析的資源:"),
#             dbc.Select(
#                 id='resource_select',
#             ),
#         ], width=5)
#     ], className="row mb-3"),

#     # html.P(id='doc_now_resource'),
# ])


# # 更新分析資源選項
# @app.callback(
#     Output("resource_select", "options"),
#     Output("resource_select", "value"),
#     Input("resource_refresh", "n_clicks")
#     )
# def resource_refresh(n_clicks):

#     # 讀取目前有的資源列表
#     resourceList = os.listdir('./web/resource')
#     resourceList.sort()
#     resourceList.reverse()

#     # 建立選單
#     options = [{'label': elem.split('.')[0], 'value': elem} for elem in resourceList]

#     # 設定默認值
#     value = resourceList[0]
    
#     return options, value
