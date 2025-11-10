# -*- mode: python ; coding: utf-8 -*-

"""
PyInstaller Build Specification for MR Conflict Resolver GUI
Creates a single GUI executable with all dependencies included.
"""

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect all necessary data files and hidden imports
yaml_datas = collect_data_files('yaml')
gitlab_hiddenimports = collect_submodules('gitlab')

# Common analysis settings
common_excludes = [
    'matplotlib',
    'numpy',
    'pandas',
    'scipy',
    'PIL',
    'unittest',
    'test',
    'setuptools',
]

block_cipher = None

# =============================================================================
# GUI MR Conflict Resolver (Single Executable)
# =============================================================================
gui_mr_fixer = Analysis(
    ['gui_mr_fixer.py'],
    pathex=[],
    binaries=[],
    datas=[],  # No external files - everything embedded
    hiddenimports=[
        'yaml',
        'git',
        'gitlab',
        'requests',
        'urllib3',
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'threading',
        'logging',
        'auto_fix_mr_conflicts_ndo',
        're',
        'sys',
    ] + gitlab_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas', 'scipy', 'PIL'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

gui_mr_fixer_pyz = PYZ(
    gui_mr_fixer.pure,
    gui_mr_fixer.zipped_data,
    cipher=block_cipher,
)

gui_mr_fixer_exe = EXE(
    gui_mr_fixer_pyz,
    gui_mr_fixer.scripts,
    gui_mr_fixer.binaries,
    gui_mr_fixer.zipfiles,
    gui_mr_fixer.datas,
    [],
    name='MR_Conflict_Resolver_GUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # <-- No console window for GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
