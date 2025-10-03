# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

tiktoken_datas = collect_data_files('tiktoken', includes=['*.tiktoken', '*.json'])

a = Analysis(
    ['run_gui.py'],
    pathex=[],
    binaries=[],
    datas=[('data', 'data')] + tiktoken_datas,
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtWidgets',
        'PySide6.QtGui',
        'openai',
        'whisper',
        'tiktoken',
        'typer',
        'pydantic',
        'python_dotenv',
        'rich',
        'requests',
        'sounddevice',
        'soundfile',
        'numpy',
        'torch',
        'torchaudio',
        'retention',
        'retention.gui',
        'retention.gui.windows',
        'retention.gui.components',
        'retention.gui.utils',
        'retention.asr',
        'retention.nlp',
        'retention.recording',
        'retention.validation',
        'tiktoken_ext.openai_public',
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
    name='SummitAccelerator',
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
    entitlements_file=None,
    icon=None,
)

