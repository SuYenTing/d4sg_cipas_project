# 網絡關係圖
from app import app
import dash
from dash import dash_table, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import itertools
import pandas as pd
import networkx as nx
import os
import numpy as np
from app import docData, nerDict


# 建立網絡關係圖所需資料
def setting_network(word, dic, articles, rank_pct):

    # 建立關係
    node_dictionary = dict()  # 紀錄實體(node)出現文章的編號
    edge_dictionary = dict()  # 紀錄兩個實體(node)同時出現在文章的編號
    wordInDocNums = 0  # 計算繪製網路關係圖所使用到的文章數
    # 走過每一篇文章
    for iDoc in range(len(articles)):
        article = articles[iDoc]
        if word in article:

            # 紀錄文章數
            wordInDocNums += 1

            appears = []
            # 走過每一個單位
            for item in dic:
                # 走過每一個單位的許多別稱
                for name in dic[item]:
                    # 如果有出現在文章內就加入list
                    if name in article:
                        appears.append(item)
                        break

            #利用 itertools.combinations 將list的名單進行排列組合 會自動排除重複值
            relationships = itertools.combinations(sorted(appears), 2)
            #走過每一條關係 存到關係字典中 如果不同文章中都有關係就會累計
            for relationship in relationships:

                # 紀錄兩個實體(node)同時出現在文章的編號
                if relationship in edge_dictionary:
                    edge_dictionary[relationship].add(iDoc)
                else:
                    edge_dictionary[relationship] = {iDoc}

                # 紀錄實體(node)出現文章的編號
                for node in relationship:
                    if node in node_dictionary:
                        node_dictionary[node].add(iDoc)
                    else:
                        node_dictionary[node] = {iDoc}

    # 若使用者輸入關鍵字沒有出現任何關係 則輸出空值
    if not edge_dictionary:
        return wordInDocNums, None, None, None, None

    # 建立隨機網絡點位
    G_ran = nx.random_geometric_graph(len(node_dictionary), 0)
    G = nx.Graph()

    # 把實體存到node
    for item, i in zip(node_dictionary, range(len(node_dictionary))):
        G.add_node(item, pos=(G_ran.nodes[i]['pos'][0], G_ran.nodes[i]['pos'][1]))

    # 把關係存到edge(keys為兩個node values為兩個node的交集文章ID)
    if edge_dictionary:
        for edge, iDocs in edge_dictionary.items():
            G.add_edge(edge[0], edge[1], weight=len(iDocs))  # weight採用兩篇文章的交集數量

    # Transform networkx nodes to dataframe
    nodelist = list(G.nodes(data=True)) # From G to list
    node_df = pd.DataFrame(nodelist, columns=['vertex', 'name_attribute']) # From list to DF
    nodeWeight = pd.DataFrame()
    for node, iDocs in node_dictionary.items():
        nodeWeight = pd.concat([
            nodeWeight, 
            pd.DataFrame(data={'vertex': node, 'weight': len(iDocs)}, index=[0])
            ])
    node_df = node_df.merge(nodeWeight, how='left', on='vertex')

    # Get G egdes to dataframe
    edge_df = nx.to_pandas_edgelist(G)

    # 對weight值分成10組做標準化 讓待會繪圖大小在不同的關鍵詞具有一致性
    binNums = 10
    node_df['weight'] = pd.cut(node_df['weight'], bins=binNums, labels=False)+1  # 加1避免0出現導致無法畫node
    # if len(edge_df) > 0:  # 防呆機制: 若沒有任何關係時則不處理
    edge_df['weight'] = pd.cut(edge_df['weight'], bins=binNums, labels=False)+1  # 加1避免0出現導致無法畫edge

    # 挑選特定比例的節點與對應的關係
    # 先根據標準化後的權重排序
    node_df = node_df.sort_values(by ='weight', ascending=False).reset_index(drop=True)
    # 選擇特定比例節點
    node_df = node_df.iloc[range(0, max(1, int(len(node_df) * float(rank_pct/100)))),:]
    node_use = node_df['vertex'].tolist()
    # 選擇對應的關係
    edge_df = edge_df[(edge_df['source'].isin(node_use)) & (edge_df['target'].isin(node_use))]

    # 整理node繪圖資訊
    nodes = [
        {
            'data': {'id': short, 'label': label, 'size': 10*w},
            'position': {'x': xy['pos'][0], 'y': xy['pos'][1]}
        }
        for short, label,w, xy in zip(node_df['vertex'], node_df['vertex'], node_df['weight'], node_df['name_attribute'])
    ]
    
    # 整理edges繪圖資訊
    edges = [
        {'data': {
            'source': source, 
            'target': target, 
            'weight': 0.3*w
            }
        }
        for source, target, w in zip(edge_df['source'], edge_df['target'], edge_df['weight'])
    ]

    # 將 node_dictionary 和 edge_dictionary 轉為df的dict格式
    nodeDf = pd.DataFrame()
    for key, value in node_dictionary.items():
        value = list(value)
        iNodeDf = pd.DataFrame(data={'node': key, 'docId': value}, index=range(len(value)))
        nodeDf = pd.concat([nodeDf, iNodeDf])
    nodeDf = nodeDf.reset_index(drop=True)
    nodeDfDict = nodeDf.to_dict()

    edgeDf = pd.DataFrame()
    for key, value in edge_dictionary.items():
        value = list(value)
        iEdgeDf = pd.DataFrame(data={'source': key[0], 'target': key[1], 'docId': value}, index=range(len(value)))
        edgeDf = pd.concat([edgeDf, iEdgeDf])
    edgeDf = edgeDf.reset_index(drop=True)
    edgeDfDict = edgeDf.to_dict()

    return wordInDocNums, nodes, edges, nodeDfDict, edgeDfDict


