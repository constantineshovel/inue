# DISCLAIMER OF LIABILITY:
# This software is provided "as is", without any warranty
# The author is not responsible for any damages resulting from its use
#LICENSE:
# This file is part of INUE - INteractive and Userfriendly Emergency tool for burnt areas v. 1.1.1 'άλφα, released under the GNU Affero General Public License v3.
# See the LICENSE file or https://www.gnu.org/licenses/agpl-3.0.html for more details.
#Copyright Costantino Pala © 2025
#This file was created in the framework of a PhD funded by CNR-IRPI-PG and DSCG-UNICA
# Written by me, with coding support and suggestions from ChatGPT.


import os #useful to manage files and folders
import geopandas as gpd #vectorial data management
from shapely.geometry import box #creation of rectangular polygons
import rasterio#reading and writing of geospatial raster
import numpy as np #......
from rasterio.features import rasterize#rasterize vectors
from shapely.ops import unary_union#union of different vectors
import file_manager as manager#The armed wing of INUE
from assetios import input_shp, input_tiff, parameters#The dictionary of INUE.. Assetios stores parameters and paths
import cv2#Image elaboration (OpenCV)
import datetime#Manages time
import customtkinter as ctk#GUI library for logger
import sys#Rading and management of system parameters and settings
from PIL import Image#Image elaboration (Pillow)


#The following code creates and manages the logger.. You will find it many modules and a commented version in ndvithresholder.py :)
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

class LogWindow(ctk.CTkToplevel):
    def __init__(self, title="Log", icon_path=None, log_file_path="disconnector.log"):
        self.original_stdout = sys.stdout
        super().__init__()

        self.title(title)
        if icon_path:
            if parameters["sistema"] == 2:
                self.iconbitmap(icon_path)
            elif parameters["sistema"] == 1:
                import tkinter as tk
                icon_img = tk.PhotoImage(file=resource_path("inue256.png"))
                self.iconphoto(True, icon_img)

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


def disconnector(use_log_window=True, log_file_path=None):
    """
    Disconnector applies a correction to take into account the effects of landforms which act retaining sediment. The output raster is used to ignore this areas when using sediment connectivity indexes. 
    """
    global STUDY_AREA
    study_area_path = input_shp["STUDY_AREA"]
    global discshape
    discshape_path = input_shp["DISCSHAPE"]
    global epsg
    epsg = parameters['epsg']
    global otrs
    otrs = parameters['trs_csi']
    global res
    res = parameters['resolution']
    global output_folder
    output_folder = parameters['out_fold']

    if log_file_path is None:
        logfold = os.path.join(output_folder, 'log')
        os.makedirs(logfold, exist_ok=True)
        log_file_path = os.path.join(logfold,"INUE LOGS__Sediment Disconnector.log")

    log_window = None
    if use_log_window:
        log_window = LogWindow(title="INUE - version 1.1.1 άλφα - Sediment Disconnector module", 
                               icon_path=resource_path("inue_YQZ_icon.ico"),
                               log_file_path=log_file_path)
        log_window.update() 

    sys.stdout = LogFileWriter(log_file_path) if not use_log_window else sys.stdout

    print("====== INUE - version 1.1.1 άλφα - Sediment Disconnector Module ======")
    print(f"Session started: {datetime.datetime.now()}\n")
    log_window.update() if log_window else None
    print("Disconnector is useful to calculate the parameter needed to simulate sediment disconnection by landforms such as afforestation terraces or postfire emergency works.")
    print("Disconnector need a shapefile for study area and a shapefile with disconnected areas. Each disconnected area has its own disconnection value")
    print("Please remember that the landform shapefile must contain a field called discfactor: this is mandatory.")
    log_window.update() if log_window else None
    cumintzora = datetime.datetime.now()

    #Reading shapefiles
    study_area = gpd.read_file(study_area_path)
    discshape = gpd.read_file(discshape_path)

    print(f"Disconnector succesfully loaded shapefiles for study area perimeter and disconnection indexes.")

    #Clip the disconnection layer over the study area
    disc_clipped = gpd.overlay(discshape, study_area, how='intersection')

    print(f"Disconnected areas had been selected.")

    #Assign the 1 values to connected areas
    study_area['value'] = 1

    #Assigns a disconnection value to landforms
    disc_clipped['value'] = disc_clipped['discfactor']#This is the name of the field in the shapefile.. you can manage the DI changing the discfactor value of the landform in a GIS environment

    # Geometry union
    area_geom = unary_union(study_area.geometry)
    disc_geom_val = [(geom, value) for geom, value in zip(disc_clipped.geometry, disc_clipped['value'])]
    log_window.update() if log_window else None

    #Define raster parameters
    combined_bounds = area_geom.bounds
    width = int((combined_bounds[2] - combined_bounds[0]) / res)
    height = int((combined_bounds[3] - combined_bounds[1]) / res)
    transform = rasterio.transform.from_bounds(*combined_bounds, width=width, height=height)

    #Raster crafting
    raster_data = np.ones((height, width), dtype=np.float32)

    #Rasterize disconnected areas
    rasterize(
        disc_geom_val,
        out=raster_data,
        transform=transform,
        all_touched=True
    )

    manager.save(raster_data, 'DISCONNECTED_AREAS', res, epsg, otrs)

    output_raster = os.path.join(output_folder, "DISCONNECTED_AREAS.tif")
    log_window.update() if log_window else None

    print(f"The index map is crafted and saved to: {output_raster}")
    manager.update_assetios("DISCONNECTING_INDEX", output_raster, "tiff", "input")
    acabora = datetime.datetime.now()
    totale = acabora - cumintzora
    print(f"Total time required: {totale}")
    print("Sediment Disconnector disconnected sediment where you asked for!")
    print("See you soon!")
    if log_window:
        log_window.mainloop()
