# -*- mode: python -*-

root_files = ['eplaunch/workflows/workflow_tester.py']

added_files = [
    ('eplaunch', 'eplaunch'),
]

a = Analysis(
    root_files,
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=['json'],
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
    name='EpLaunchWorkflowTester',
    debug=True,
    strip=False,
    upx=True,
    console=False
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name='EpLaunchWorkflowTester'
)
