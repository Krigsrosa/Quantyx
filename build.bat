@echo off
chcp 65001 >nul
color 0A
title Quantyx Builder

:menu
cls
echo ==========================================================
echo               QUANTYX - OPCOES DE BUILD
echo ==========================================================
echo.
echo Escolha o tipo de empacotamento desejado:
echo.
echo  [1] PyInstaller (One-Dir)  - Mais rapido p/ testes
echo  [2] PyInstaller (One-File) - Unico .exe (pode ser lento)
echo  [3] Pynsist (Instalador)   - Gera um setup.exe (Recomendado p/ Usuarios)
echo  [4] Sair
echo.
set /p op=Digite a opcao desejada [1/2/3/4]: 

if "%op%"=="1" goto onedir
if "%op%"=="2" goto onefile
if "%op%"=="3" goto pynsist
if "%op%"=="4" goto exit
goto menu

:onedir
cls
echo ===================================================
echo   Construindo PyInstaller (One-Dir)...
echo ===================================================
call .venv\Scripts\activate.bat
pip install pyinstaller
call pyinstaller --name "Quantyx" ^
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
  --collect-all PyQt6 ^
  --collect-all pandas ^
  --collect-all numpy ^
  --collect-all pyqtgraph ^
  --collect-all scipy ^
  --collect-all sklearn ^
  --collect-all plotly ^
  --collect-all openpyxl ^
  --collect-all pptx ^
  main.py
echo ===================================================
echo Concluido! A pasta esta em "dist\Quantyx"
echo ===================================================
pause
goto menu

:onefile
cls
echo ===================================================
echo   Construindo PyInstaller (One-File)...
echo ===================================================
call .venv\Scripts\activate.bat
pip install pyinstaller
call pyinstaller --name "Quantyx" ^
  --onefile ^
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
  --collect-all PyQt6 ^
  --collect-all pandas ^
  --collect-all numpy ^
  --collect-all pyqtgraph ^
  --collect-all scipy ^
  --collect-all sklearn ^
  --collect-all plotly ^
  --collect-all openpyxl ^
  --collect-all pptx ^
  main.py
echo ===================================================
echo Concluido! O executavel esta em "dist\Quantyx.exe"
echo ===================================================
pause
goto menu

:pynsist
cls
echo ===================================================
echo   Construindo Instalador Windows (Pynsist)...
echo ===================================================
C:\Users\50116125\AppData\Roaming\Python\Python312\Scripts\pynsist.exe installer.cfg
echo ===================================================
echo Concluido! O instalador esta em "build\nsis"
echo ===================================================
pause
goto menu

:exit
exit
