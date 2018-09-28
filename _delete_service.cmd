@echo off
cd /d %~dp0


sc stop mqtt2mbs_Service
ping 127.0.0.1 -n 2 > nul
sc delete mqtt2mbs_Service
ping 127.0.0.1 -n 1 > nul



::pause & exit