@echo off
setlocal
cd /d "%~dp0"
if "%~1"=="" (
  echo Arrastra la ROM ORIGINAL limpia sobre este BAT.
  echo Tambien: APLICAR_BPS.bat "ruta\original.ws"
  pause
  exit /b 1
)
where py >nul 2>nul
if not errorlevel 1 (
  py -3 source\patch_rom.py apply "%~1" patches\Makaimura_Phase4_1E_r2_CUMULATIVO_ORIGINAL.bps "Makaimura_WS_EEPROM2K_Phase4_1E_r2_EraseSave.ws"
) else (
  python source\patch_rom.py apply "%~1" patches\Makaimura_Phase4_1E_r2_CUMULATIVO_ORIGINAL.bps "Makaimura_WS_EEPROM2K_Phase4_1E_r2_EraseSave.ws"
)
set "RESULT=%ERRORLEVEL%"
pause
exit /b %RESULT%
