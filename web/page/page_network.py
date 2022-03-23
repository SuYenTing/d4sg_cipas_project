# 網絡關係圖
from app import app
from dash import html, Input, Output, State
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import itertools
import pandas as pd
import networkx as nx
from app import docData, nerDict


# 建立網絡關係圖所需資料
def setting_network(word, dic, articles):

    # 建立關係
    net_assoc_dictionary = dict()
    # 走過每一篇文章
    for article in articles:
        if word in article:
            appears = []
            # 走過每一個單位
            for item in dic:
                # 走過每一個單位的許多別稱
                for name in dic[item]:
                    # 如果有出現在文章內就加入list
                    if name in article:
                        appears.append(item)
                        break

            #利用 itertools.combinations 將list的名單進行排列組合，會自動排除重複值
            relationships = itertools.combinations(sorted(appears),2)
            #走過每一條關係，存到關係字典中，如果不同文章中都有關係就會累計
            for relationship in relationships:
                if relationship in net_assoc_dictionary:
                    net_assoc_dictionary[relationship] += 1
                else:
                    net_assoc_dictionary[relationship] = 1

    # 若使用者輸入關鍵字沒有出現在任何文章 則輸出空值
    if not net_assoc_dictionary:
        elements = None
        nodes = None
        return elements, nodes

    # 建立隨機網絡點位
    G_ran = nx.random_geometric_graph(len(dic), 0)
    G = nx.Graph()
    # 把人物存到node
    for item, i in zip(dic, range(len(dic))):
        G.add_node(item,pos = (G_ran.nodes[i]['pos'][0], G_ran.nodes[i]['pos'][1]))
    # 把關係存到edge(keys 有兩個點, values 就是關係出現次數)
    for edge, weight in net_assoc_dictionary.items():
        G.add_edge(edge[0], edge[1], weight=weight)
    # 抓出關係出現次數,除以文章篇數,乘上多少倍取決於輸出結果,我們當作加權強度
    edges = G.edges()
    # weights = [G[u][v]['weight'] / len(articles) * 30 for u,v in edges]
    d = nx.degree_centrality(G)
    
    # Transform networkx nodes to dataframe
    nodelist = list(G.nodes(data=True)) # From G to list
    node_df = pd.DataFrame(nodelist, columns=['vertex', 'name_attribute']) # From list to DF
    def addweight(s):
        for k in d.keys():
            if s == k:
                return d[k]
    node_df['weight'] = node_df['vertex'].apply(addweight)

    # Get G egdes to dataframe
    edge_df = nx.to_pandas_edgelist(G) 
    #edge_df

    # 過濾出有關係的節點
    node_use = edge_df['source'].tolist()
    node_target = edge_df['target'].tolist()
    node_use.extend(node_target)
    node_use = list(dict.fromkeys(node_use))
    node_df = node_df[node_df['vertex'].isin(node_use)]

    nodes = [
        {
            'data': {'id': short, 'label': label,'size': int(100 * w)},
            'position': {'x': 3000 * xy['pos'][0], 'y': 3000 * xy['pos'][1]}
        }
        for short, label,w, xy in zip(node_df['vertex'],node_df['vertex'],node_df['weight'],node_df['name_attribute'])
    ]
    
    edges = [
        {'data': {'source': source, 'target': target, 'weight': 10 * w / len(articles) }}
        for source, target,w in zip(edge_df['source'],edge_df['target'],edge_df['weight'])
    ]
    #edges
    elements = nodes + edges
    return elements, nodes


# 實體類別選項
network_nertype = [{"label": elem, "value": elem} for elem in nerDict.keys()]

# 網絡形狀選項
network_style = [
    {'label': "隨機", 'value': "random"},
    {'label': "預設", 'value': "preset"},
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

# # Load extra layouts
# cyto.load_extra_layouts()

# 主頁面內容
page_network = dbc.Container([

    dbc.Row([
        dbc.Col([
            html.Center(html.H3("網絡關係圖")),
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
            dbc.Select(id="network_style", options=network_style, value="preset")
        ]),
        dbc.Col([
            dbc.Button("開始繪製", id="network_submit", color="primary", style={'margin-top': '25px'})
        ]),
    ], className="row mb-3"),

    # dbc.Row([
    #     dbc.Col([
    #         html.Span('請輸入節點數量:'),
            
    #     ]),
    #     dbc.Col([
    #         dbc.Button("開始繪製", id="network_submit", color="primary", style={'margin-top': '25px'})
    #     ]),
    # ], className="row mb-3"),

    # 網絡關係圖輸出位置
    dbc.Row([
        dbc.Col([
            dbc.Spinner(html.Div(id="network_graph"), color="primary"),
        ])
    ], className="row mb-3"),

    dbc.Row([

    ]),
])


# WEB後端運作
# 繪製網絡關係圖
@app.callback(
    Output("network_graph", "children"),
    Input("network_submit", "n_clicks"),
    State("network_word", "value"),
    State("network_nertype", "value"),
    State("network_style", "value")
)
def update_options(n_clicks, network_word, network_nertype, network_style):

    # 若使用者沒輸分析的關鍵詞則提示
    if not network_word:
        return html.Span(['請記得要輸入分析的關鍵字唷!'])

    # 建立網絡關係圖所需資料
    elements, nodes = setting_network(network_word, nerDict[network_nertype], docData['doc'])

    # 若使者輸入關鍵字沒有出現在任何文章 則提示使用調整關鍵字
    if not nodes:
        return html.Div([
            html.Span(['您輸入的關鍵字: ']),
            html.Span([network_word], style={'color': 'blue'}),
            html.Span([' 沒有出現在任何一篇文檔中，所以無法繪製網絡關係圖。要不要試試看別的關鍵字?'])
        ])

    # 繪製網絡關係圖
    network_graph = cyto.Cytoscape(
        id='cytoscape',
        elements=elements,
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
                # 'content': 'data(weight)',
                'line-color': 'rgb(' + 'data(weight)' + ',' + 'data(weight)' + ',' + 'data(weight)' + ')',
                'width': 'data(weight)'
                }
            }
        ]
    )

    return html.Div(network_graph, style={'border': '2px solid black'})