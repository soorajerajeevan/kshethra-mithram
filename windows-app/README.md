# Kshethra-Mithram Windows Standalone Application

This folder contains everything needed to build a self-contained Windows executable (.exe) for the Kshethra-Mithram temple management system.

## What This Does

- Bundles the entire Flask application, templates, static assets, and all Python dependencies into a single folder
- Requires **no installation** on the target machine — no Python, no Node.js required
- Stores the SQLite database and uploads in the user's `%APPDATA%` folder for persistence
- Automatically initializes the database on first run

## Quick Start

### Build the Application (Windows with Python + Node.js installed)

```powershell
PS> .\build.ps1
```

This will:
1. Build webpack assets (`npm run build`)
2. Install PyInstaller
3. Create the executable in `dist\kshethra-mithram\`

The build takes 2-5 minutes depending on your machine.

### Run the Application (Any Windows machine)

Double-click:
```
windows-app\dist\kshethra-mithram\kshethra-mithram.exe
```

The app will:
1. Start automatically
2. Open your browser to `http://127.0.0.1:5000`
3. Initialize the database (first run only)

## Data Storage

All application data is stored in:
```
%APPDATA%\kshethra-mithram\
├── temple.db          # SQLite database
├── uploads/           # Uploaded files
└── .appkey            # App secret (auto-generated)
```

This means:
- **Data persists** across app restarts and updates
- **No admin rights needed** — everything in user's home folder
- **Easy backup** — just copy the folder to another computer

## Prerequisites for Building

- **Python 3.11+** with all dependencies from `requirements.txt` installed
- **Node.js 18+** for webpack builds
- **PyInstaller** (installed automatically by `build.ps1`)
- **Windows 10 or 11** for the target machine

## Stopping the Application

Press `Ctrl+C` in the terminal window, or close the terminal.

## Troubleshooting

### "Port 5000 already in use"
Another application is using port 5000. Solutions:
- Close any other running Flask/web servers
- Or wait 30 seconds and try again

### "Database locked"
The database is in use by another instance. Only one .exe can access the database at a time.

### Build fails with "webpack not found"
Make sure you've run `npm install` in the project root:
```powershell
PS> npm install
```

### WeasyPrint errors when generating PDFs
PyInstaller sometimes misses WeasyPrint's fonts. If this happens:
1. Delete the `dist\kshethra-mithram` folder
2. Re-run `build.ps1`

## Files in This Folder

```
windows-app/
├── launcher.py                    # Entry point for the .exe
├── kshethra-mithram.spec          # PyInstaller configuration
├── hooks/
│   └── hook-weasyprint.py         # Ensures WeasyPrint DLLs are bundled
├── build.ps1                      # Build script
├── README.md                      # This file
├── dist/                          # Output folder (created by build.ps1)
│   └── kshethra-mithram/          # The distributable app
└── build/                         # Temporary build files (can be deleted)
```

## Development Workflow

This `windows-app/` folder is **completely isolated** from the main Docker/deployment workflow. You can:

1. Keep Docker deployments unchanged
2. Develop normally in the main codebase
3. Rebuild the Windows .exe whenever you want
4. Distribute the `dist/kshethra-mithram/` folder standalone

## Distributing to Others

1. Build the application with `.\build.ps1`
2. Copy the entire `dist\kshethra-mithram\` folder
3. Send it to your users or package it as a ZIP
4. Users just need to run the `.exe` — no setup required

## Future Improvements

- Auto-detect free port if 5000 is in use
- Add an installer/uninstaller (.msi)
- Add system tray icon
- Auto-update mechanism
- 64-bit only option to reduce file size

## Support

For issues specific to the Windows build, check:
- `windows-app/README.md` (this file)
- PyInstaller docs: https://pyinstaller.org/

For application issues, refer to the main project documentation.
