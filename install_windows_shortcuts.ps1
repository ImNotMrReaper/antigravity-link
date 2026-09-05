# Antigravity Link - Windows Shortcuts & URL Protocol Installer
# Run once on Windows to enable 'link' in PATH, clickable notifications, and Desktop shortcuts.

$ErrorActionPreference = "SilentlyContinue"
$repoDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$scriptPath = Join-Path $repoDir "agy_link.py"
$linkCmd = Join-Path $repoDir "link.cmd"
$batRunner = Join-Path $repoDir "run_link_windows.bat"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🤖 Installing Antigravity Link Windows Shortcuts & Protocol" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 1. Add repo directory to User PATH so 'link' works anywhere
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*$repoDir*") {
    $newPath = "$userPath;$repoDir"
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    $env:Path = "$env:Path;$repoDir"
    Write-Host "[✓] Added '$repoDir' to User PATH (Run 'link' anywhere!)" -ForegroundColor Green
} else {
    Write-Host "[✓] User PATH already contains '$repoDir'" -ForegroundColor Green
}

# 2. Register 'agy-link:' URL Protocol in HKCU (No admin required)
$regBase = "HKCU:\Software\Classes\agy-link"
New-Item -Path $regBase -Force | Out-Null
Set-ItemProperty -Path $regBase -Name "(default)" -Value "URL:Antigravity Link Protocol"
Set-ItemProperty -Path $regBase -Name "URL Protocol" -Value ""
$cmdPath = "$regBase\shell\open\command"
New-Item -Path $cmdPath -Force | Out-Null
$launchCmd = "cmd.exe /c start `"Antigravity Link Chat`" python `"$scriptPath`" chat"
Set-ItemProperty -Path $cmdPath -Name "(default)" -Value $launchCmd
Write-Host "[✓] Registered 'agy-link://' notification protocol handler" -ForegroundColor Green

# 3. Create Desktop Shortcut: 'Antigravity Link Chat'
$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutFile = Join-Path $desktop "Antigravity Link Chat.lnk"
$wsh = New-Object -ComObject WScript.Shell
$shortcut = $wsh.CreateShortcut($shortcutFile)
$shortcut.TargetPath = "cmd.exe"
$shortcut.Arguments = "/c `"$batRunner`""
$shortcut.WorkingDirectory = $repoDir
$shortcut.WindowStyle = 1
$shortcut.Description = "Launch Antigravity Link Chat with Mr-Reaper"
$shortcut.Save()
Write-Host "[✓] Created Desktop Shortcut: '$shortcutFile'" -ForegroundColor Green

# 4. Create Start Menu Shortcut
$startMenu = [Environment]::GetFolderPath("Programs")
$smShortcutFile = Join-Path $startMenu "Antigravity Link Chat.lnk"
$smShortcut = $wsh.CreateShortcut($smShortcutFile)
$smShortcut.TargetPath = "cmd.exe"
$smShortcut.Arguments = "/c `"$batRunner`""
$smShortcut.WorkingDirectory = $repoDir
$smShortcut.Description = "Launch Antigravity Link Chat"
$smShortcut.Save()
Write-Host "[✓] Created Start Menu Shortcut: '$smShortcutFile'" -ForegroundColor Green

Write-Host "`n🎉 Installation complete! Senpai can now:" -ForegroundColor Yellow
Write-Host "   1. Type 'link' or 'link chat' in any PowerShell/CMD window."
Write-Host "   2. Type 'link ai <task>' to summon both AIs."
Write-Host "   3. Double-click 'Antigravity Link Chat' on the Windows Desktop."
Write-Host "   4. Click on incoming desktop notifications to pop up the chat!" -ForegroundColor Yellow
