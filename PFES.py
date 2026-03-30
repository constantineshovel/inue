# DISCLAIMER OF LIABILITY:
# This software is provided "as is", without any warranty
# The author is not responsible for any damages resulting from its use
# LICENSE:
# This file is part of INUE - INteractive and Userfriendly Emergency tool for burnt areas v. 1.1 'άλφα, released under the GNU Affero General Public License v3.
# See the LICENSE file or https://www.gnu.org/licenses/agpl-3.0.html for more details.
# Copyright Costantino Pala © 2025
# This file was created in the framework of a PhD funded by CNR-IRPI-PG and DSCG-UNICA
# Written by me, with coding support and suggestions from ChatGPT.


import numpy as np
import dask.array as da
import os
import assetios
from assetios import parameters, input_tiff, output_tiff
import file_manager as manager
from mapadore import mapper
from mapadore import font_props
import datetime
import sys
import customtkinter as ctk
from PIL import Image

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



def pfes(use_log_window=True, log_file_path=None):
    global nic
    nic = output_tiff["normalized_IC"]
    global dnbr
    dnbr = output_tiff["dNBR"]
    global otrs
    otrs = manager.open_array(nic)[2]
    global epsg
    epsg = parameters["epsg"]
    global resolution
    resolution = parameters["resolution"]
    global output_folder
    output_folder = parameters['out_fold']

    # Open the files as array
    global nicar
    nicar = manager.open_array(nic)[1]
    global dnbar
    dnbar = manager.open_array(dnbr)[1]
    dnbrnorm = (dnbar - np.nanmin(dnbar)) / (np.nanmax(dnbar) - np.nanmin(dnbar))
    dnbn = os.path.join(output_folder, 'dnbr normalized.tif')
    manager.save(dnbrnorm, dnbn, resolution, epsg, otrs)
    global optional
    optional = input_tiff["Custom_Variable"]
    optar = manager.open_array(optional)[1]

    # Here checks for switchers and import needed variables
    global config
    config = parameters["Area Configuration"]  # Postfire/Vegetation Recovering
    global DL
    DL = parameters["Disconnecting Landforms"]  # No/Yes

    optcheck = input_tiff["Custom_Variable"]


    def pfes2(nicar, dnbrnorm, resolution, epsg, otrs, config, DL, output_folder, use_log_window=True, log_file_path=None):
        # Se non è specificato un percorso, usa quello predefinito nella cartella output
        # Se non è specificato un percorso, usa quello predefinito nella cartella output
        if log_file_path is None:
            logfold = os.path.join(output_folder, 'log')
            os.makedirs(logfold, exist_ok=True)
            log_file_path = os.path.join(logfold, "INUE LOGS__PFES Map Crafter.log")

        log_window = None
        if use_log_window:
            log_window = LogWindow(title="INUE - version 1.1 άλφα - PFES Map Crafter", 
                                   icon_path=resource_path("inue_YQZ_icon.ico"),
                                   log_file_path=log_file_path)
            log_window.update()  # Mantiene attiva la finestra durante i calcoli

        # Reindirizza i print sia al file di log che alla finestra (se attiva)
        sys.stdout = LogFileWriter(log_file_path) if not use_log_window else sys.stdout
        print("====== INUE - version 1.1 άλφα - Postfire Erosion Susceptibility Map Crafter======")
        print("This module is useful to craft a raster map which assesses the posftire erosion susceptibility based on the settings you provided.")
        log_window.update() if log_window else None
        print(f"Session started: {datetime.datetime.now()}\n")
        cumintzora = datetime.datetime.now()
        if config == "Postfire" and DL == "No":
            print(f"The area was recently burnt and there are no disconnecting landforms")
            log_window.update() if log_window else None
            pfestif, pfesar = manager.array_calculator(nicar, dnbrnorm, 'times', resolution, epsg, otrs, 'PFES')
            manager.update_assetios('PFES', pfestif, 'tiff', 'output')
            mapper(pfestif, 'Postfire Erosion Susceptibility map', 'turbo', 'linear', font_props)#mapper(pfestif, 'Postfire Erosion Susceptibility map', 'turbo', 'linear', font_props, value_to_label1)
            print(f"Postfire Erosion Susceptibility Map crafted")
        
        elif config == "Postfire" and DL == "Yes":
            print(f"The area was recently burnt and disconnecting landforms exist")
            log_window.update() if log_window else None
            DI = input_tiff["DISCONNECTING_INDEX"]
            diar = manager.open_array(DI)[1]
            pfestif, pfesar = manager.array_calculator(nicar, dnbrnorm, 'times', resolution, epsg, otrs, 'PFES')
            pfesdar = manager.array_calculator(pfesar, diar, 'division', resolution, epsg, otrs, 'PFES disconnected')[1]
            dpfestif = os.path.join(output_folder, 'PFES disconnected.tif')
            mapper(dpfestif, 'Postfire Erosion Susceptibility map', 'turbo', 'linear', font_props)
            manager.update_assetios('DPFES', dpfestif, 'tiff', 'output')
            print(f"Postfire Erosion Susceptibility Map crafted considering disconnecting landform")

        elif config == "Vegetation recovering" and DL == "No":
            print(f"Vegetation is recovering, there are no disconnecting landforms")
            log_window.update() if log_window else None
            VRf1 = output_tiff["VRf"]
            DI = input_tiff["DISCONNECTING_INDEX"]
            vrfar = manager.open_array(VRf1)[1]
            pfestif, pfesar = manager.array_calculator(nicar, dnbrnorm, 'times', resolution, epsg, otrs, 'PFES')
            pfesar = manager.array_calculator(pfesar, vrfar, 'times', resolution, epsg, otrs, 'PFES vegetation recovery')[1]
            pfesvrt = os.path.join(output_folder, 'PFES vegetation recovery.tif')
            mapper(pfesvrt, 'Postfire Erosion Susceptibility map', 'turbo', 'linear', font_props)
            manager.update_assetios('PFESVRT', pfesvrt, 'tiff', 'output')
            print(f"Postfire Erosion Susceptibility Map crafted considering vegetation recovering")
        
        elif config == "Vegetation recovering" and DL == "Yes":
            print(f"Vegetation is recovering and disconnecting landforms exist")
            log_window.update() if log_window else None
            DI1 = input_tiff["DISCONNECTING_INDEX"]
            diar = manager.open_array(DI1)[1]
            VRf = output_tiff["VRf"]
            vrfar = manager.open_array(VRf)[1]
            pfestif, pfesar = manager.array_calculator(nicar, dnbrnorm, 'times', resolution, epsg, otrs, 'PFES')
            pfesdar = manager.array_calculator(pfesar, diar, 'division', resolution, epsg, otrs)
            pfesdivrfar = manager.array_calculator(pfesdar, vrfar, 'times', resolution, epsg, otrs, 'PFES disconnected vegetation recovery')
            pdvrftif = os.path.join(output_folder, 'PFES disconnected vegetation recovery.tif')
            mapper(pdvrftif, 'Postfire Erosion Susceptibility map', 'turbo', 'linear', font_props)
            manager.update_assetios('PFESDVRT', pdvrftif, 'tiff', 'output')
            print(f"Postfire Erosion Susceptibility Map crafted considering vegetation recovering and disconnecting landforms")
        acabora = datetime.datetime.now()
        totale = acabora - cumintzora
        print(f"Total time required: {totale}")
        print("INUE finished its work! If you want to compute the effects of local variables please use the Custom Variables Applier.")
        print("Thank you for using INUE. I personally hope it will be useful to manage and/or study the area.")
        print("See you soon!")
        log_window.update() if log_window else None
        if log_window:
            log_window.mainloop()  # Ora la finestra è già aperta, quindi non ritarda i calcoli



            
    pfes2(nicar, dnbrnorm, resolution, epsg, otrs, config, DL, output_folder)

