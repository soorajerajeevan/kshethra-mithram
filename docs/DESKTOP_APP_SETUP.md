# Desktop Application Setup Instructions

This guide explains how to create a Windows desktop application with a single-click launcher for the Temple App.

## Option 1: Simple Batch File (Easiest) ⚡

The easiest method is to use the batch file launcher.

### Setup Steps:

1. **Create a shortcut on Desktop:**
   - Right-click on `launch_app.bat` in the project folder
   - Click "Send to" → "Desktop (create shortcut)"
   - Right-click the shortcut → "Properties"
   - Change name to: "Temple App"
   - Click "Change Icon" → browse to any icon file or use default

2. **Or manually create a shortcut:**
   - Right-click on Desktop → New → Shortcut
   - Location: `C:\work\Project\RnD\temple_app\kshethra-mithram\launch_app.bat`
   - Name: "Temple App"
   - Finish

3. **Double-click the shortcut** to launch the app

### What it does:
- ✓ Checks if Docker is installed
- ✓ Verifies Docker daemon is running
- ✓ Stops any existing containers
- ✓ Starts a new container
- ✓ Opens browser to http://localhost:5000
- ✓ Shows live logs

---

## Option 2: Python GUI Launcher (Better UX) 🖥️

A professional GUI launcher with start/stop buttons and logs.

### Setup Steps:

1. **Install PyInstaller** (one-time setup):
   ```bash
   pip install pyinstaller
   ```

2. **Convert to executable:**
   ```bash
   pyinstaller --onefile --windowed --name "Temple App" launch_app.py
   ```
   
   This creates `dist\Temple App.exe`

3. **Create a Desktop shortcut:**
   - Copy `dist\Temple App.exe` to a convenient location
   - Right-click → Send to → Desktop (create shortcut)
   - Or create shortcut manually pointing to the exe

4. **Double-click the shortcut** to launch

### Features:
- ✓ Professional GUI with status indicator
- ✓ Start/Stop buttons
- ✓ Open Web button
- ✓ Live logs display
- ✓ Docker status check
- ✓ No terminal window

---

## Option 3: Advanced - Installer (For Distribution) 📦

Create an installer that can be distributed to others.

### Tools needed:
- NSIS (Nullsoft Scriptable Install System): https://nsis.sourceforge.io/

### Basic NSIS script (save as `temple_app_installer.nsi`):

```nsis
!include "MUI2.nsh"

Name "Temple App"
OutFile "TempleAppInstaller.exe"
InstallDir "$PROGRAMFILES\TempleApp"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

Section "Install"
  SetOutPath "$INSTDIR"
  File "dist\Temple App.exe"
  
  CreateDirectory "$SMPROGRAMS\TempleApp"
  CreateShortCut "$SMPROGRAMS\TempleApp\Temple App.lnk" "$INSTDIR\Temple App.exe"
  CreateShortCut "$DESKTOP\Temple App.lnk" "$INSTDIR\Temple App.exe"
SectionEnd
```

Build with NSIS Compiler, then run the resulting `TempleAppInstaller.exe`

---

## Quick Reference

| Method | Setup Time | User Experience | Distribution |
|--------|-----------|-----------------|--------------|
| Batch File | 1 min | Good | Easy (just copy .bat) |
| Python GUI | 5 min | Better | Easy (distribute .exe) |
| Installer | 15 min | Professional | Best (single .exe installer) |

---

## Recommended Setup (Option 2):

```bash
# Terminal commands to set up everything:
pip install pyinstaller
cd C:\work\Project\RnD\temple_app\kshethra-mithram
pyinstaller --onefile --windowed --name "Temple App" launch_app.py
# Shortcut created on Desktop → "Temple App.exe"
```

Then users can simply double-click the desktop icon!

---

## Prerequisites for End Users:

1. **Docker Desktop installed** - https://www.docker.com/products/docker-desktop
2. **Docker running** (automatically starts with Docker Desktop)

---

## Troubleshooting

### "Docker not found"
- Install Docker Desktop: https://www.docker.com/products/docker-desktop
- Restart your computer

### "Port 5000 already in use"
- Stop previous Docker container: `docker-compose down`
- Or change port in docker-compose.yml

### "Permission denied"
- Run as Administrator (right-click launcher → Run as administrator)

---

## Desktop Shortcut Tips

### Using an Icon:
1. Save a temple icon (`.ico` file) to project folder
2. Right-click shortcut → Properties
3. Click "Change Icon"
4. Browse to the `.ico` file

### Example icon websites:
- Flaticon: https://www.flaticon.com
- Icon8: https://icons8.com
- FontAwesome: https://fontawesome.com

---

## What Happens When You Click the Icon:

1. Docker container is stopped (if running)
2. New container is started
3. App waits 5 seconds for initialization
4. Browser opens to http://localhost:5000
5. Logs are displayed (batch) or GUI shows status (Python GUI)

---

## Next Steps:

1. **Try Option 1 first** (batch file is instant):
   ```bash
   launch_app.bat
   ```

2. **If you want GUI**, set up Option 2:
   ```bash
   pip install pyinstaller
   pyinstaller --onefile --windowed --name "Temple App" launch_app.py
   ```

3. **For production/distribution**, consider Option 3 (installer)
