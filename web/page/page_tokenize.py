# 史料斷詞成果
from app import app
from dash import html, dash_table, Input, Output
import dash_bootstrap_components as dbc
from app import docData, docTokenizeList, dashNerContentList, recommendDocs


# 主頁面內容
page_tokenize = dbc.Container([

    dbc.Row([
        dbc.Col([
            html.Center(html.H3("史料斷詞成果")),
        ])
    ], className="row mb-3"),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("說明"),
                dbc.CardBody([
                    html.P('''
                    此處內容為以CKIP斷詞模型對使用者提供文本進行斷詞與實體辨識結果。
                    並透過自定義字典內建立的實體類別詞彙作為詞矩陣，以相似度算法找出與該文本相似的文章。
                    使用者可參考目前模型斷詞與實體辨識結果，新增詞彙到自定義字典內，增加模型斷詞能力。
                    請點選表格內任一文本，即可呈現CKIP模型斷詞成果與推薦相關文章。
                    '''),
                    # html.P(''),
                    # html.P('使用者可參考目前模型斷詞與實體辨識結果，新增詞彙到自定義字典內，增加模型斷詞能力。'),
                    # html.P('請點選表格內任一文本，即可呈現CKIP模型斷詞成果與推薦相關文章。')
                ])
             ])
        ])
    ], className="row mb-3"),

    # 文章列表
    dbc.Row([
        dbc.Col([
            dash_table.DataTable(
                id='tokenize_doc_datatable',
                data=docData.to_dict('records'), 
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
        ]), 
    ], className="row mb-3"),

    # 依使用者點選文章輸出斷詞與實體辨識內容
    dbc.Row([
        dbc.Col([
            dbc.Spinner(html.Div(id="tokenize_doc_output"), color="primary")
        ]),
    ], className='row mt-3 mb-5'),

    # 依使用者點選文章輸出相關文章
    dbc.Row([
        dbc.Col([
            dbc.Spinner(html.Div(id="tokenize_doc_recommend"), color="primary")
        ]),
    ], className='row mt-3 mb-5'),
])


# WEB後端運作
# 依使用者搜尋內容輸出對應結果
@app.callback(
    Output("tokenize_doc_output", "children"),
    Output("tokenize_doc_recommend", "children"),
    Input("tokenize_doc_datatable", "active_cell"),
    prevent_initial_call=True,
    )
def tokenize_doc_output(active_cell):

    # 若使用者點選上下頁按鈕時返回空值
    if active_cell is None:
        tokenize_doc_output = list()
        tokenize_doc_recommend = list()
        return tokenize_doc_output, tokenize_doc_recommend

    # 讀取使用者點擊的文章
    # 原文內容
    doc = docData['doc'][active_cell['row_id']]
    title = docData['title'][active_cell['row_id']]
    source = docData['source'][active_cell['row_id']]
    tabDocContent = dbc.Card(dbc.CardBody(
        html.Div([
            html.H3(title),
            html.P('文本來源: '+source),
            html.P(doc)
            ], 
            style={'whiteSpace': 'pre-wrap'})), 
        className="mt-3")
    # 斷詞結果
    docTokenize = docTokenizeList[active_cell['row_id']]
    docTokenize = html.P(' / '.join(docTokenize))
    tabTokenizeContent = dbc.Card(dbc.CardBody(html.Div(docTokenize, style={'whiteSpace': 'pre-wrap'})), className="mt-3")
    # 實體辨識結果
    dashNerContent = dashNerContentList[active_cell['row_id']]
    tabNerContent = dbc.Card(dbc.CardBody(html.Div(dashNerContent, style={'whiteSpace': 'pre-wrap'})), className="mt-3")

    # 輸出斷詞與實體辨識內容
    tokenize_doc_output = html.Div([

        dbc.Row([
            dbc.Col([
                dbc.Tabs(
                    [
                        dbc.Tab(tabDocContent, label="原文內容", tab_id="tab-1"),
                    ],
                    active_tab="tab-1"
                )
            ], className='col-6'),

            dbc.Col([
                dbc.Tabs(
                    [
                        dbc.Tab(tabTokenizeContent, label="斷詞結果", tab_id="tab-1"),
                        dbc.Tab(tabNerContent, label="實體辨識", tab_id="tab-2"),
                    ],
                    active_tab="tab-1"
                )
            ], className='col-6'),

        ], className='row mt-3 mb-5')
    ])

    # 整理推薦文章
    recommendDocIdx = recommendDocs[active_cell['row_id']][1:]
    recommendDocTab = list()
    for i in range(len(recommendDocIdx)):
        recommendTitle = docData['title'][recommendDocIdx[i]]
        recommendSource = docData['source'][recommendDocIdx[i]]
        recommendDoc = docData['doc'][recommendDocIdx[i]]
        tabContent = dbc.Card(dbc.CardBody(
            html.Div([
                html.H3(recommendTitle),
                html.P('文本來源: '+recommendSource),
                html.P(recommendDoc)
                ], style={'whiteSpace': 'pre-wrap'})), 
            className="mt-3")
        recommendDocTab.append(dbc.Tab(tabContent, label=f"相關文章{i+1}", tab_id=f"tab-{i+1}"))

    # 輸出推薦文章
    tokenize_doc_recommend = html.Div([

        dbc.Row([
            dbc.Col([
                dbc.Tabs(dbc.Tab(tabDocContent, label="原文內容", tab_id="tab-1"), active_tab="tab-1")
            ], className='col-6'),

            dbc.Col([
                dbc.Tabs(recommendDocTab, active_tab="tab-1")
            ], className='col-6'),

        ], className='row mt-3 mb-5')
    ])

    return tokenize_doc_output, tokenize_doc_recommend