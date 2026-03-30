# DISCLAIMER OF LIABILITY:
# This software is provided "as is", without any warranty
# The author is not responsible for any damages resulting from its use
# LICENSE:
# This file is part of INUE - INteractive and Userfriendly Emergency tool for burnt areas v. 1.1 'άλφα, released under the GNU Affero General Public License v3.
# See the LICENSE file or https://www.gnu.org/licenses/agpl-3.0.html for more details.
# Copyright Costantino Pala © 2025
# This file was created in the framework of a PhD funded by CNR-IRPI-PG and DSCG-UNICA
# Written by me, with coding support and suggestions from ChatGPT.

import sys
import customtkinter as ctk
import datetime
import os
import numpy as np
import dask.array as da
import file_manager as manager
from assetios import parameters, input_tiff, output_tiff
from PIL import Image

def resource_path(relative_path):
    """Obtain the proper path for icons, even if it is executed in an .exe"""
    if getattr(sys, 'frozen', False):  #if the program is executed as an exe
        base_path = sys._MEIPASS  # PyInstaller extracts the file here
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class PrintRedirector:
    """This function sends the print messages to the logger """
    def __init__(self, text_widget, log_file_path):
        self.text_widget = text_widget
        self.log_file_path = log_file_path  #Creates a dynamic path for the logger

    def write(self, message):
        self.text_widget.configure(state="normal")
        self.text_widget.insert("end", message)
        self.text_widget.see("end")
        self.text_widget.configure(state="disabled")
        write_to_log(message, self.log_file_path)  #Writes the message in the log file

    def flush(self):
        pass

class LogFileWriter:
    """Writes the log in a txt file"""
    def __init__(self, log_file_path):
        self.log_file_path = log_file_path

    def write(self, message):
        write_to_log(message, self.log_file_path)

    def flush(self):
        pass

def write_to_log(message, log_file_path):
    """The function to write the log message in a file """
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

        sys.stdout = PrintRedirector(self.text_area, log_file_path)  #Calls the function to send the print to the log

        self.protocol("WM_DELETE_WINDOW", self.on_close)  #Manages the window closing

    def on_close(self):#this function reset the stdout.. since the log function is the same across the modules it prevents problems
            if hasattr(self, "original_stdout"):
                sys.stdout = self.original_stdout #stdout reset
            self.destroy()

def arbures(use_log_window=True, log_file_path=None):
    """
    NDVI Thresholder calculates NDVI from Sentinel 2 L2A images then applies a threshold to take into account vegetation recovery.
    """

    output_folder = parameters['out_fold']  #The expression gets the output folder from the parameters dictionary stored in assetios

    #The following code manages the path where log will be saved
    if log_file_path is None:
        logfold = os.path.join(output_folder, 'log')
        os.makedirs(logfold, exist_ok=True)
        log_file_path = os.path.join(logfold, "INUE LOGS__NDVI Thresholder.log")

    log_window = None
    if use_log_window:
        log_window = LogWindow(title="INUE - version 1.1 άλφα - NDVI Thresholder module", 
                               icon_path=resource_path("inue_YQZ_icon.ico"),
                               log_file_path=log_file_path)
        log_window.update()  #This mantains the windows open while processing

    sys.stdout = LogFileWriter(log_file_path) if not use_log_window else sys.stdout

    print("====== INUE - version 1.1 άλφα - NDVI Thresholder Module ======")
    print(f"Session started: {datetime.datetime.now()}\n")
    log_window.update() if log_window else None  #Window updater
    cumintzora = datetime.datetime.now()
    
    b4 = input_tiff["Red_NDVI_Thresholder"] #The expression gets the Red file
    b8 = input_tiff["NIR_NDVI_Thresholder"]#The expression gets the NIR file
    thr = parameters["ndvi_thr"]#The expression gets the threshold to be used for NDVI thresholding
    epsg = parameters["epsg"]#The expression gets the epsg code you wrote
    resolution = parameters["resolution"]#The expression gets the resolution you set up
    otrs = parameters["trs_arb"]#The expression gets the Affine matrix to manage projection and georeferencing of the outputs

    print("NDVI Thresholder is reading the input files (Band 04 and Band 08)")
    log_window.update() if log_window else None  #Window updater

    b4ar = manager.open_array(b4)[1]
    b8ar = manager.open_array(b8)[1]

    print("NDVI Thresholder is computing NDVI")
    log_window.update() if log_window else None  #Window updater

    num = manager.array_calculator(b8ar, b4ar, 'difference', resolution, epsg, otrs)
    denom = manager.array_calculator(b8ar, b4ar, 'sum', resolution, epsg, otrs)
    ndvi, ndviar = manager.array_calculator(num, denom, 'division', resolution, epsg, otrs, 'NDVI')

    print(f"NDVI succesfully computed and saved to {ndvi}")
    log_window.update() if log_window else None  #Window updater

    print("NDVI Thresholder is thresholding NDVI to take into account the effects of vegetation recovery")
    vrt = da.where(ndviar <= thr, 1.0, 0.0)
    vrt2 = np.nan_to_num(vrt.compute(), nan=-9999, posinf=-9999, neginf=-9999)
    manager.save(vrt2, 'Vegetation Recovery Factor', resolution, epsg, otrs)

    vrtif = os.path.join(output_folder, "Vegetation Recovery Factor.tif")
    print(f"NDVI thresholded and saved to {vrtif}")
    log_window.update() if log_window else None  #Window updater

    manager.update_assetios("NDVI", ndvi, "tiff", "output")
    manager.update_assetios("VRf", vrtif, "tiff", "output")

    p1 = output_tiff["NDVI"]
    p2 = output_tiff["VRf"]
    print(f"NDVI path: {p1}")
    log_window.update() if log_window else None
    print(f"Vegetation Recovery path: {p2}")
    log_window.update() if log_window else None

    print("INUE is going to clean memory! Wait please!")
    log_window.update() if log_window else None
    del vrt2, vrtif, ndvi, p1, p2
    print(f"Total time required: {datetime.datetime.now() - cumintzora}")
    log_window.update() if log_window else None
    print("INUE cleaned memory! Thank you so much for waiting!")
    log_window.update() if log_window else None
    print("NDVI Thresholder finished its work. See you soon!")
    log_window.update() if log_window else None

    if log_window:
        log_window.mainloop()  #An expression allowing the log window to stay open and the operations to be performed
