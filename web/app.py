import dash
import dash_bootstrap_components as dbc
import os, pickle
import pandas as pd
import numpy as np
import re
from scipy.spatial import distance_matrix

# WEB初始化設定
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True,
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0'}]
)

# 網站名稱
app.title = 'D4SG資料英雄計畫:黨產會專案'


# 讀取最近執行斷詞與實體辨識結果
def ReadResource(resourceFilePath):
    resourceList = os.listdir(resourceFilePath)
    resourceList.sort()
    resource = resourceList[-1]
    with open(f'{resourceFilePath}/{resource}', 'rb') as f:
        docData, docTokenizeList, docEntityDf, dashNerContentList = pickle.load(f)
    return docData, docTokenizeList, docEntityDf, dashNerContentList

print('正在載入CKIP斷詞模型結果...')
docData, docTokenizeList, docEntityDf, dashNerContentList = ReadResource(resourceFilePath='./web/resource')


# 整理自定義字典內實體辨識詞彙 用於繪製網絡圖
def MakeNerDict(customDictFilePath):
    customDictData = pd.read_excel(customDictFilePath)
    customDictData['實體類別'] = customDictData['實體類別'].str.upper()
    customDictData = customDictData[~pd.isna(customDictData['實體類別'])]
    customDictData['同義詞'] = np.where(pd.isna(customDictData['同義詞']), customDictData['自定義詞'], customDictData['同義詞'])
    nerDict = dict()
    for nerType in pd.unique(customDictData['實體類別']):
        iCutomDictData =  customDictData[customDictData['實體類別'] == nerType]
        iNerDict = dict()
        for _, row in iCutomDictData.iterrows():

            if iNerDict.get(row['同義詞']):
                iNerDict[row['同義詞']].append(row['自定義詞'])
            else:
                iNerDict[row['同義詞']] = [row['自定義詞']]
        nerDict[nerType] = iNerDict
    return nerDict

print('正在整理自定義字典內實體辨識詞彙...')
nerDict = MakeNerDict(customDictFilePath='./data/自定義字典.xlsx')


# 計算文章相似度用於推薦文章
def ComputeDocSimilarity(docData, nerDict):

    # 將各實體類別的key作為詞矩陣
    wordDict = {}
    for nerType in nerDict.keys():
        wordDict = {**wordDict, **nerDict[nerType]}

    # 建立詞頻矩陣
    wordMatrix = {elem: list() for elem in wordDict}
    for doc in docData['doc']:
        # 清洗資料
        doc = re.sub('\s', '', doc)
        # 迴圈比對詞是否有在文章裡面
        for word in wordMatrix:
            if any([True if elem in doc else False for elem in wordDict[word]]):
                wordMatrix[word].append(1)
            else:
                wordMatrix[word].append(0)
    # 詞頻矩陣轉為Df(row:文本 column:詞 value: 是否出現)
    wordMatrix = pd.DataFrame(wordMatrix)

    # 整理各篇文章相似度(minkowski_distance)
    distanceMatrix = pd.DataFrame(
        distance_matrix(wordMatrix.values, wordMatrix.values), 
        index=wordMatrix.index, 
        columns=wordMatrix.index)

    # 整理各篇文章對應的推薦文章
    recommendDocs = dict()
    for i in range(len(distanceMatrix)):
        recommendDocs[i] = list(distanceMatrix.iloc[i].sort_values().head(6).index)

    return recommendDocs

print('正在計算文章相似度...')
recommendDocs = ComputeDocSimilarity(docData, nerDict)

print('網站相關資料已載入完畢  請在網址列輸入 http://127.0.0.1:8050/ 即可使用')
print('使用網站期間請勿關閉此視窗！')