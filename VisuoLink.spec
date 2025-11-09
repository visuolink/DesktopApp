# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['Visuolink\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('Visuolink/assets', 'Visuolink/assets'), ('Visuolink/core', 'Visuolink/core'), ('Visuolink/data_model', 'Visuolink/data_model'), ('S:\\\\VS_code\\\\PROJECTS\\\\VisuoLink\\\\Frontend\\\\Desktop\\\\visuolink_kivy\\\\Lib\\\\site-packages\\\\mediapipe\\\\modules', 'mediapipe/modules'), ('Visuolink/visuolink_layout.kv', 'Visuolink'), ('data.json', '.')],
    hiddenimports=['mediapipe', 'pyautogui', 'pycaw', 'pynput', 'comtypes'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='VisuoLink',
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
    icon=['Visuolink\\assets\\visuolink.ico'],
)
