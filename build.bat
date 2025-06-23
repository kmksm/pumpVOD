.\venv\Scripts\pyinstaller --distpath=pumpVOD --workpath=build -F --specpath=build -i ..\static\icon.ico main.py

RMDIR /S /Q build
MOVE /Y pumpVOD\main.exe pumpVOD\pumpVOD.exe
COPY /Y config.cfg pumpVOD\config.cfg
