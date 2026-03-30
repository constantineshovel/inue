# -*- mode: python ; coding: utf-8 -*-

import sys
sys.setrecursionlimit(sys.getrecursionlimit() * 5)


a = Analysis(
    ['INUE.py'],
    pathex=[],
    binaries=[],
    datas=[('inue_YQZ_icon.ico', '.'), ('inue.png', '.'), ('C:\\Users\\Constantine\\AppData\\Roaming\\Python\\Python313\\site-packages\\fiona', 'fiona'), ('C:\\Users\\Constantine\\AppData\\Roaming\\Python\\Python313\\site-packages\\fiona.libs', 'fiona.libs'), ('C:\\Users\\Constantine\\AppData\\Roaming\\Python\\Python313\\site-packages\\fiona-1.10.1.dist-info', 'fiona-1.10.1.dist-info'), ('C:\\Users\\Constantine\\AppData\\Roaming\\Python\\Python313\\site-packages\\rasterio', 'rasterio'), ('C:\\Users\\Constantine\\AppData\\Roaming\\Python\\Python313\\site-packages\\rasterio.libs', 'rasterio.libs'), ('C:\\Users\\Constantine\\AppData\\Roaming\\Python\\Python313\\site-packages\\rasterio-1.4.3.dist-info', 'rasterio-1.4.3.dist-info'), ('C:\\Users\\Constantine\\AppData\\Roaming\\Python\\Python313\\site-packages\\geopandas', 'geopandas'), ('C:\\Users\\Constantine\\AppData\\Roaming\\Python\\Python313\\site-packages\\geopandas-1.0.1.dist-info', 'geopandas-1.0.1.dist-info'), ('C:\\Users\\Constantine\\AppData\\Roaming\\Python\\Python313\\site-packages\\pyogrio', 'pyogrio'), ('C:\\Users\\Constantine\\AppData\\Roaming\\Python\\Python313\\site-packages\\pyogrio.libs', 'pyogrio.libs'), ('C:\\Users\\Constantine\\AppData\\Roaming\\Python\\Python313\\site-packages\\pyogrio-0.11.0.dist-info', 'pyogrio-0.11.0.dist-info'), ('C:\\Users\\Constantine\\AppData\\Roaming\\Python\\Python313\\site-packages\\pyproj', 'pyproj'), ('C:\\Users\\Constantine\\AppData\\Roaming\\Python\\Python313\\site-packages\\pyproj.libs', 'pyproj.libs'), ('C:\\Users\\Constantine\\AppData\\Roaming\\Python\\Python313\\site-packages\\pyproj-3.7.1.dist-info', 'pyproj-3.7.1.dist-info'), ('C:\\Users\\Constantine\\AppData\\Roaming\\Python\\Python313\\site-packages\\affine', 'affine'), ('C:\\Users\\Constantine\\AppData\\Roaming\\Python\\Python313\\site-packages\\affine-2.4.0.dist-info', 'affine-2.4.0.dist-info')],
    hiddenimports=['file_manager', 'customtkinter', 'geopandas', 'shapely', 'rasterio', 'psutil', 'opencv-python', 'dask', 'dask.array', 'dask_image', 'dask_image.ndfilters', 'scipy', 'fiona', 'pyogrio', 'rasterio.sample', 'rasterio.vrt', 'rasterio.warp', 'matplotlib.colors', 'matplotlib.font_manager', 'numpy', 'matplotlib.pyplot', 'requests', 'assetios', 'assetios.input_tiff', 'assetios.output_tiff', 'assetios.parameters', 'rasterio.transform', 'rasterio.plot', 'matplotlib.colors.Normalize'],
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
    name='INUE',
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
    icon=['inue_YQZ_icon.ico'],
)
