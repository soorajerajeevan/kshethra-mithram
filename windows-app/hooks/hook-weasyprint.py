"""
PyInstaller hook for WeasyPrint.

Ensures that WeasyPrint's bundled DLLs, fonts, and data files are collected
when building the Windows standalone executable.
"""

from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = collect_all('weasyprint')
