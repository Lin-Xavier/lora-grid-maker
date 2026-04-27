@echo off
setlocal EnableExtensions

cd /d "%~dp0"

echo Current folder:
echo %CD%
echo.

if not exist "requirements.txt" (
    echo ERROR: requirements.txt was not found in this folder.
    echo Please extract the whole ZIP package, not only this BAT file.
    pause
    exit /b 1
)

if not exist "lora_grid_maker_qt.py" (
    echo ERROR: lora_grid_maker_qt.py was not found in this folder.
    echo Please extract the whole ZIP package, not only this BAT file.
    pause
    exit /b 1
)

set PY_VERSION=3.11.8
set PY_ZIP=python-%PY_VERSION%-embed-amd64.zip
set PY_URL=https://www.python.org/ftp/python/%PY_VERSION%/%PY_ZIP%
set PY_DIR=%CD%\portable_python
set GETPIP_URL=https://bootstrap.pypa.io/get-pip.py

if not exist "%PY_DIR%\python.exe" (
    echo Downloading portable Python...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri '%PY_URL%' -OutFile '%PY_ZIP%'"
    if errorlevel 1 (
        echo ERROR: Failed to download portable Python.
        pause
        exit /b 1
    )

    echo Extracting portable Python...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive -Path '%PY_ZIP%' -DestinationPath '%PY_DIR%' -Force"
    if errorlevel 1 (
        echo ERROR: Failed to extract portable Python.
        pause
        exit /b 1
    )
)

echo Enabling site packages in embeddable Python...
powershell -NoProfile -ExecutionPolicy Bypass -Command "(Get-Content '%PY_DIR%\python311._pth') -replace '#import site','import site' | Set-Content '%PY_DIR%\python311._pth'"

if not exist "%PY_DIR%\Scripts\pip.exe" (
    echo Downloading get-pip.py...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri '%GETPIP_URL%' -OutFile 'get-pip.py'"
    if errorlevel 1 (
        echo ERROR: Failed to download get-pip.py.
        pause
        exit /b 1
    )

    echo Installing pip into portable Python only...
    "%PY_DIR%\python.exe" get-pip.py
    if errorlevel 1 (
        echo ERROR: Failed to install pip into portable Python.
        pause
        exit /b 1
    )
)

echo Installing build dependencies into portable Python only...
"%PY_DIR%\python.exe" -m pip install --upgrade pip
"%PY_DIR%\python.exe" -m pip install -r "%CD%\requirements.txt"
if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

echo Building portable Qt EXE...
"%PY_DIR%\python.exe" -m PyInstaller ^
  --noconfirm ^
  --onefile ^
  --windowed ^
  --name LoRA_Grid_Maker ^
  --collect-all PySide6 ^
  "%CD%\lora_grid_maker_qt.py"

if errorlevel 1 (
    echo ERROR: PyInstaller build failed.
    pause
    exit /b 1
)

echo.
echo Done.
echo Your portable EXE is here:
echo %CD%\dist\LoRA_Grid_Maker.exe
echo.
echo You can copy only this EXE to another Windows computer.
echo The EXE may be large because it contains Python, Qt, Pillow, and the app code.
pause
