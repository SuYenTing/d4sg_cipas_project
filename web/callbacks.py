from app import app
from dash import html, Input, Output
import os

# 更新分析資源選項
@app.callback(
    Output("resource", "options"),
    Output("resource", "value"),
    Input("resource_refresh", "n_clicks")
    )
def resource_refresh(n_clicks):

    # 讀取目前有的資源列表
    resourceList = os.listdir('./web/resource')
    resourceList.sort()
    resourceList.reverse()

    # 建立選單
    options = [{'label': elem.split('.')[0], 'value': elem} for elem in resourceList]

    # 設定默認值
    value = resourceList[0]
    
    return options, value


# 依分析資源選項更新史料斷詞成果
@app.callback(
    Output("doc_now_resource", "children"),
    Input("resource", "value")
    )
def tokenize(resource):

    doc_now_resource = f"目前正在使用的資源: {resource}"

    return doc_now_resource