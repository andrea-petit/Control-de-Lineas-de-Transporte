# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['control_app.py'],
    pathex=[os.path.abspath(".")],
    binaries=[],
    datas=[('dialogs', 'dialogs'), ('windows', 'windows'), ('icons', 'icons'), ('img', 'img')],
    hiddenimports=['styles', 'main_', 'app_state', 'dialogs', 'windows'], 
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Control',
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
)
