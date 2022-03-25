# 文本CKIP斷詞與實體辨識
import pandas as pd
import pickle
import re
import sys
import os
import gdown
from ckiptagger import data_utils, construct_dictionary, WS, POS, NER
from dash import html
from datetime import datetime


# 確認CKIP模型是否已下載 若沒有則下載模型
def CheckModelExist(ckipModelPath):
    if not os.path.exists(ckipModelPath):
        print('目前尚未下載CKIP模型 開始下載模型 請稍等...')
        os.makedirs(ckipModelPath, exist_ok=True)
        data_utils.download_data_gdown("./model/ckiptagger/")
        print('CKIP模型下載完畢!')
    else:
        print('確認目前路徑下已有CKIP模型')
    return None


# 讀取文本資料夾檔案
def ReadDocData(docFilePath):

    # 讀取文本檔案位置資訊
    print('目前程式正在讀取文本檔案中...')
    docFileNames = os.listdir(docFilePath)
    docFileNames = [fileName for fileName in docFileNames if (fileName.endswith('.xls') or fileName.endswith('.xlsx') or fileName.endswith('.csv'))]

    # 迴圈讀取並整理文本    
    docData = pd.DataFrame()
    for i in range(len(docFileNames)):

        print(f'目前程式正在讀取文本: {docFileNames[i]}  進度: {i+1} / {len(docFileNames)}')

        try:
            # 依據檔案類型讀取文本
            if docFileNames[i].endswith('csv'):
                iDocData = pd.read_csv(f'{docFilePath}/{docFileNames[i]}')[['標題', '內文']]
            else:
                iDocData = pd.read_excel(f'{docFilePath}/{docFileNames[i]}')[['標題', '內文']]

        except UnicodeDecodeError:
            print(f"讀取文本檔案發生錯誤: 請確認 「{docFilePath}/{docFileNames[i]}」 檔案是否為 UTF-8 編碼")
            sys.exit(1)
        
        except KeyError:
            print(f"讀取文本檔案發生錯誤: 請確認 「{docFilePath}/{docFileNames[i]}」 檔案內是否有提供「標題」及「內文」兩個欄位")
            sys.exit(1) 

        except Exception as e:
            print(f"讀取文本檔案發生錯誤: 請確認 「{docFilePath}/{docFileNames[i]}」 檔案是否有問題")
            sys.exit(1)

        # 刪除全為NaN的列
        iDocData = iDocData[~iDocData.isna().any(axis=1)]

        # 建立資料來源欄位
        iDocData.insert(0, 'source', docFileNames[i])

        # 儲存資料
        docData = pd.concat([docData, iDocData])
    
    # 修改欄位名稱
    docData = docData.rename(columns={'標題': 'title', '內文': 'doc'}).reset_index(drop=True)

    # 新增ID欄位方便網頁dashtable在呈現時能夠判斷正確的row
    docData = docData.reset_index().rename(columns={'index': 'id'})

    return docData


