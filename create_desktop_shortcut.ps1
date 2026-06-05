# PBI Error Helper - Crear acceso directo en el escritorio
# YPF / DA&IA

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$TargetPath = Join-Path $ScriptDir "run_app.bat"
$IconPath = Join-Path $ScriptDir "assets\icon.ico"
$ShortcutPath = [Environment]::GetFolderPath("Desktop") + "\PBI Error Helper.lnk"

Write-Host "========================================"
Write-Host "  PBI Error Helper"
Write-Host "  Creando acceso directo..."
Write-Host "========================================"
Write-Host ""

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $TargetPath
$Shortcut.WorkingDirectory = $ScriptDir
$Shortcut.Description = "PBI Error Helper - Base de conocimiento de errores Power BI"
$Shortcut.WindowStyle = 1

if (Test-Path $IconPath) {
    $Shortcut.IconLocation = $IconPath
    Write-Host "[OK] Usando icono YPF"
} else {
    Write-Host "[*] Icono no encontrado, usando predeterminado"
}

$Shortcut.Save()

if (Test-Path $ShortcutPath) {
    Write-Host ""
    Write-Host "[OK] Acceso directo creado:"
    Write-Host "     $ShortcutPath"
    Write-Host ""
    Write-Host "Doble click en 'PBI Error Helper' en el escritorio para iniciar."
} else {
    Write-Host ""
    Write-Host "[ERROR] No se pudo crear el acceso directo"
}

Write-Host ""
Write-Host "========================================"
