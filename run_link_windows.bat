@echo off
chcp 65001 >nul
title Antigravity Link - Windows Lead Node (Senpai59)
cd /d "%~dp0"

:MENU
cls
echo ============================================================
echo   🤖 ANTIGRAVITY LINK — Windows Lead Node (Senpai59)
echo ============================================================
echo   [1] Start Live Terminal Chat with Mr-Reaper
echo   [2] Run Sync Daemon (Foreground Console)
echo   [3] Start Sync Daemon (Silent Background)
echo   [4] Stop Background Daemon
echo   [5] Check Link & Peer Status
echo   [6] View Peer Inbox (INBOX.md)
echo   [7] Broadcast State Sync
echo   [8] Summon AI Agent (@ai / @both / @senpai / @reaper)
echo   [9] Install Global 'link' Command & Desktop Shortcuts
echo   [10] Install Auto-Start on Windows Login
echo   [11] Exit
echo ============================================================
set /p choice="Select an option (1-11): "

if "%choice%"=="1" (
    cls
    python agy_link.py chat
    pause
    goto MENU
)
if "%choice%"=="2" (
    cls
    python agy_link.py daemon
    pause
    goto MENU
)
if "%choice%"=="3" (
    cscript //nologo start_daemon_hidden.vbs
    echo [✓] AGY Link Daemon started in silent background!
    timeout /t 3 >nul
    goto MENU
)
if "%choice%"=="4" (
    taskkill /F /FI "WINDOWTITLE eq *agy_link.py*" >nul 2>&1
    wmic process where "commandline like '%%agy_link.py daemon%%'" delete >nul 2>&1
    echo [✓] Background daemon stopped.
    pause
    goto MENU
)
if "%choice%"=="5" (
    cls
    python agy_link.py status
    echo.
    pause
    goto MENU
)
if "%choice%"=="6" (
    cls
    python agy_link.py inbox
    echo.
    pause
    goto MENU
)
if "%choice%"=="7" (
    cls
    set /p taskname="Enter Task Title: "
    set /p taskfiles="Enter Active Files (comma-separated): "
    python agy_link.py sync --task "%taskname%" --status "in-progress" --files "%taskfiles%"
    echo.
    pause
    goto MENU
)
if "%choice%"=="8" (
    cls
    echo ============================================================
    echo   ⚡ SUMMON AI AGENT
    echo ============================================================
    set /p targetchoice="Target (both / remote / local) [default: both]: "
    if "%targetchoice%"=="" set targetchoice=both
    set /p aiprompt="Enter Task Prompt: "
    python agy_link.py summon "%aiprompt%" --target %targetchoice%
    echo.
    pause
    goto MENU
)
if "%choice%"=="9" (
    cls
    powershell -NoProfile -ExecutionPolicy Bypass -File install_windows_shortcuts.ps1
    pause
    goto MENU
)
if "%choice%"=="10" (
    powershell -NoProfile -ExecutionPolicy Bypass -File install_startup_task.ps1
    pause
    goto MENU
)
if "%choice%"=="11" exit /b 0

goto MENU
