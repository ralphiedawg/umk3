# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, collect_submodules


mediapipe_package = "mediapipe.tasks.c"

a = Analysis(
    ["src/tray/GenericTray.py"],
    pathex=["."],
    binaries=collect_dynamic_libs(mediapipe_package),
    datas=[
        ("config", "config"),
        ("src/tray/icons", "src/tray/icons"),
        ("hand_landmarker.task", "."),
        *collect_data_files(mediapipe_package),
    ],
    hiddenimports=[
        mediapipe_package,
        *collect_submodules("winsdk"),
    ],
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
    name="UMK",
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
)
