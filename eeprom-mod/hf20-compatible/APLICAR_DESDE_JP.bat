@echo off
setlocal
if "%~1"=="" (
 echo Arrastra la ROM JP sobre este archivo.
 pause
 exit /b 1
)
python "%~dp0source\apply_patch.py" "%~1" "%~dp0patches\Makaimura_HF20_EEPROM_v1_FROM_JP.bps" "%~dp0Makaimura_HF20_EEPROM_v1.ws"
pause
