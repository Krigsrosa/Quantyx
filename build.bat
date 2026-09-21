@echo off

echo ===================================================
echo   Compilando PyTab com PyInstaller (OneFile)
echo ===================================================

echo.
echo [1/4] Ativando o ambiente virtual...
cd /d %~dp0
call .venv\Scripts\activate.bat

echo.
echo [2/4] Instalando o PyInstaller...
pip install pyinstaller

echo.
echo [3/4] Iniciando a build do aplicativo (Modo Diretorio)...
python -m PyInstaller --name "Quantyx" ^
  --onedir ^
  --noconfirm ^
  --windowed ^
  --icon="img\app-ico-1.ico" ^
  --add-data "template\GlobalRD_Template.pptx;template" ^
  --add-data "img\app-ico-1.ico;img" ^
  --add-data "analysis;analysis" ^
  --add-data "data;data" ^
  --add-data "exports;exports" ^
  --add-data "plots;plots" ^
  --add-data "resources;resources" ^
  --add-data "settings;settings" ^
  --add-data "temp_report_images;temp_report_images" ^
  --add-data "ui;ui" ^
  --add-data "utils;utils" ^
  --add-data "widgets;widgets" ^
  --collect-all pandas ^
  --collect-all numpy ^
  --collect-all pyqtgraph ^
  --collect-all scipy ^
  --collect-all sklearn ^
  --collect-all pyarrow ^
  --collect-all fastparquet ^
  --collect-all openpyxl ^
  --collect-all pptx ^
  --collect-all xgboost ^
  --collect-all databricks ^
  main.py

echo.
echo ===================================================
echo   Build concluida com sucesso!
echo   A pasta do aplicativo esta em "dist\Quantyx"
echo.
echo   Para gerar o Instalador do Windows:
echo   Rode o script "create_installer.bat"
echo ===================================================
pause
