@echo off
REM update_construction_stats.bat
REM Run this manually or schedule with Windows Task Scheduler
REM Updates construction stats JSON and pushes to GitHub

echo ============================================
echo Rwanda Construction Stats Update
echo %date% %time%
echo ============================================

REM Set paths (update these for your environment)
set PYTHON_PATH=C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe
set SCRIPT_PATH=E:\Projects\UNDP\UNDP\Home Page\export_construction_stats.py
set REPO_PATH=E:\Projects\UNDP\UNDP\Home Page

REM Change to repo directory
cd /d %REPO_PATH%

REM Run Python export script
echo.
echo [1/3] Exporting stats from geodatabase...
"%PYTHON_PATH%" "%SCRIPT_PATH%"

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python script failed!
    pause
    exit /b 1
)

REM Git operations
echo.
echo [2/3] Adding changes to git...
git add construction_stats.json

echo.
echo [3/3] Committing and pushing to GitHub...
git commit -m "Stats update %date% %time%"
git push origin main

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Git push failed!
    pause
    exit /b 1
)

echo.
echo ============================================
echo SUCCESS! Stats updated on GitHub
echo Dashboard will refresh automatically
echo ============================================
echo.

REM Uncomment the line below to keep window open
REM pause