# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files

a = Analysis(
    ['src/tray/GenericTray.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('config', 'config'),
        ('icons', 'icons'),
        ('hand_landmarker.task', '.'),
        *collect_data_files('mediapipe.tasks.c'),
    ],
    hiddenimports=['mediapipe.tasks.c'],
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
    [],
    exclude_binaries=True,
    name='UMK',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icons/UMK64.png'],  # <-- Updated path
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='UMK',
)
app = BUNDLE(
    coll,
    name='UMK.app',
    icon='icons/UMK64.png',  # <-- Updated path
    bundle_identifier='com.umk.app',
    info_plist={
        'NSLocalNetworkUsageDescription': 'UMK requires access to the local network to discover and communicate with LAN devices.',
        'NSCameraUsageDescription': 'Server-side gesture detection is camera-based',
        'NSBonjourServices': ['_umk._tcp'],
        'NSHighResolutionCapable': 'True',
    },
)