# 實體類別選項
network_nertype = [{"label": elem, "value": elem} for elem in nerDict.keys()]

# 網絡形狀選項
network_style = [
    {'label': "隨機", 'value': "random"},
    # {'label': "預設", 'value': "preset"},
    {'label': "圓形", 'value': "circle"},
    {'label': "同心圓", 'value': "concentric"},
    {'label': "網格", 'value': "grid"},
    {'label': "廣度優先", 'value': "breadthfirst"},
    {'label': "Cose", 'value': "cose"},
    {'label': "Cola", 'value': "cola"},
    {'label': "Euler", 'value': "euler"},
    {'label': "Spread", 'value': "spread"},
    {'label': "Dagre", 'value': "dagre"},
    {'label': "Klay", 'value': "klay"}
]

# Load extra layouts
cyto.load_extra_layouts()

styles = {
    'json-output': {
        'overflow-y': 'scroll',
        'height': 'calc(50% - 25px)',
        'border': 'thin lightgrey solid'
    },
    'tab': {'height': 'calc(98vh - 115px)'}
}


# 主頁面內容
page_network = dbc.Container([

    dbc.Row([
        dbc.Col([
            html.Center(html.H3("網絡關係圖")),
        ])
    ], className="row mb-3"),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("說明"),
                dbc.CardBody([
                    html.P('''
                    此處在使用者輸入單一關鍵字後，會先搜尋自定義字典內是否有同義詞，並依據該關鍵字及其同義詞篩選文本。
                    之後依文本篩選結果及使用者設定的實體類別，繪製出網絡關係圖。
                    節點的圖形大小反映該節點在這群文本中出現的多寡，圖形越大表示出現頻率越高；關係線的粗細表示兩個節點同時出現的頻率，線條越粗反映兩個節點同時出現的篇數越多。
                    使用者可在網絡關係圖上點選想關注的節點或者連結，即可看到相關的文章資訊提供閱覽。
                    '''),
                ])
             ])
        ])
    ], className="row mb-3"),

    # 使用者選單選項
    dbc.Row([
        dbc.Col([
            html.Span('請輸入想分析的關鍵詞:'),
            dbc.Input(id="network_word", type="text"),
        ]),
        dbc.Col([
            html.Span('請選擇要繪製的關係:'),
            dbc.Select(id="network_nertype", options=network_nertype, value="ORG"),
        ]),
        dbc.Col([
            html.Span('請選擇網絡形狀:'),
            dbc.Select(id="network_style", options=network_style, value="spread")
        ]),
        dbc.Col([
            html.Span('請選擇要繪製的節點數量(%):'),
            dbc.Input(id="network_rank", type="number", min=1, max=100, step=1, value=100),
        ]),
        dbc.Col([
            dbc.Button("開始繪製", id="network_submit", color="primary", style={'margin-top': '25px'})
        ]),
    ], className="row mb-5"),

    # 網絡關係圖輸出位置
    dbc.Row([
        dbc.Col([
            html.Div(id="network_info"),
            dbc.Spinner(html.Div(id="network_graph"), color="primary"),
        ])
    ], className="row mb-5"),

    # 使用者點選node時或edge時對應出現的相關文章列表
    dbc.Row([
        dbc.Col([
            html.Div(id='tap_respond_datatable_site')
        ]), 
    ], className="row mb-5"),

    # 使用者點選相關文章列表對應輸出原文內容
    dbc.Row([
        dbc.Col([
            html.Div(id='tap_respond_doc_output')
        ]), 
    ], className="row mb-5"),    

    # 放置網絡關係圖node或edge隱藏資料
    dcc.Store(id='node_dictionary'),
    dcc.Store(id='edge_dictionary'),
])


