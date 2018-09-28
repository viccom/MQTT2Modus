@echo off
cd /d %~dp0

set s32=%windir%\SysWOW64
set reg_file=MQTT2Modus_serv.reg
set prog_path=%cd:\=\\%
set prog_name=MQTT2Modus_serv.exe
set service_name=mqtt2mbs_Service

sc stop %service_name%
ping 127.0.0.1 -n 2 > nul
sc delete %service_name%
ping 127.0.0.1 -n 1 > nul
::wusa.exe "%cd%\Windows6.1-KB2999226-x86.msu" /quiet /norestart
::copy /y %cd%\srvany.exe %s32%\srvany.exe

srvany.exe install %service_name% %cd%\%prog_name%

REM sc create %service_name% binpath= "%cd%\srvany.exe" displayname= "%service_name% Service" depend= Tcpip start= auto 

REM echo Windows Registry Editor Version 5.00> %reg_file% 
REM echo [HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\%service_name%\Parameters] >> %reg_file%
REM echo "Application"="%prog_path%\\%prog_name%" >> %reg_file%
REM echo "AppDirectory"="%prog_path%" >> %reg_file%
REM regedit /s %reg_file%

REM ping 127.0.0.1 -n 1 > nul
REM FOR /F "tokens=3 delims=:" %%A IN ('sc qc %service_name% ^|findstr /N "START_TYPE"') DO set type=%%A
REM echo %type%|find /i "DEMAND" >nul && echo ����DEMAND >nul 2>nul || sc config %service_name% start= demand
REM del /s /q %reg_file%

::ping 127.0.0.1 -n 1 > nul
::FOR /F "tokens=3 delims=:" %%A IN ('sc qc %service_name% ^|findstr /N "START_TYPE"') DO set type=%%A
::echo %type%|find /i "DEMAND" >nul && echo ����DEMAND >nul 2>nul || sc config %service_name% start= demand

::pause & exit