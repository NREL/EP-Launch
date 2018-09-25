# -*- mode: python -*-

root_files = ['eplaunch/runner.py']

added_files = [
    ('eplaunch', 'eplaunch'),
]

a = Analysis(
    root_files,
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None
)

pyz = PYZ(
    a.pure, a.zipped_data,
    cipher=None
)

exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name='EP_Launch',
    debug=False,
    strip=False,
    upx=True,
    console=False,
    icon='eplaunch/interface/main_icon.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name='EPLaunch'
)

app = BUNDLE(
    coll,
    name='eplaunch.app',
    icon=None,
    bundle_identifier=None
)
