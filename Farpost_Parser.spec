# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# Collect customtkinter and curl_cffi assets
ctk_datas, ctk_binaries, ctk_hiddenimports = collect_all('customtkinter')
curl_datas, curl_binaries, curl_hiddenimports = collect_all('curl_cffi')

a = Analysis(
    ['gui.py'],
    pathex=['.'],
    binaries=ctk_binaries + curl_binaries,
    datas=[
        ('src', 'src'),              # Include the entire src directory
        *ctk_datas,
        *curl_datas,
    ],
    hiddenimports=[
        'src',
        'src.scheduler',
        'src.scheduler.jobs',
        'src.config',
        'src.database',
        'src.database.repository',
        'src.database.models',
        'src.parsers',
        'src.parsers.farpost_parser',
        'src.telegram',
        'src.telegram.bot',
        'src.utils',
        *ctk_hiddenimports,
        *curl_hiddenimports,
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Farpost_Parser',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    icon=None,
)