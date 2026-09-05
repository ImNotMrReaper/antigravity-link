param(
    [string]$Title = "Antigravity Link",
    [string]$Message = "New message received",
    [string]$Action = "chat"
)

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$repoDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$scriptPath = Join-Path $repoDir "agy_link.py"

$notify = New-Object System.Windows.Forms.NotifyIcon
$notify.Icon = [System.Drawing.SystemIcons]::Information
$notify.Visible = $true
$notify.Text = "Antigravity Link"

$clicked = $false
$actionBlock = {
    $global:clicked = $true
    $wt = Get-Command wt.exe -ErrorAction SilentlyContinue
    if ($wt) {
        Start-Process wt.exe -ArgumentList "-w", "0", "nt", "--title", "Antigravity Link Chat", "python", "`"$scriptPath`"", "chat" -WorkingDirectory "$repoDir"
    } else {
        Start-Process cmd.exe -ArgumentList "/c start `"Antigravity Link Chat`" python `"$scriptPath`" chat" -WorkingDirectory "$repoDir"
    }
}

Register-ObjectEvent -InputObject $notify -EventName BalloonTipClicked -Action $actionBlock | Out-Null
Register-ObjectEvent -InputObject $notify -EventName Click -Action $actionBlock | Out-Null

$notify.ShowBalloonTip(12000, $Title, $Message, [System.Windows.Forms.TooltipIcon]::Info)

# Pump Windows event loop for up to 12 seconds
$timeout = [DateTime]::Now.AddSeconds(12)
while ([DateTime]::Now -lt $timeout -and -not $clicked) {
    [System.Windows.Forms.Application]::DoEvents()
    Start-Sleep -Milliseconds 100
}

$notify.Visible = $false
$notify.Dispose()
