# DISCLAIMER OF LIABILITY:
# This software is provided "as is", without any warranty.
# This module is part of INUE - version 1.1 "άλφα"
# The author is not responsible for any damages resulting from its use.
# See the LICENSE file for more details.
# Copyright Costantino Pala © 2025
# Developed with the support of ChatGPT between November 2024 and March 2025.
# Written by me, with coding support and suggestions from ChatGPT.


import os
import geopandas as gpd
from tkinter import Tk, filedialog
from shapely.geometry import box
import rasterio
import numpy as np
from rasterio.features import rasterize
from shapely.ops import unary_union
import file_manager as manager
from assetios import input_shp, input_tiff, parameters
from scipy.ndimage import zoom
import cv2
import datetime
import customtkinter as ctk
import sys
from PIL import Image
from file_manager import calculate_chunk_size
import dask.array as da
import rioxarray
from rasterio.enums import Resampling
import xarray as xr

def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class PrintRedirector:
    def __init__(self, text_widget, log_file_path):
        self.text_widget = text_widget
        self.log_file_path = log_file_path 

    def write(self, message):
        self.text_widget.configure(state="normal")
        self.text_widget.insert("end", message)
        self.text_widget.see("end")
        self.text_widget.configure(state="disabled")
        write_to_log(message, self.log_file_path) 

    def flush(self):
        pass

class LogFileWriter:
    def __init__(self, log_file_path):
        self.log_file_path = log_file_path

    def write(self, message):
        write_to_log(message, self.log_file_path)

    def flush(self):
        pass

def write_to_log(message, log_file_path):
    with open(log_file_path, "a", encoding="utf-8") as log_file:
        log_file.write(message)

class LogWindow(ctk.CTk):
    def __init__(self, title="Log", icon_path=None, log_file_path="disconnector.log"):
        self.original_stdout = sys.stdout
        super().__init__()

        self.title(title)
        if icon_path:
            self.iconbitmap(icon_path)

        self.geometry("800x600")
        self.resizable(True, True)

        self.text_area = ctk.CTkTextbox(self, wrap="word", state="disabled", font=("Open Sans", 12))
        self.text_area.pack(expand=True, fill="both", padx=10, pady=10)

        sys.stdout = PrintRedirector(self.text_area, log_file_path)  

        self.protocol("WM_DELETE_WINDOW", self.on_close)  

    def on_close(self):
            if hasattr(self, "original_stdout"):  
                sys.stdout = self.original_stdout  
            self.destroy()



