@echo off
echo ===================================================
echo   Gerando Instalador Nativo do Quantyx
echo ===================================================

set "ISCC_PATH1=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
set "ISCC_PATH2=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
set "ISCC_PATH3=C:\Program Files\Inno Setup 6\ISCC.exe"

set "ISCC="

if exist "%ISCC_PATH1%" (
    set "ISCC=%ISCC_PATH1%"
) else if exist "%ISCC_PATH2%" (
    set "ISCC=%ISCC_PATH2%"
) else if exist "%ISCC_PATH3%" (
    set "ISCC=%ISCC_PATH3%"
)

if "%ISCC%"=="" (
    echo [ERRO] O compilador do Inno Setup nao foi encontrado nos caminhos padroes.
    echo Por favor, baixe e instale gratuitamente o Inno Setup 6:
    echo https://jrsoftware.org/isdl.php
    echo Apos a instalacao, rode este script novamente.
    pause
    exit /b 1
)

echo.
echo [1/2] Verificando a pasta dist\Quantyx...
if not exist "dist\Quantyx\Quantyx.exe" (
    echo [ERRO] O executavel Quantyx.exe nao foi encontrado na pasta dist\Quantyx.
    echo Por favor, rode o script build.bat primeiro para gerar a pasta dist.
    pause
    exit /b 1
)

echo.
echo [2/2] Compilando o instalador tradicional do Windows usando Inno Setup...
echo Caminho do ISCC: "%ISCC%"
"%ISCC%" quantyx_setup.iss

echo.
echo ===================================================
echo   Instalador gerado com sucesso!
echo   Verifique o arquivo "Quantyx_Installer.exe" na pasta "dist".
echo ===================================================
pause