# 執行CKIP斷詞
def RunCkipModel(docData, customDictFilePath, ckipModelPath):

    # 讀取自定義字典
    print('程式正在讀取自定義字典中...')
    customDictData = pd.read_excel(customDictFilePath)[['自定義詞', '同義詞']]
    customDict = customDictData.to_numpy().flatten()
    customDict = customDict[~pd.isnull(customDict)]
    customDict = list(set(customDict))
    customDict = {elem: 1 for elem in customDict}
    customDict = construct_dictionary(customDict)

    # 載入ckip模型
    print('程式正在載入CKIP模型...')
    wsModel = WS(ckipModelPath, disable_cuda=False)
    posModel = POS(ckipModelPath, disable_cuda=False)
    nerModel = NER(ckipModelPath, disable_cuda=False)

    # 篩選關注實體
    targetEntity = ['DATE', 'ORG', 'PERSON', 'EVENT', 'FAC', 'GPE', 'LOC', 'WORK_OF_ART']
    # WEB實體繪製顏色
    entityColor = {
        'DATE': '#ffb549',
        'ORG': '#dd2a7b', 
        'PERSON': '#515bd4', 
        'EVENT': '#8134af', 
        'FAC': '#8134af', 
        'GPE': '#8134af', 
        'LOC': '#8134af', 
        'WORK_OF_ART':'#8134af'
    }

    # 迴圈文本資料
    docTokenizeList = list()  # 儲存各篇文章斷詞結果
    docEntityDf = pd.DataFrame()  # 儲存各篇文章實體辨識結果
    dashNerContentList = list()  # 儲存DASH要呈現實體辨識結果語法
    for iDoc in range(len(docData)):

        print(f'目前程式正在執行CKIP斷詞與實體辨識 執行進度: {iDoc+1} / {len(docData)}')

        # 讀取使用者輸入文章
        doc = docData['doc'][iDoc]
        # 移除空格跳行字元
        doc = re.sub('\s', '', doc)

        # 執行CKIP斷詞
        wsModelResult = wsModel(
            [doc],
            sentence_segmentation=True,
            segment_delimiter_set={",", "。", ":", "?", "!", ";"},
            coerce_dictionary=customDict,
            )
        # 執行CKIP詞性標註
        posModelResult = posModel(wsModelResult)
        # 執行CKIP實體辨識
        entityModelResult = nerModel(wsModelResult, posModelResult)
        # 過濾出要關注的實體辨識
        entityModelResult = {elem for elem in entityModelResult[0] if elem[2] in targetEntity}

        # 儲存斷詞結果
        docTokenizeList.append(wsModelResult[0])

        # 儲存實體辨識結果
        iDocEntityDf = pd.DataFrame(data=entityModelResult).iloc[:, 2:4]
        iDocEntityDf.columns = ['實體類別', '詞彙']
        iDocEntityDf = iDocEntityDf[iDocEntityDf['實體類別'] != 'DATE']
        docEntityDf = pd.concat([docEntityDf, iDocEntityDf])

        # 整理實體辨識結果
        iDashNerContentList = list()
        normalWord = ''
        ix = 0
        while ix < len(doc):

            # 判斷該字位置是否有符合實體辨識結果
            entity = [elem for elem in entityModelResult if elem[0] == ix]

            if entity:

                # 紀錄先前的一般字詞
                iDashNerContentList.append(html.Span(normalWord))
                normalWord = ''

                # 紀錄實體辨識字詞
                entityEndSite = entity[0][1]
                entityType = entity[0][2]
                entityStr = doc[ix:entityEndSite]
                iDashNerContentList.append(html.Span(entityStr, style={'color': entityColor[entityType]}))
                iDashNerContentList.append(html.Span(entityType, style={'font-size': 'x-small', 'color': entityColor[entityType]}))
                ix = entityEndSite
            else:
                # 若未符合則紀錄一般字詞
                normalWord = f'{normalWord}{doc[ix]}'
                ix += 1
                
        iDashNerContentList.append(html.Span(normalWord))

        # 儲存實體辨識結果
        dashNerContentList.append(iDashNerContentList)

    # 清除重複實體辨識詞彙並排序
    docEntityDf = docEntityDf.drop_duplicates()
    docEntityDf = docEntityDf.sort_values(['實體類別', '詞彙']).reset_index(drop=True)

    # 過濾使用者尚未定義的詞彙
    customDictWord = customDictData.to_numpy().flatten()
    customDictWord = customDictWord[~pd.isnull(customDictWord)]
    customDictWord = list(set(customDictWord))
    docEntityDf = docEntityDf[~(docEntityDf['詞彙'].isin(customDictWord))]

    print('CKIP斷詞與實體辨識已執行完畢!')

    return docTokenizeList, docEntityDf, dashNerContentList


# 執行程式
if __name__ == '__main__':

    # 文本資料夾位置
    docFilePath = './data/docs'
    # 自定義字典位置
    customDictFilePath = './data/自定義字典.xlsx'
    # CKIP模型資料夾位置
    ckipModelPath = "./model/ckiptagger/data"
    # 執行結果存取位置
    modelOutputPath = './web/resource'

    # 確認CKIP模型是否已下載 若沒有則下載模型
    CheckModelExist(ckipModelPath)

    # 讀取文本資料夾檔案
    docData = ReadDocData(docFilePath)

    # 執行CKIP模型
    docTokenizeList, docEntityDf, dashNerContentList = RunCkipModel(docData, customDictFilePath, ckipModelPath)

    # 儲存檔案
    now = datetime.now().strftime('%Y%m%d%H%M%S')
    if not os.path.isdir(modelOutputPath):
        os.mkdir(modelOutputPath)
    with open(f'{modelOutputPath}/{now}.pickle', 'wb') as f:
        pickle.dump((docData, docTokenizeList, docEntityDf, dashNerContentList), f)
    print(f'檔案已儲存: {modelOutputPath}/{now}.pickle')
    
    # # 讀取檔案
    # with open(f'{modelOutputPath}/{now}.pickle', 'rb') as f:
    #     docData, docTokenizeList, docEntityDf, dashNerContentList = pickle.load(f)
