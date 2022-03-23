# 建議加入詞彙
import dash_bootstrap_components as dbc
from dash import html, dash_table
from app import docEntityDf

# 主頁面內容
page_word = dbc.Container([

    dbc.Row([
        dbc.Col([
            html.Center(html.H3("建議加入詞彙")),
        ])
    ], className="row mb-3"),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("說明"),
                dbc.CardBody([
                    html.P('''
                    此處的表格為CKIP斷詞模型辨識出且尚未出現於自定義字典中的實體辨識詞彙。
                    使用者可直接在表格中修改與刪除詞彙，整理完後記得按下Export按鈕下載為CSV檔案，若跳離此畫面後會回復為原本結果。
                    記得要將整理好的詞彙放入自定義字典檔案內，重新去跑模型得到更好的斷詞結果。
                    '''),
                ])
             ])
        ])
    ], className="row mb-3"),

    dbc.Row([
        dbc.Col([
            dash_table.DataTable(
                id='word_datatable',
                data=docEntityDf.to_dict('records'), 
                columns=[{"name": "實體類別", "id": "實體類別"}, {"name": "詞彙", "id": "詞彙"}], 
                style_header={'textAlign': 'center'},
                style_cell={'textAlign': 'left'},
                style_cell_conditional=[
                    {'if': {'column_id': '實體類別'}, 'textAlign': 'center', 'minWidth': '150px', 'width': '150px', 'maxWidth': '150px'},
                    ],
                fixed_rows={'headers': True},
                filter_action="native",
                export_format='csv',
                row_deletable=True,
                editable=True,
                page_size=10,
            ),
        ])
    ], className="row mb-3"),

    dbc.Row([
    ]),
])