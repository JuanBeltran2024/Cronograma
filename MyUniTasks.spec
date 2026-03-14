# -*- mode: python ; coding: utf-8 -*-
import os

project_dir = os.path.abspath('.')
ctk_path = r'C:\Users\juanm\Desktop\Yo\Cronograma\venv\Lib\site-packages\customtkinter'

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[project_dir],
    binaries=[],
    datas=[
        ('stitch_logo.png', '.'),
        ('stitch_icon.ico', '.'),
        ('database.py', '.'),
        (ctk_path, 'customtkinter/'),
    ],
    hiddenimports=[
        'customtkinter',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'tkcalendar',
        'babel.numbers',
        'colorsys',
        'sqlite3',
    ],
    hookspath=[],
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
    [],
    exclude_binaries=True,
    name='MyUniTasks',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='stitch_icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MyUniTasks',
)
