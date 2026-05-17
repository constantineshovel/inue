# DISCLAIMER OF LIABILITY:
# This software is provided "as is", without any warranty
# The author is not responsible for any damages resulting from its use
#LICENSE:
# This file is part of INUE - INteractive and Userfriendly Emergency tool for burnt areas v. 1.1.1 'άλφα, released under the GNU Affero General Public License v3.
# See the LICENSE file or https://www.gnu.org/licenses/agpl-3.0.html for more details.
#Copyright Costantino Pala © 2026
#This file was created in the framework of a PhD funded by CNR-IRPI-PG and DSCG-UNICA


from assetios import input_tiff, output_tiff, parameters
import os
import datetime
import numpy as np
import scipy as sp
import dask.array as da
import file_manager as manager
from mapadore import mapper
from mapadore import font_props
import customtkinter as ctk
import sys
from PIL import Image

#LOGGER: opens a popup and saves its messages as a log file
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

#LOGGER end

def fogu(use_log_window=True, log_file_path=None):
    """
    Burnt Area Analyzer allows to use Sentinel 2 L2A images for burnt scar analysis. Fogu performs an analysis which calculates prefire and postfire NBRs, calculates the dNBR, Burn Severity and Wildfire perimeter.
    Between the outputs also a special Burn Severity is calculated: this burn severity file is useful to draft the PostFire Erosion Susceptibility map, since is one of the two mandatory inputs (other one is the
    normalized IC).
    """
    output_folder = parameters['out_fold']  #defines the output

    #If the log folder does not exist the following expression creates it
    if log_file_path is None:
        logfold = os.path.join(output_folder, 'log')
        os.makedirs(logfold, exist_ok=True)
        log_file_path = os.path.join(logfold, "INUE LOGS__Burnt Area Analyzer.log")

    log_window = None
    if use_log_window:
        log_window = LogWindow(title="INUE - version 1.1 άλφα Burnt Area Analyzer module", 
                               icon_path=resource_path("inue_YQZ_icon.ico"),
                               log_file_path=log_file_path)
        log_window.update()#keeps the logger open while calculating
        log_window.update()#keeps the logger open while calculating

    # Reindirizza i print sia al file di log che alla finestra (se attiva)
    sys.stdout = LogFileWriter(log_file_path) if not use_log_window else sys.stdout

    print("====== INUE - version 1.1.1 άλφα - Burnt Area Analyzer Module ======")
    print(f"Session started: {datetime.datetime.now()}\n")
    log_window.update() if log_window else None

    cumintzora = datetime.datetime.now()
    print("Welcome in Burnt Area Analyzer! This module allows to calculate the necessary input for PFES drafting. Additiionally drafts wildfire perimeter.")
    log_window.update() if log_window else None
    print("Burnt Area Analyzer is loading files and parameters... Wait please :)")
    log_window.update() if log_window else None
    b8pre = input_tiff['PREFIRE_NIR']
    b12pre = input_tiff['PREFIRE_SWIR']
    b8post = input_tiff['POSTFIRE_NIR']
    b12post = input_tiff['POSTFIRE_SWIR']
    coro = parameters['coro']
    resolution = parameters['resolution']
    epsg = parameters['epsg']
    parameters['trs_l2a'] = manager.open_array(b8pre)[2]
    otrs = parameters['trs_l2a']
    output_folder = parameters['out_fold']

    #PREFIRE condition
    print("Burnt Area Analyzer - Module 1: NBR index for the prefire condition is going to be calculated")
    log_window.update() if log_window else None
    prenir = manager.open_array(b8pre)[1]
    preswir = manager.open_array(b12pre)[1]
    prenum = manager.array_calculator(prenir, preswir, 'difference', resolution, epsg, otrs)
    preden = manager.array_calculator(prenir, preswir, 'sum', resolution, epsg, otrs)
    NBRprefire = manager.array_calculator(prenum, preden, 'division', resolution, epsg, otrs, 'NBRprefire')[1]
    print("Burnt Area Analyzer is cleaning memory.. Please wait!")
    log_window.update() if log_window else None
    del prenir
    del preswir
    del prenum
    del preden
    print("Memory was successfully cleaned")
    log_window.update() if log_window else None
    print("Burnt Area Analyzer - Module 1: NBR index for the prefire condition had been calculated")
    log_window.update() if log_window else None

    #POSTFIRE condition
    print("Burnt Area Analyzer - Module 1: NBR index for the postfire condition is going to be calculated")
    log_window.update() if log_window else None
    postnir = manager.open_array(b8post)[1]
    postswir = manager.open_array(b12post)[1]
    postnum = manager.array_calculator(postnir, postswir, 'difference', resolution, epsg, otrs)
    postden = manager.array_calculator(postnir, postswir, 'sum', resolution, epsg, otrs)
    NBRpostfire = manager.array_calculator(postnum, postden, 'division', resolution, epsg, otrs, 'NBRpostfire')[1]
    print("Burnt Area Analyzer is cleaning memory.. Please wait!")
    log_window.update() if log_window else None
    del postnir
    del postswir
    del postnum
    del postden
    print("Memory was successfully cleaned")
    log_window.update() if log_window else None
    print("Burnt Area Analyzer - Module 1: NBR index for the postfire condition had been calculated")
    log_window.update() if log_window else None

    # dNBR
    print("Burnt Area Analyzer - Module 2: dNBR index is going to be calculated")
    log_window.update() if log_window else None
    dNBR = manager.array_calculator(NBRprefire, NBRpostfire, 'difference', resolution, epsg, otrs) 
    del NBRprefire
    del NBRpostfire
    print("Memory was successfully cleaned")
    log_window.update() if log_window else None
    dNBRpath = os.path.join(output_folder, 'dNBR.tif')
    manager.save(dNBR, 'dNBR', resolution, epsg, otrs)
    mapper(dNBRpath, 'dNBR', 'turbo', 'linear', font_props)
    dnbrmin = np.nanmin(dNBR)
    if dnbrmin < 0:
        damin = abs(dnbrmin)
        dnbrplus = manager.array_calculator(dNBR, damin, 'sum', resolution, epsg, otrs, 'dNBR+')[1]
        dnbrpfespath = os.path.join(output_folder, 'dNBR+.tif')
    else:
        dnbrpfespath = dNBRpath
    manager.update_assetios('dNBR+', dnbrpfespath, 'tiff', 'output')
    manager.update_assetios('dNBR', dNBRpath, 'tiff', 'output')

    print("Burnt Area Analyzer - Module 2: dNBR index had been calculated")
    log_window.update() if log_window else None

   # Burn Severity
    print("Burnt Area Analyzer - Module 3: Burn severity drafting")
    log_window.update() if log_window else None
    Burn_severity = np.zeros_like(dNBR) 

    #Burn_severity[dNBR < -0.500] = -9999
    Burn_severity[(dNBR >= np.nanmin(dNBR)) & (dNBR <= -0.250)] = 1.0
    Burn_severity[(dNBR > -0.250) & (dNBR <= -0.100)] = 2.0
    Burn_severity[(dNBR > -0.100) & (dNBR <= 0.100)] = 3.0
    Burn_severity[(dNBR > 0.100) & (dNBR <= 0.270)] = 4.0
    Burn_severity[(dNBR > 0.270) & (dNBR <= 0.440)] = 5.0
    Burn_severity[(dNBR > 0.440) & (dNBR <= 0.660)] = 6.0
    Burn_severity[(dNBR > 0.660) & (dNBR <= np.nanmax(dNBR))] = 7.0
    #Burn_severity[dNBR > 1.300] = -9999    

    manager.save(Burn_severity, 'Burn Severity map', resolution, epsg, otrs)
    bspath = os.path.join(output_folder, 'Burn Severity map.tif')
    value_to_label1 = {
    1: 'Postfire Regrowth (High)',
    2: 'Postfire Regrowth (Low)',
    3: 'Unburnt',
    4: 'Low Severity',
    5: 'Moderate Low Severity',
    6: 'Moderate High Severity',
    7: 'High Severity'
    }
    mapper(bspath, 'Burn Severity', 'turbo', 'linear', font_props, value_to_label1)
    print("Burnt Area Analyzer - Module 3: Burn severity had been calculated")
    log_window.update() if log_window else None

    BPFES = np.zeros_like(dNBR)
    
    BPFES[(dNBR >= np.nanmin(dNBR)) & (dNBR <= 0.100)] = 1.0
    BPFES[(dNBR > 0.100) & (dNBR <= 0.270)] = 2.0
    BPFES[(dNBR > 0.270) & (dNBR <= 0.440)] = 3.0
    BPFES[(dNBR > 0.440) & (dNBR <= 0.660)] = 4.0
    BPFES[(dNBR > 0.660) & (dNBR <= np.nanmax(dNBR))] = 5.0

    manager.save(BPFES, 'rBS', resolution, epsg, otrs)
    rBSpath = os.path.join(output_folder, 'rBS.tif')
    value_to_label2 = {
    1: 'Unburnt',
    2: 'Low Severity',
    3: 'Moderate Low Severity',
    4: 'Moderate High Severity',
    5: 'High Severity'
    }
    mapper(rBSpath, 'reclassified Burn Severity', 'turbo', 'linear', font_props, value_to_label2)
    manager.update_assetios('rBS', rBSpath, 'tiff', 'output')
    print("Burnt Area Analyzer - Module 3: rBS input parameter had been calculated")
    log_window.update() if log_window else None
    print("Burnt Area Analyzer - Module 4: Wildfire Perimeter drafting")
    log_window.update() if log_window else None
    WFP = np.zeros_like(BPFES)

    WFP[BPFES == 1.0] = -9999
    WFP[BPFES >= 2.0] = 1.0
    WFP[BPFES == -9999] = -9999
    manager.save(WFP, 'Wildfire Perimeter', resolution, epsg, otrs)
    wfpath = os.path.join(output_folder, 'Wildfire Perimeter.tif')
    print("Burnt Area Analyzer - Module 4: Wildfire Perimeter drafted...")
    log_window.update() if log_window else None
    #shpath = os.path.join(output_folder, 'Wildfire Perimeter Shapefile.shp')
    #manager.shapadore(wfpath, shpath, epsg) in case of wide burnt areas the program dramatically slows down. this is the reason why it is deactivated
    value_to_label3 = {
    1.0: 'Burnt Scar Perimeter',
    }
    mapper(wfpath, 'Wildfire Perimeter', 'Oranges', 'linear', font_props)

    print("Burnt Area Analyzer is cleaning memory.. Please wait!")
    log_window.update() if log_window else None
    del dNBR
    del value_to_label1
    del value_to_label2
    del BPFES
    del Burn_severity
    del WFP
    print("Memory was successfully cleaned")
    log_window.update() if log_window else None
    acabora = datetime.datetime.now()
    totale = acabora-cumintzora
    print("Burnt Area Analyzer - Module 4: Wildfire Perimeter drafted as shapefile!")
    log_window.update() if log_window else None
    print(f"elaborations performed in {totale}")
    log_window.update() if log_window else None
    print("Burnt Area Analyzer ended its work! See you soon!")
    log_window.update() if log_window else None
    if log_window:
        log_window.mainloop()

    
    
