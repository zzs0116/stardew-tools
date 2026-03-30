@echo off
setlocal

REM 进入脚本所在目录
cd /d "%~dp0"

REM 建议本地安装 http-server（只需第一次）
call npm ls http-server >nul 2>&1
if errorlevel 1 (
  echo Installing http-server locally...
  call npm i -D http-server
)

echo.
echo Starting static server at http://127.0.0.1:5500
echo Root: %cd%\public
echo.

npx http-server public -p 5500
pause