# WEB後端運作
# 繪製網絡關係圖
@app.callback(
    Output("network_info", "children"),
    Output("network_graph", "children"),
    Output("node_dictionary", "data"),
    Output("edge_dictionary", "data"),
    Input("network_submit", "n_clicks"),
    State("network_word", "value"),
    State("network_nertype", "value"),
    State("network_style", "value"),
    State("network_rank", "value"),
)
def update_options(n_clicks, network_word, network_nertype, network_style, network_rank):

    # 若使用者沒輸分析的關鍵詞則提示
    if not network_word:
        network_info = None
        network_graph = html.Span(['請記得要輸入分析的關鍵字唷!'])
        nodeDfDict = {}
        edgeDfDict = {}
        return network_info, network_graph, nodeDfDict, edgeDfDict

    # 建立網絡關係圖所需資料
    wordInDocNums, nodes, edges, nodeDfDict, edgeDfDict = setting_network(network_word, nerDict[network_nertype], docData['doc'], network_rank)

    # 若使者輸入關鍵字沒有出現在任何文章 則提示使用調整關鍵字
    if not nodes:
        network_info = None
        if wordInDocNums == 0:
            network_graph = html.Div([
                html.Span(['您輸入的關鍵字: ']),
                html.Span([network_word], style={'color': 'blue'}),
                html.Span([' 沒有出現在任何一篇文檔中，所以無法繪製網絡關係圖。要不要試試看別的關鍵字?'])
            ])
        else:
            network_graph = html.Div([
                html.Span(['您輸入的關鍵字: ']),
                html.Span([network_word], style={'color': 'blue'}),
                html.Span([f' 有出現在 {wordInDocNums} 篇文章中，但這些文章中的實體節點之間彼此沒有關係，所以無法繪製網絡關係圖。可以嘗試在自訂義字典中建立更多與該關鍵詞相關的實體類別詞彙，或者試試看別的關鍵字?'])
            ])
        nodeDfDict = {}
        edgeDfDict = {}
        return network_info, network_graph, nodeDfDict, edgeDfDict

    # 繪製網絡關係圖
    network_graph = cyto.Cytoscape(
        id='cytoscape',
        elements=nodes+edges,
        style={'width': '100%', 'height': '500px'},
        layout={
            'name': network_style,
            'animate': True,
            'animationDuration': 1000,
            'positions': {node['data']['id']: node['position'] for node in nodes}
        },
        stylesheet=[
            # Group selectors
            {
                'selector': 'node',
                'style': {
                    'content': 'data(label)',
                    'width': 'data(size)',
                    'height': 'data(size)'
                }
            },
            {
                'selector': 'edge',
                'style': {
                    'width': 'data(weight)'
                }
            }
        ]
    )

    # 整理輸出結果
    network_info = f'本次繪製網路圖共計有 {wordInDocNums} 篇文章，共計有 {len(nodes)} 個節點(Node)，共計有 {len(edges)} 個關係(Edge)'
    network_graph = html.Div(network_graph, style={'border': '2px solid black'})
    return network_info, network_graph, nodeDfDict, edgeDfDict