def roadmask(use_log_window=True, log_file_path=None):
    cumintzora = datetime.datetime.now()
    global STUDY_AREA
    study_area_path = input_shp["STUDY_AREA"]
    global ROADS
    roads_path = input_shp["ROADS"]
    global epsg
    epsg = parameters['epsg']
    global otrs
    otrs = parameters['trs_csi']
    global res
    res = parameters['resolution']
    global output_folder
    output_folder = parameters['out_fold']
    

    #If the path is not specified uses the one available in the output folder
    if log_file_path is None:
        logfold = os.path.join(output_folder, 'log')
        os.makedirs(logfold, exist_ok=True)
        log_file_path = os.path.join(logfold, "INUE LOGS__DEMROAD Crafter.log")

    log_window = None
    if use_log_window:
        log_window = LogWindow(title="INUE - version 1.1 άλφα DEMROAD and ROADMASK Crafter", 
                               icon_path=resource_path("inue_YQZ_icon.ico"),
                               log_file_path=log_file_path)
        log_window.update()  #Keeps the window open while calculating

    #Sends the print messages to the log files and to the popup
    sys.stdout = LogFileWriter(log_file_path) if not use_log_window else sys.stdout

    print("====== INUE - version 1.1 άλφα - DEMROAD crafter ======")
    print(f"Session started: {datetime.datetime.now()}\n")
    log_window.update() if log_window else None
    print("This module calculates DEMROAD. DEMROAD is an input parameter for Sediment Connector. Before calculating load a shapefile containing a polygon delimitating Study Area (MASK) and a shapefile for ROADS")
    print("Study Area shapefile must contain a regular polygon with study area perimeter. Either shapefiles must be in the same EPSG")
    print("This module allows to simulate the effects of roads on sediment connectivity: it is a fork to use ROADMASK in TAUDEM (Take a look to the GIS procedure proposed by Borselli et al. 2008)")
    print("ROADMASK raster is also calculated for use on ESRI ArcGIS Pro environment. You will find it in the output folder as ROADMASK.tif")
    print("Please note that the effects of demroad are effective on high resolution DEM. If you prefer to not use it, switch off DEMROAD with the dedicated switcher")
    log_window.update() if log_window else None
    """
    roadmask calculates the roadmask layer useful for the calculation of IC. It simply crosses a polygon representing study area with a shapefile for roads. Both files need to be referenced in the
    same SR (same EPSG).
    """


    #reads the shapefiles using geopandas
    study_area = gpd.read_file(study_area_path)
    roads = gpd.read_file(roads_path)

    print(f"Study area and roads are successfully loaded in the roadmask crafter")

    #crops the road shapefile using the extent of the study area. all the roads placed outside will be discarded
    roads_clipped = gpd.overlay(roads, study_area, how='intersection')

    print(f"The roads inside the study area are succesfully selected")
    log_window.update() if log_window else None

    #Assigns 1 value to the areas which are not roads (max connection)
    study_area['value'] = 1

    #Assigns the 0 values to roads (min connection)
    roads_clipped['value'] = 0

    #Crafts a new shapefile which combines the roads and outer areas
    area_geom = unary_union(study_area.geometry)
    roads_geom = unary_union(roads_clipped.geometry)
    log_window.update() if log_window else None

    print(f"DEMROAD crafter assigned 0 to roads and 1 to outer areas.")

    # Creates a bounding box and defines the final resolution
    combined_bounds = area_geom.bounds
    resolution = 1  
    width = int((combined_bounds[2] - combined_bounds[0]) / resolution)
    height = int((combined_bounds[3] - combined_bounds[1]) / resolution)
    transform = rasterio.transform.from_bounds(*combined_bounds, width=width, height=height)

    #Craftes the empty raster and assignes the value 1 to all the area
    raster_data = np.ones((height, width), dtype=np.uint8) * 1

    #roads = 0
    rasterize(
        [(roads_geom, 0)],
        out=raster_data,
        transform=transform,
        all_touched=True
    )

    #output path
    rmsk = os.path.join(output_folder, "ROADMASK.tif")

    #Crafts the final raster
    with rasterio.open(
        rmsk,
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=1,
        dtype=raster_data.dtype,
        crs=study_area.crs,
        transform=transform,
    ) as dst:
        dst.write(raster_data, 1)

    print(f"ROADMASK.tif is succesfully crafted and saved in: {rmsk}")
    ROADMASK = rmsk
    log_window.update() if log_window else None
    manager.update_assetios("roadmask", rmsk, "tiff", "input")#loads the file path to the dictionary of input_tiffs for further use in the app
    global dem
    dem = input_tiff['DEM']
    global roadmask
    roadmask = input_tiff['roadmask']


    chdx, chsx = calculate_chunk_size(dtype=np.float32, target_memory_fraction=0.5, max_chunk_size=1000)

    #Opens the roadmask file as a dask array
    roadar = rioxarray.open_rasterio(roadmask, chunks=(1, chdx, chsx)).squeeze()
    demar = rioxarray.open_rasterio(dem, chunks=(1, chdx, chsx)).squeeze()

    #Resamples the file using dask 
    roadar_resampled = roadar.rio.reproject_match(demar, resampling=Resampling.bilinear)

    #The following expressions calculate DEMROAD without loading all the info in RAM
    demroad = da.where(roadar_resampled == 0, demar - 0.10, demar)
    demroad_xr = xr.DataArray(
    demroad, 
    dims=("y", "x"),  
    coords={"y": demar.y, "x": demar.x},  #Mantains spatial coordinates
    attrs=demar.attrs  #Mantains metadata
    )

    #Assigns the CRS
    demroad_xr.rio.write_crs(demar.rio.crs, inplace=True)

    #saves the file
    demroad_xr.rio.to_raster(os.path.join(output_folder, 'demroad.tif'))

    #and writes the path to be used to update dictionaries
    dpath = os.path.join(output_folder, 'demroad.tif')

    manager.update_assetios('DEMROAD', dpath, 'tiff', 'input')
    acabora = datetime.datetime.now()
    totale = acabora - cumintzora
    print(f"Total time required: {totale}")
    print(f"ROADS are succesfully added to dem. The new DEM is loaded to be used so, you can run sediment connector now!")
    if log_window:
        log_window.mainloop()  #keeps the window open while upgrading

    
