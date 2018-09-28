@echo off
cd /d %~dp0

pyinstaller -F MQTT2Modus_serv.py

ping 127.0.0.1 -n 1 >nul

copy  /Y .\dist\MQTT2Modus_serv.exe .\MQTT2Modus_serv.exe


::pause & exit