# 使用者點選node對應措施
@app.callback(Output('tap_respond_datatable_site', 'children'),
              Input('cytoscape', 'tapNodeData'),
              Input('cytoscape', 'tapEdgeData'),
              Input("network_submit", "n_clicks"),
              State('node_dictionary', 'data'),
              State('edge_dictionary', 'data'),
              prevent_initial_call=True,
              )
def displayTapNodeData(tapNodeData, tapEdgeData, n_clicks, node_dictionary, edge_dictionary):

    ctx = dash.callback_context
    if ctx.triggered:

        # 使用者重新按下開始繪製按鈕時則移除內容避免混淆
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == "network_submit":
            return None

        # 依使用者點選node或edge做對應處理
        userTapType = ctx.triggered[0]['prop_id']
        if userTapType == "cytoscape.tapNodeData":
            if tapNodeData:
                # 將儲存資料轉為資料表
                nodeDf = pd.DataFrame(node_dictionary)
                # 篩選使用者選取的節點
                nodeName = tapNodeData['id']
                # 整理輸出表格
                padDf = nodeDf[nodeDf['node'] == nodeName]
                padDfTitle = html.Center(html.H3(f'{nodeName} 相關文章'))

        elif userTapType == "cytoscape.tapEdgeData":
            if tapNodeData:
                # 將儲存資料轉為資料表
                edgeDf = pd.DataFrame(edge_dictionary)
                # 篩選使用者選取的關係
                sourceName = tapEdgeData['source']
                targetName = tapEdgeData['target']
                print(sourceName)
                print(targetName)
                # 整理輸出表格 
                padDf = pd.concat([
                    edgeDf[(edgeDf['source'] == sourceName) & (edgeDf['target'] == targetName)],
                    edgeDf[(edgeDf['source'] == targetName) & (edgeDf['target'] == sourceName)]
                    ])
                padDfTitle = html.Center(html.H3(f'{sourceName} 與 {targetName} 相關文章'))

        # 篩選對應文章
        tap_respond_datatable_site = [
            dbc.Row([
                dbc.Col([
                    padDfTitle,
                ])
            ]),
            dbc.Row([
                dbc.Col([
                    dash_table.DataTable(
                        id='tap_respond_datatable',
                        data=docData.iloc[padDf['docId']].to_dict('records'), 
                        columns=[{"name": "文章來源", "id": "source"}, {"name": "文章標題", "id": "title"}, {"name": "內文", "id": "doc"}], 
                        style_header={'textAlign': 'center'},
                        style_cell={'textAlign': 'left'},
                        style_cell_conditional=[
                            {'if': {'column_id': 'source'}, 'textAlign': 'center', 'minWidth': '150px', 'width': '150px', 'maxWidth': '150px'},
                            {'if': {'column_id': 'title'}, 'minWidth': '300px', 'width': '300px', 'maxWidth': '300px'},
                            ],
                        style_data={
                            'overflow': 'hidden',
                            'textOverflow': 'ellipsis',
                            'maxWidth': 0
                        },
                        fixed_rows={'headers': True},
                        filter_action="native",
                        page_size=10,
                    )
                ])
            ])            
        ]

        return tap_respond_datatable_site


# 依使用者點選節點文章輸出對應結果
@app.callback(
    Output("tap_respond_doc_output", "children"),
    Input("tap_respond_datatable", "active_cell"),
    Input("network_submit", "n_clicks"),
    prevent_initial_call=True,
    )
def tokenize_doc_output(active_cell, n_clicks):

    # 使用者重新按下開始繪製按鈕時則移除內容避免混淆
    ctx = dash.callback_context
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == "network_submit":
            return None

    # 若使用者點選上下頁按鈕時返回空值
    if active_cell is None:
        tap_respond_doc_output = list()
        return tap_respond_doc_output

    # 讀取使用者點擊的文章
    # 原文內容
    doc = docData['doc'][active_cell['row_id']]
    title = docData['title'][active_cell['row_id']]
    source = docData['source'][active_cell['row_id']]
    # 輸出斷詞與實體辨識內容
    tap_respond_doc_output = html.Div([

        dbc.Row([
            dbc.Col([
                html.H3(title),
                html.P('文本來源: '+source),
                html.P(doc)
            ]),
        ], className='row mt-3 mb-5')
    ])

    return tap_respond_doc_output
