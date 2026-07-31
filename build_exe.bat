@echo off
setlocal
cd /d "%~dp0"
python -m pip install -r requirements.txt
python -m PyInstaller --noconfirm --clean --onefile --windowed --name Rice2kMagicTasks src\rice2k_magic_tasks.py
if exist dist\Rice2kMagicTasks.exe (
  echo Built dist\Rice2kMagicTasks.exe
) else (
  echo Build failed.
  exit /b 1
)
