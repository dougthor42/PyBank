call C:\WinPython34_x64\Scripts\env.bat
cd C:\WinPython34_x64\projects\github\PyBank
RMDIR /S /Q .\build\exe.win-amd64-3.4
python build_executables.py build
cd .\build\exe.win-amd64-3.4
gui.exe