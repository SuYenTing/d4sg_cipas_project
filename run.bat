@echo off

echo �ˬd�ثe��Ƨ��O�_���w�˵������� & echo.

if exist .\env\d4sg-cipas-env\ (

  echo �ثe�w���w�˵������� & echo.

) else (

  echo ���o�{�������� �}�l�إ�Python��������... & echo.

  python -m venv ./env/d4sg-cipas-env

  echo Python�������Ҥw�إߧ���! & echo.

  echo �}�l�w�ˬ����M�� �еy��... & echo.

  call .\env\d4sg-cipas-env\Scripts\activate.bat & python -m pip install -r .\env\requirements.txt

  echo �M��w�w�˧���! & echo.

  echo Python�������ҫظm�w���� & echo.
)


choice /M "�аݬO�_�n�i��CKIP�_���P�������? [Yes/No]"

if %errorlevel%==1 (

  echo �}�l�i��CKIP�_���P������� & echo.
  call .\env\d4sg-cipas-env\Scripts\activate.bat & python ./model/docTokenize.py
)

if %errorlevel%==2 (

  echo ���LCKIP�_���P������� & echo.

)

echo �}�l�إ�WEB���� & echo.
call .\env\d4sg-cipas-env\Scripts\activate.bat & python ./web/index.py

pause