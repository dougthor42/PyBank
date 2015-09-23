call C:\WinPython34_x64\Scripts\env.bat
cd C:\WinPython34_x64\projects\github\PyBank
echo ----- Deleting previous build -----
RMDIR /S /Q C:\WinPython34_x64\projects\github\PyBank\build\exe.win-amd64-3.4
echo ----- Running build script -----
python build_executables.py build
echo ----- Launching Application -----
cd .\build\exe.win-amd64-3.4\
PyBank.exe
cd ..\..
echo ----- Finished -----
@echo off
set size=0
for /r %%x in (.\build\exe.win-amd64-3.4\*) do set /a size+=%%~zx
set /a mb = %size% / 1000000
echo %size% Bytes
echo %mb% MB