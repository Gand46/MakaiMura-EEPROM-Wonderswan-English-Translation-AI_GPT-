@echo off
setlocal
if "%~1"=="" (
  echo Usage: BUILD_HF20.bat CLEAN_JP.ws
  exit /b 2
)
set "BASE_ROM=%~f1"
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 source\build_phase4w_hf20.py "%BASE_ROM%" HF20_PRIVATE.ws HF20_CUMULATIVE_FROM_JP.bps
  if errorlevel 1 exit /b 1
  py -3 source\validate_hf20.py "%BASE_ROM%"
) else (
  python source\build_phase4w_hf20.py "%BASE_ROM%" HF20_PRIVATE.ws HF20_CUMULATIVE_FROM_JP.bps
  if errorlevel 1 exit /b 1
  python source\validate_hf20.py "%BASE_ROM%"
)
if errorlevel 1 exit /b 1
echo HF20 build and structural verification completed.
