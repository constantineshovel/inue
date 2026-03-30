# DISCLAIMER OF LIABILITY:
# This software is provided "as is", without any warranty
# The author is not responsible for any damages resulting from its use
#LICENSE:
# This file is part of INUE - INteractive and Userfriendly Emergency tool for burnt areas v. 1.1 'άλφα, released under the GNU Affero General Public License v3.
# See the LICENSE file or https://www.gnu.org/licenses/agpl-3.0.html for more details.
#Copyright Costantino Pala © 2025
#This file was created in the framework of a PhD funded by CNR-IRPI-PG and DSCG-UNICA

import numpy as np
import dask.array as da
import os
import assetios
from assetios import parameters, input_tiff, output_tiff
import file_manager as manager
import datetime
import customtkinter as ctk
import sys
from PIL import Image
from mapadore import mapper
from mapadore import font_props

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


def scc(use_log_window=True, log_file_path=None):
    cumintzora = datetime.datetime.now()


    global epsg
    epsg = parameters["epsg"]
    global resolution
    resolution = parameters["resolution"]
    global output_folder
    output_folder = parameters['out_fold']
    global optional
    optional = input_tiff["Custom_Variable"]
    optar = manager.open_array(optional)[1]
    global otrs
    otrs =  manager.open_array(optional)[2]

    # Here checks for switchers and import needed variables
    global config
    config = parameters["Area Configuration"]  # Postfire/Vegetation Recovering
    global DL
    DL = parameters["Disconnecting Landforms"]  # No/Yes

    opt = input_tiff["Custom_Variable"]
    optar = manager.open_array(opt)[1]
    output_folder = parameters['out_fold']  

    if log_file_path is None:
        logfold = os.path.join(output_folder, 'log')
        os.makedirs(logfold, exist_ok=True)
        log_file_path = os.path.join(logfold, "INUE LOGS__Local Variable Applier.log")

    log_window = None
    if use_log_window:
        log_window = LogWindow(title="INUE - version 1.1 άλφα Local Variable Applier Module", 
                               icon_path=resource_path("inue_YQZ_icon.ico"),
                               log_file_path=log_file_path)
        log_window.update()  


    sys.stdout = LogFileWriter(log_file_path) if not use_log_window else sys.stdout

    print("====== INUE - version 1.1 άλφα - Local Variable Applier Module ======")
    print(f"Session started: {datetime.datetime.now()}\n")
    log_window.update() if log_window else None

    print("Welcome to the Custom Variable Applier. This module allows you to customize the PFES map with additional parameters.")
    print("PFES customization is performed by multiplying the PFES map by the custom variable you provided.")
    print("Loading input files and settings...")
    print("Input files must be prepared on a different software and should have same extent and resolution.")
    print("You can assure input files have same resolution and extent with Crop and Resample tools available in Preliminary Operations")

    optname = os.path.splitext(os.path.basename(optional))[0]#This expression extract the Custom Variable Name
    print("Settings and files had been loaded. INUE will apply your variable now")
    log_window.update() if log_window else None

    if config == "Postfire" and DL == "No":
        print("The area was burned recently and disconnecting landforms are not detected")
        pfes = output_tiff["PFES"]
        pfesar = manager.open_array(pfes)[1]
        name = 'PFES customized with' + f'{optname}'
        pfeslv, pfeslvar = manager.array_calculator(pfesar, optar, 'times', resolution, epsg, otrs, f'{name}')
        pfcvtif = os.path.join(output_folder, f'{name}.tif')
        mapper(pfcvtif, f'Postfire Erosion Susceptibility map with {optname}', 'turbo', 'linear', font_props)
        npfes = (pfeslvar - np.nanmin(pfeslvar))/(np.nanmax(pfeslvar)-np.nanmin(pfeslvar))
        manager.save(npfes, f'Normalized PFES with {optname}', resolution, epsg, otrs)
        norm = os.path.join(output_folder, f'Normalized PFES custimized with {optname}.tif')
        mapper(norm, f'Normalized Postfire Erosion Susceptibility map customized with {optname}', 'turbo', 'linear', font_props)
        acabora = datetime.datetime.now()
        totale = acabora-cumintzora
        print(f"Total time required: {totale}")
        print(f"Custom Variable {optname} applied. See you soon!")
        log_window.update() if log_window else None
        
    elif config == "Postfire" and DL == "Yes":
        print("The area was burned recently and disconnecting landforms are detected")
        pfes = output_tiff["DPFES"]
        pfesar = manager.open_array(pfes)[1]
        name = f'PFES Disconnected customized with {optname}'
        pfeslv, pfeslvar = manager.array_calculator(pfesar, optar, 'times', resolution, epsg, otrs, f'{name}')
        pfcvtif = os.path.join(output_folder, f'{name}.tif')
        mapper(pfcvtif, f'Postfire Erosion Susceptibility map customized with {optname}', 'turbo', 'linear', font_props)
        npfes = (pfeslvar - np.nanmin(pfeslvar))/(np.nanmax(pfeslvar)-np.nanmin(pfeslvar))
        manager.save(npfes, f'Normalized PFES customized with {optname}', resolution, epsg, otrs)
        norm = os.path.join(output_folder, f'Normalized PFES customized with {optname}.tif')
        mapper(norm, f'Normalized Postfire Erosion Susceptibility customized with {optname}', 'turbo', 'linear', font_props)
        log_window.update() if log_window else None
        acabora = datetime.datetime.now()
        totale = acabora-cumintzora
        print(f"Total time required: {totale}")
        print(f"Custom Variable {optname} applied. See you soon!")


    elif config == "Vegetation recovering" and DL == "No":
        print("Vegetation is recovering and disconnecting landforms are not detected")
        pfes = output_tiff["PFESVRT"]
        pfesar = manager.open_array(pfes)[1]
        name = f'PFES Vegetation Recovery customized with {optname}'
        pfeslv, pfeslvar = manager.array_calculator(pfesar, optar, 'times', resolution, epsg, otrs, f'{name}')
        pfcvtif = os.path.join(output_folder, 'f{name}.tif')
        mapper(pfcvtif, f'Postfire Erosion Susceptibility map customized with {optname}', 'turbo', 'linear', font_props)
        npfes = (pfeslvar - np.nanmin(pfeslvar))/(np.nanmax(pfeslvar)-np.nanmin(pfeslvar))
        manager.save(npfes, f'Normalized PFES customized with {optname}', resolution, epsg, otrs)
        norm = os.path.join(output_folder, f'Normalized PFES customized with {optname}.tif')
        mapper(norm, f'Normalized Postfire Erosion Susceptibility customized with {optname}', 'turbo', 'linear', font_props)
        log_window.update() if log_window else None
        acabora = datetime.datetime.now()
        totale = acabora-cumintzora
        print(f"Total time required: {totale}")
        print(f"Custom Variable {optname} applied. See you soon!")
    
    elif config == "Vegetation recovering" and DL == "Yes":
        print("Vegetation is recovering and disconnecting landforms are detected")
        pfes = output_tiff["PFESDVRT"]
        pfesar = manager.open_array(pfes)[1]
        name = f'PFES Vegetation Recovery disconnected customized witj {optname}'
        pfeslv, pfeslvar = manager.array_calculator(pfesar, optar, 'times', resolution, epsg, otrs, f'{name}')
        pfcvtif = os.path.join(output_folder, f'{name}.tif')
        mapper(pfcvtif, f'Postfire Erosion Susceptibility map customized with {optname}', 'turbo', 'linear', font_props)
        npfes = (pfeslvar - np.nanmin(pfeslvar))/(np.nanmax(pfeslvar)-np.nanmin(pfeslvar))
        manager.save(npfes, f'Normalized PFES customized with {optname}', resolution, epsg, otrs)
        norm = os.path.join(output_folder, f'Normalized PFES customized with {optname}.tif')
        mapper(norm, f'Normalized Postfire Erosion Susceptibility map customized with {optname}', 'turbo', 'linear', font_props)
        log_window.update() if log_window else None
        acabora = datetime.datetime.now()
        totale = acabora-cumintzora
        print(f"Total time required: {totale}")
        print(f"Custom Variable {optname} applied. See you soon!")
    if log_window:
        log_window.mainloop() 
