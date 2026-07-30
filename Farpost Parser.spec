import os

from PyInstaller.utils.hooks import collect_all

block_cipher = None

ctk_datas, ctk_binaries, ctk_hiddenimports = collect_all('customtkinter')

curl_datas, curl_binaries, curl_hiddenimports = collect_all('curl_cffi')
pydantic_datas, pydantic_binaries, pydantic_hiddenimports = collect_all('pydantic')
pydantic_settings_datas, pydantic_settings_binaries, pydantic_settings_hiddenimports = collect_all('pydantic_settings')

a = Analysis(

    ['gui.py'],

    pathex=['.'],

    binaries=ctk_binaries + curl_binaries + pydantic_binaries + pydantic_settings_binaries,

    datas=[

        ('src', 'src'),                                                

        *ctk_datas,

        *curl_datas,

        *pydantic_datas,

        *pydantic_settings_datas,

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

        *pydantic_hiddenimports,

        *pydantic_settings_hiddenimports,

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
