@echo off
echo Rozpoczynam budowanie pliku wykonywalnego Price Monitor
..\.venv\Scripts\pyinstaller.exe --noconfirm --clean --onedir --windowed --paths "src" --name "PriceMonitor" "main.py"
echo Proces zakonczony. Pobrany plik znajduje sie w folderze 'dist/PriceMonitor'.
pause