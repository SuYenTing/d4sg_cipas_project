@echo off

echo 檢查目前資料夾是否有安裝虛擬環境 & echo.

if exist .\env\d4sg-cipas-env\ (

  echo 目前已有安裝虛擬環境 & echo.

) else (

  echo 未發現虛擬環境 開始建立Python虛擬環境... & echo.

  python -m venv ./env/d4sg-cipas-env

  echo Python虛擬環境已建立完成! & echo.

  echo 開始安裝相關套件 請稍等... & echo.

  call .\env\d4sg-cipas-env\Scripts\activate.bat & python -m pip install -r .\env\requirements.txt

  echo 套件已安裝完畢! & echo.

  echo Python虛擬環境建置已完成 & echo.
)


choice /M "請問是否要進行CKIP斷詞與實體辨識? [Yes/No]"

if %errorlevel%==1 (

  echo 開始進行CKIP斷詞與實體辨識 & echo.
  call .\env\d4sg-cipas-env\Scripts\activate.bat & python ./model/docTokenize.py
)

if %errorlevel%==2 (

  echo 跳過CKIP斷詞與實體辨識 & echo.

)

echo 開始建立WEB環境 & echo.
call .\env\d4sg-cipas-env\Scripts\activate.bat & python ./web/index.py

pause