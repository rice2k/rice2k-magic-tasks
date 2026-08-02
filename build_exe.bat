@echo off
setlocal
cd /d "%~dp0"
python -m pip install -r requirements.txt
python -m PyInstaller --noconfirm --clean --onefile --windowed --name Rice2kMagicTasks --icon assets\rice2k_magic_tasks.ico --add-data "assets;assets" src\rice2k_magic_tasks.py
if errorlevel 1 (
  echo Build failed.
  exit /b 1
)
if exist dist\Rice2kMagicTasks.exe (
  echo Built dist\Rice2kMagicTasks.exe
) else (
  echo Build failed.
  exit /b 1
)
