from pathlib import Path

a = Analysis(
    ['main.py'],
    pathex=[
        Path('src').absolute().__str__()
    ],
    datas=[
        (Path('lib\libssl-3-x64.dll').absolute().__str__(), '.'),
        (Path('lib\libcrypto-3-x64.dll').absolute().__str__(), '.'),
    ],
    hiddenimports=[
        'ssl',
    ]
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name='main',
    console=True
)
