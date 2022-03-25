chcp 65001

@echo off

echo Check whether the current folder has a virtual environment installed. & echo.

if exist .\env\d4sg-cipas-env\ (

  echo A virtual environment is currently installed. & echo.

) else (

  echo No virtual environment found. Start to create a Python virtual environment... & echo.

  python -m venv ./env/d4sg-cipas-env

  echo Python virtual environment has been established. & echo.

  echo Start installing related packages, please wait... & echo.

  call .\env\d4sg-cipas-env\Scripts\activate.bat & python -m pip install -r .\env\requirements.txt

  echo Python packages are all installed! & echo.

  echo Python virtual environment setup has been completed. & echo.
)


choice /M "Do you want to run CKIP word segmentation and name entity recognition? [Yes/No]"

if %errorlevel%==1 (

  echo Start CKIP word segmentation and entity recognition. & echo.
  call .\env\d4sg-cipas-env\Scripts\activate.bat & python ./model/docTokenize.py
)

if %errorlevel%==2 (

  echo Skip CKIP segmentation and entity recognition. & echo.

)

echo Start building a WEB environment... & echo.
call .\env\d4sg-cipas-env\Scripts\activate.bat & python ./web/index.py

pause