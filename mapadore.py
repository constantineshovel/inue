# DISCLAIMER OF LIABILITY:
# This software is provided "as is", without any warranty
# The author is not responsible for any damages resulting from its use
# LICENSE:
# This file is part of INUE - INteractive and Userfriendly Emergency tool for burnt areas v. 1.1'άλφα, released under the GNU Affero General Public License v3.
# See the LICENSE file or https://www.gnu.org/licenses/agpl-3.0.html for more details.
# Copyright Costantino Pala © 2025
# This file was created in the framework of a PhD funded by CNR-IRPI-PG and DSCG-UNICA
# This module was entirely written by ChatGPT, based on a human idea and guidance.
# Thanks a lot, ChatGPT :)

import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.font_manager import FontProperties
import numpy as np
import geopandas as gpd
import os
import numpy as np
import matplotlib.pyplot as plt
from rasterio.plot import show
from matplotlib import font_manager
import requests
from assetios import input_tiff, output_tiff, parameters
from rasterio.transform import array_bounds
from rasterio.plot import show
from rasterio.warp import transform_bounds
from matplotlib.colors import Normalize
import matplotlib.patches as mpatches


# Function to save fonts temporarily
def save_font_temp(url):
    response = requests.get(url, timeout=5)
    font_path = os.path.join(os.getcwd(), "temp_font.ttf")
    with open(font_path, 'wb') as f:
        f.write(response.content)
    return font_path

# Try to load fonts from internet
fonts_urls = {
    'normal': 'https://github.com/googlefonts/opensans/blob/main/fonts/ttf/OpenSans-Regular.ttf?raw=true',
    'bold_italic': 'https://github.com/googlefonts/opensans/blob/main/fonts/ttf/OpenSans-BoldItalic.ttf?raw=true',
    'italic': 'https://github.com/googlefonts/opensans/blob/main/fonts/ttf/OpenSans-Italic.ttf?raw=true'
}

try:
    font_paths = [save_font_temp(url) for url in fonts_urls.values()]
    for path in font_paths:
        font_manager.fontManager.addfont(path)

    plt.rcParams['font.family'] = 'Open Sans'
    print("Open Sans loaded successfully.")

except Exception as e:
    # Fallback: use system default (TkDefaultFont or customtkinter defaults)
    print("Could not load custom fonts, falling back to default. Reason:", str(e))

#Font properties
opensans_bold_italic = FontProperties(family='Open Sans', style='italic', weight='bold', size=15)
opensans_italic = FontProperties(family='Open Sans', style='italic', size=12)
opensans_bold_italic_legend = FontProperties(family='Open Sans', style='italic', weight='bold', size=13)
opensans_normal = FontProperties(family='Open Sans', size=12)

#Function to plot the raster to 4326 epsg
def convert_to_4326(input_tif, output_tif):
    with rasterio.open(input_tif) as src:
        transform, width, height = calculate_default_transform(
            src.crs, 'EPSG:4326', src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': 'EPSG:4326',
            'transform': transform,
            'width': width,
            'height': height
        })

        with rasterio.open(output_tif, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs='EPSG:4326',
                    resampling=Resampling.nearest)

#Function for map handling
def mapper(tif_path, title, color_gradient, scale_type='linear', font_props=None, value_to_label=None):
    output_folder = parameters['out_fold']
    mapout = os.path.join(output_folder, 'maps')
    os.makedirs(mapout, exist_ok=True)
    output_tif = tif_path.replace('.tif', '_4326.tif')
    convert_to_4326(tif_path, output_tif)

    with rasterio.open(output_tif) as src:
        data = src.read(1)
        data = np.where(data == src.nodata, np.nan, data)
        bounds = src.bounds

    fig, ax = plt.subplots(figsize=(10, 8))

    #Raster classification
    if value_to_label:
        num_classes = len(value_to_label)
        cmap = ListedColormap(plt.get_cmap(color_gradient, num_classes).colors)
        norm = BoundaryNorm(list(value_to_label.keys()) + [max(value_to_label.keys()) + 1], cmap.N)
    else:
        cmap = plt.get_cmap(color_gradient)
        if scale_type == 'quantile':
            quantiles = np.nanpercentile(data, [0, 25, 50, 75, 100])
            norm = BoundaryNorm(quantiles, cmap.N)
        else:
            norm = Normalize(vmin=np.nanmin(data), vmax=np.nanmax(data))

    #Map plotter
    img = ax.imshow(data, cmap=cmap, norm=norm, extent=[bounds.left, bounds.right, bounds.bottom, bounds.top])
    ax.set_title(title, fontproperties=font_props['bold_italic'], pad=20)

    #Add coordinates
    ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True,
                   right=False, top=False, labelright=False, labeltop=False)

    if value_to_label:
        patches = [mpatches.Patch(color=cmap(norm(v)), label=label) for v, label in value_to_label.items()]
    
        #Creating a legend, outside of the map area
        leg = ax.legend(handles=patches, title="Legend", loc='center left', 
                        bbox_to_anchor=(1.02, 0.5), borderaxespad=0., prop=font_props['bold_italic_legend'])

        #removes the legend border
        leg.get_frame().set_linewidth(0)
    else:
        cbar = plt.colorbar(img, ax=ax, orientation='vertical', fraction=0.046, pad=0.04)
        cbar.ax.tick_params(labelsize=10)

    plt.tight_layout()
    plt.savefig(f'{mapout}/{title}.png', dpi=300)
    plt.close()


#example
font_props = {
    'bold_italic': FontProperties(family='Open Sans', style='italic', weight='bold', size=15),
    'italic': FontProperties(family='Open Sans', style='italic', size=12),
    'bold_italic_legend': FontProperties(family='Open Sans', style='italic', weight='bold', size=13),
    'normal': FontProperties(family='Open Sans', size=12)
}

# create_map('path_to_raster.tif', 'Mappa Esempio', 'viridis', scale_type='quantile', value_to_label=value_to_label, font_props=font_props)
