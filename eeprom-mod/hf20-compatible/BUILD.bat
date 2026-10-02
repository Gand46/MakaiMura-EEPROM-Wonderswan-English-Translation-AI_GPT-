@echo off
setlocal
if "%~1"=="" (
 echo Uso: BUILD.bat original.ws
 pause
 exit /b 1
)
python "%~dp0source\build_combined.py" "%~1" --out "%~dp0build_output"
pause
