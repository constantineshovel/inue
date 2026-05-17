# DISCLAIMER OF LIABILITY:
# This software is provided "as is", without any warranty
# The author is not responsible for any damages resulting from its use
#LICENSE:
# This file is part of INUE - INteractive and Userfriendly Emergency tool for burnt areas v. 1.1.1 'άλφα, released under the GNU Affero General Public License v3.
# See the LICENSE file or https://www.gnu.org/licenses/agpl-3.0.html for more details.
#Copyright Costantino Pala © 2026
#This file was created in the framework of a PhD funded by CNR-IRPI-PG and DSCG-UNICA


import os#library useful to manage paths and folders
import subprocess#library useful to load TauDEM commands 
import datetime#library used to measure the time needed for operations
import numpy as np#do you need a comment here?
import file_manager as manager #the armed wing of INUE: it holds the 99% of functions used in the modules. 
from dask_image.ndfilters import generic_filter #is a function useful to performer neighbhrood analysis using multiprocessing
from assetios import parameters, input_tiff, output_tiff #assetios is the configuration module
from mapadore import mapper#A function written by ChatGPT to plot simple maps for some of the outputs...
from mapadore import font_props#dictionary containing the font settings for the simple maps
import dask.array as da#manages arrays in chunks, allowing multiprocessing 
import customtkinter as ctk#The library used to build the GUI. In this case is needed to open the logger
import sys#useful when giving an icon to the logger window
from PIL import Image#useful when giving an icon to the logger window
import shutil

def resource_path(relative_path):#you can find comments about this functions in the module ndvithresholder.py
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

coro = parameters['coro']#the number of cores available in your machine. this number is useful to load MPI prompts to use all the available cores
def tauexecuter(taucommand, resolution, epsg, otrs, output_folder, corenumber = coro, flowdirinput = None, flowdiroutput = None, slopout = None, scainput = None, scaname = None, floac = None, demwg = None, dirfleg = None, rivfleg = None):
    """
    Tauexecuter allows to set the TAUDEM commands for dem sink filling, d-inifinity flow direction and flow accumulation and flow lenght calculation. The function has mandatory and optional
    commands and the outputs can be one or two, depending on the case. The first output is the path to the TIF file, the second one is the memory pointer to the array. SInce TAUDEM does not assigns
    the transform INUE overwrites the output assigning a transform for proper GIS visualization.

    >>>Commands
    taucommand is the TAUDEM function to use
    resolution is the resolution used, rembember that the resolution in INUE is always the same. epsg is the SR EPSG code, corenumber is automatically calculated and is useful to use memory
    in an efficient way.
    
    > 'FillDem' sink filler for Digital Elevation Models
    tauexecuter('FillDem', resolution, epsg, output_folder, corenumber)
    > 'FlowDir' calculates the d-infinity flow direction
    tauexecuter('FlowDir', resolution, epsg, output_folder, corenumber)
    > 'FlowAcc' calculates the Flow Accumulation, following the D-Inifinity flow algorithms. It is splitted in two parts: the first one calculates the Specific Catchment Area (SCA) using the TAUDEM AreaDinf.
    The second part uses the INUE array_calculator to divide for the resolution and obtain the Flow Accumulation.
    tauexecuter('FlowAcc', resolution, epsg, corenumber, 'scainput', 'scaname', 'floac') --> without weight
    scainput is the d-inifinity flowdirection raster path to use for SCA computation (string). scaname is the output name for the SCA raster tif (string). floac is the name of the final flow accumu-
    lation raster (string). All the strings are without the extension, which is tif by default.
    Since SCA computation allows the use of a weight the weight is a raster tiff whose path is furnished by the demwg option, which is optional. 
    tauexecuter('FlowAcc', resolution, epsg, corenumber, 'scainput', 'scaname', 'floac', 'demwg') --> this one has weight
    the FLOWACC outputs are 2, the tiff and the array.

    >'FlowLenght' is the command to calculate the FlowLenght. It outputs only an array of FlowLenghts.
    tauexecuter('FlowLenght', resolution, epsg, output_folder, coro, 'demwg', 'dirfleg', 'rivfleg')
    'FlowLenght' is the keyworkd to launch this TAUDEM command. demwg is a string and is a weight. dirfleg is the flowdirection to use for the flowlenght, is a path to the raster file.
    rivfleg is the path to the proper raster of streams to use as target.    
    """
    global syst
    syst = parameters["sistema"]#system code for taudem. based on the OS gives the right MPI sintax to launch the TauDEM module.. tested on linux, must be tested on macos
    whereistau = os.path.expanduser("~/TauDEM/src/build")
    if taucommand == 'FillDem':#1 output: path to filled dem
        global filledem
        output_folder = parameters['out_fold']
        filledem = os.path.join(output_folder, 'filledem.tif')
        match syst:
            case 1:
                pitpath = os.path.join(whereistau, 'pitremove')
                result=subprocess.run(f"mpiexec -n {coro} {pitpath} -z \"{DEM}\" -fel \"{filledem}\"",
                                 capture_output=True, text=True, shell=True
            )
                print(result.stdout)
                print(result.stderr)
            case 2:
                result=subprocess.run(f"mpiexec -n {coro} PitRemove -z \"{DEM}\" -fel \"{filledem}\"",
                                 capture_output=True, text=True, shell=True
            )
                print(result.stdout)
                print(result.stderr)
            case 3:
                result=subprocess.run(f"mpiexec -n {coro} pitremove -z \"{DEM}\" -fel \"{filledem}\"",
                                 capture_output=True, text=True, shell=True
            )
                print(result.stdout)
                print(result.stderr)
        fdt = manager.open_array(filledem)[1]
        manager.save(fdt, 'filledem', resolution, epsg, otrs)#assigns a transform and overwrites the file. I noticed the files in output from TauDEM did not have the right transform.. By this way i ensure the transform is assigned
        return filledem
        del fdt# i used del to free memory!
        # No file assignment needed, filledemtif is used later in further calculations
    elif taucommand == 'FlowDir':#1 output: path to the flow direction file generated
        global flowdirinf
        output_folder = parameters['out_fold']
        fgh = f'{flowdiroutput }'+'.tif'
        flowdirinf = os.path.join(output_folder, fgh)#flow direction output path
        global slopedirinf
        sgh = f'{slopout}'+'.tif'
        slopedirinf = os.path.join(output_folder, sgh)#slope output path
        match syst:
            case 1:#linux
                inflowdirpath = os.path.join(whereistau, 'dinfflowdir')
                result = subprocess.run(f'mpiexec -n {coro} {inflowdirpath} -fel \"{flowdirinput}\" -ang \"{flowdirinf}\" -slp \"{slopedirinf}\"',
                             capture_output=True, text=True, shell=True
                )
                print(result.stdout)
                print(result.stderr)
            case 2:#windows... for the sintax of TauDEM commands check in the TauDEM user guide
                result = subprocess.run(f'mpiexec -n {coro} DinfFlowDir -fel \"{flowdirinput}\" -ang \"{flowdirinf}\" -slp \"{slopedirinf}\"',
                             capture_output=True, text=True, shell=True
                )
                print(result.stdout)
                print(result.stderr)
            case 3:#macos
                result = subprocess.run(f'mpiexec -n {coro} dinfflowdir -fel \"{flowdirinput}\" -ang \"{flowdirinf}\" -slp \"{slopedirinf}\"',
                             capture_output=True, text=True, shell=True
                )
                print(result.stdout)
                print(result.stderr)
        
        if result.returncode == 0:
            # If the command was successful, check if output files are created
            if os.path.exists(flowdirinf) and os.path.exists(slopedirinf):
                global fdd
                fdd = manager.open_array(flowdirinf)[1]
                fdd[fdd < 0] = np.nan #ignores the 0 values using np.nan
                manager.save(fdd, 'flowdirinf', resolution, epsg, otrs)#assigns a transform and overwrites the file
                del fdd
                global sdr
                sdr = manager.open_array(slopedirinf)[1]
                manager.save(sdr, 'slopedirinf', resolution, epsg, otrs)#assigns a transform and overwrites the file
                del sdr
                # Assign the file paths to variables
                flowdir_output = f'{flowdirinf}'
                slope_output = f'{slopedirinf}'
                print(f"Flow direction and slope files created: {flowdir_output}, {slope_output}")
                return flowdir_output
            else:
                print("Error: Output files not found.")
        else:
            print(f"Error in running command: {result.stderr}")
    
    elif taucommand == 'FlowAcc':#2 outputs (path to tiff file, pointer to array)
        #This algorithm firstly calculates the Specific Catchment Area, then uses the resolution to calculate the flow accumulation. D-Inf algorithm. TauDEM function: AreDINF
        global demsca
        output_folder = parameters['out_fold']
        dsa = f'{scaname}' + '.tif'
        demsca = os.path.join(output_folder, dsa)

        #checks the definition of a weight
        if demwg is None:
            match syst:
                case 1:
                    inareadinf = os.path.join(whereistau, 'areadinf')
                    result = subprocess.run(
                    f'mpiexec -n {coro} {inareadinf} -ang \"{scainput}\" -sca \"{demsca}\" -nc',
                    capture_output=True, text=True, shell=True
                )
                    print(result.stdout)
                    print(result.stderr)
                case 2:
                    result = subprocess.run(
                    f'mpiexec -n {coro} AreaDinf -ang \"{scainput}\" -sca \"{demsca}\" -nc',
                    capture_output=True, text=True, shell=True
                )
                    print(result.stdout)
                    print(result.stderr)
                case 3:
                    result = subprocess.run(
                    f'mpiexec -n {coro} areadinf -ang \"{scainput}\" -sca \"{demsca}\" -nc',
                    capture_output=True, text=True, shell=True
                )
                    print(result.stdout)
                    print(result.stderr)
        else:
            dws = f'{demwg}' #+ '.tif'
            wgfile = os.path.join(output_folder, dws)
            match syst:
                case 1:
                    inareadinf = os.path.join(whereistau, 'areadinf')
                    result = subprocess.run(
                    f'mpiexec -n {coro} {inareadinf} -ang \"{scainput}\" -sca \"{demsca}\" -wg \"{wgfile}\" -nc',
                    capture_output=True, text=True, shell=True
                )
                    print(result.stdout)
                    print(result.stderr)
                case 2:
                    result = subprocess.run(
                    f'mpiexec -n {coro} AreaDinf -ang \"{scainput}\" -sca \"{demsca}\" -wg \"{wgfile}\" -nc',
                    capture_output=True, text=True, shell=True
                )
                    print(result.stdout)
                    print(result.stderr)
                case 3:
                    result = subprocess.run(
                    f'mpiexec -n {coro} areadinf -ang \"{scainput}\" -sca \"{demsca}\" -wg \"{wgfile}\" -nc',
                    capture_output=True, text=True, shell=True
                )
                    print(result.stdout)
                    print(result.stderr)

        #print(result)

        if os.path.exists(demsca):
            scar = manager.open_array(demsca)[1]
            #print(scar)
            scarestif, scaresar = manager.array_calculator(scar, resolution, 'division', resolution, epsg, otrs, f'{floac}') #This is the command which calculates the flow accumulation
            return scarestif, scaresar 
        else:
            print(f"Error: Output file {demsca} not found.")
            return


        
    elif taucommand == 'FlowLenght':#1 output, as pointer to array
        output_folder = parameters['out_fold']
        X = os.path.join(output_folder, 'X.tif')
        match syst:
            case 1:
                indinfdown = os.path.join(whereistau, 'dinfdistdown')
                result = subprocess.run(
               f'mpiexec -n {coro} {indinfdown} -ang \"{dirfleg}\" -fel \"{filledem}\" -src \"{rivfleg}\" -wg \"{demwg}\" -dd \"{X}\" -m min v -nc',
                capture_output=True, text=True, shell=True
            )
                print(result.stdout)
                print(result.stderr)
            case 2:
                result = subprocess.run(
               f'mpiexec -n {coro} DinfDistDown -ang \"{dirfleg}\" -fel \"{filledem}\" -src \"{rivfleg}\" -wg \"{demwg}\" -dd \"{X}\" -m min v -nc',
                capture_output=True, text=True, shell=True
            )
                print(result.stdout)
                print(result.stderr)
            case 3:
                result = subprocess.run(
               f'mpiexec -n {coro} dinfdistdown -ang \"{dirfleg}\" -fel \"{filledem}\" -src \"{rivfleg}\" -wg \"{demwg}\" -dd \"{X}\" -m min v -nc',
                capture_output=True, text=True, shell=True
            )
                print(result.stdout)
                print(result.stderr)
    
        if result.returncode == 0:
            if os.path.exists(X):
                xd = manager.open_array(X)[1]
                xdd = np.where(xd < 0, np.nan, xd)
                manager.save(xdd, "X", resolution, epsg, otrs)
                del xd
                del xdd
                print(f"Flow length file created: {X}")
                return X
            else:
                print("Error: Output file not found.")
        else:
            print(f"Error in running command: {result.stderr}")

def aberi_ic(use_log_window=True, log_file_path=None):
    #global is used to allow the file be used by File_Manager.py
    global DEM
    DEM = input_tiff["DEM"]
    global DEMROAD
    demset = parameters['Demroad']
    if demset == 'On':
        DEMROAD = input_tiff["DEMROAD"]
    else:
        DEMROAD = input_tiff["DEM"]
    print('DEM path:', f'{DEM}')
    print('DEMROAD path:', f'{DEMROAD}')
    global epss
    epss = parameters["epsg"]
    global res
    res = parameters["resolution"]
    global output_folder
    output_folder = parameters["out_fold"]
    global otrs 
    otrss = parameters["trs_csi"]
    coro = parameters['coro']
   

    def ic(DEM, output_folder, resolution = res, epsg = epss, otrs= otrss, corenumber=coro,use_log_window=True, log_file_path=None):
        if log_file_path is None:
            logfold = os.path.join(output_folder, 'log')
            os.makedirs(logfold, exist_ok=True)
            log_file_path = os.path.join(logfold, "INUE LOGS__Sediment Connector.log")

        log_window = None
        if use_log_window:
            log_window = LogWindow(title="INUE - version 1.1 άλφα Sediment Connector Module", 
                                   icon_path=resource_path("inue_YQZ_icon.ico"),
                                   log_file_path=log_file_path)
            log_window.update()  #This expression mantains the window open while INUE and TauDEM are calculating

        #The following expression sends the messages to the log window and file
        sys.stdout = LogFileWriter(log_file_path) if not use_log_window else sys.stdout

        print("====== INUE - version 1.1 άλφα - Sediment Connector Module ======")
        print(f"Session started: {datetime.datetime.now()}\n")
        log_window.update() if log_window else None

        # _______________________DEM FILLER_________________________________this is useful to calculate Rivermask.. 
        print("Sediment Connector: Module 1 - DEM FILLER, by TAUDEM")
        cumintzora = datetime.datetime.now()
        filledem = tauexecuter('FillDem', resolution, epsg, otrs, output_folder, corenumber=coro)
        log_window.update() if log_window else None
        print("100% completed")
        print("Sediment Connector: Module 1 - TAUDEM successfully filled the sinks")

        # ___________________FlowDir: DINFFLOWDIR___________________________ Calculates a normal FlowDir for the rivermask
        print("Sediment Connector: Module 2 - FLOW DIRECTION, by TAUDEM")
        flowdir = tauexecuter('FlowDir', resolution, epsg, otrs, output_folder, corenumber=coro, flowdirinput = filledem, flowdiroutput = 'flowdir', slopout = 'slp')#per calcolo rivermask
        del filledem
        log_window.update() if log_window else None
        print("100% completed")
        print("Sediment Connector: Module 2 - TAUDEM successfully computed Flow Direction d-infinity")
        
        # ___________________DIRMASK DINFFLOWDIR * ROADMASK________________This FlowDir takes into account the effects of roads on flows.. 
        print("Sediment Connector: Module 3 - DIRMASK is going to be calculated by TAUDEM and INUE")
        dirmask = tauexecuter('FlowDir', resolution, epsg, otrs, output_folder, corenumber=coro, flowdirinput = DEMROAD, flowdiroutput = 'DIRMASK', slopout = 'slproad')#per calcoli considerando strade
        log_window.update() if log_window else None
        print("100% completed")
        print("Sediment Connector: Module 3 - TAUDEM and INUE successfully computed DIRMASK")

        
        
        # _____________________RIVERMASK ACCMASK <=1000_________________________Outputs the StreamNetwork to be used as target for other modules.. 
        print("Sediment Connector: Module 5 - RIVERMASK is going to be calculated by TAUDEM and INUE")
        accnorm = tauexecuter('FlowAcc', resolution, epsg, otrs, output_folder, corenumber=coro, scainput=flowdir, scaname = 'sca_acc', floac = 'FLOWACC')[1]#ACCnormal
        print(f"{int((1/5)*100)}% completed")
        rivthr = np.nanmax(accnorm)*0.004#0.4% of flow acc
        print(f"{int((2/5)*100)}% completed")
        rivermaskar = np.where(accnorm <= rivthr, 1.0, 0.0) #1 is slope area, 0 is channel area
        rivermaskar.astype(np.float32)
        print(f"{int((3/5)*100)}% completed")
        #rivermaskar = generic_filter(rivermaskar1, np.mean, [5,5])
        manager.save(rivermaskar, 'RIVERMASK', resolution, epsg, otrs)
        print(f"{int((4/5)*100)}% completed")
        rivermask = os.path.join(output_folder, 'RIVERMASK.tif')
        del rivthr
        del accnorm
        print(f"{int((5/5)*100)}% completed")
        log_window.update() if log_window else None
        print("Sediment Connector: Module 5 - TAUDEM and INUE successfully computed RIVERMASK")
        

        dirmask = os.path.join(output_folder, 'DIRMASK.tif')
        flowdir = os.path.join(output_folder, 'flowdirinf.tif')

        
        # _________________________ACCFINAL: DINFFLOWACC on DIRFINAL_____________
        print("Sediment Connector: Module 6 - ACCFINAL is going to be calculated by TAUDEM and INUE")
        preaccfinalar = tauexecuter('FlowAcc', resolution, epsg, otrs, output_folder, corenumber=coro, scainput=dirmask, scaname = 'SCA_preaccfinal', floac='preaccfinal')[1]
        accfinalar = manager.array_calculator(preaccfinalar, 1, 'sum', resolution, epsg, otrs, otn = 'ACCFINAL')[1]
        accfinal = os.path.join(output_folder, 'ACCFINAL.tif')
        log_window.update() if log_window else None
        print("Sediment Connector: Module 6 - TAUDEM and INUE successfully computed ACCFINAL") 
        
        # ___________________________WEIGHTS_____________________________________________________ This section calculates S and W impedance factors
        print("INUE is going to calculate the W and S weights")
        # Calculate S__________________________
        # __________________SLOPE________________
        print("Sediment Connector: Module 7 - SLOPE is going to be calculated by INUE")
        demarnp = manager.open_array(DEM)[1]
        print(f"{int((1/3)*100)}% completed")
        slopear = manager.slope(demarnp)#a function in the File_manager.py calculating the slope.. in degrees!
        print(f"{int((2/3)*100)}% completed")
        manager.save(slopear, 'slope', resolution, epsg, otrs)
        print(f"{int((3/3)*100)}% completed")
        log_window.update() if log_window else None
        print("Slope was successfully calculated. S will be calculated now.")
        
        # __________________S____________________
        # ((slope == 0) * 0.005) + slope (Borselli et al. 2008)
        Sar = da.where(slopear == 0, 0.005, slopear)
        print(f"{int((1/3)*100)}% completed")
        manager.save(Sar, 'S', resolution, epsg, otrs)
        del slopear
        print(f"{int((2/3)*100)}% completed")
        Stif = os.path.join(output_folder, 'S.tif')
        print(f"{int((3/3)*100)}% completed")
        log_window.update() if log_window else None
        print("Sediment Connector: Module 7 - Weight S has been calculated by INUE")
        
        # _________W____________________________
        print("Sediment Connector: Module 8 - Weight W")
        wseberadu = parameters.get("W Index")
        print(f"{int((1/7)*100)}% completed")
        if wseberadu == "Default":  # this is the choice to use the RI (Cavalli et al 2008) as W Index
            print("Since you choose to use the default W (Roughness Index proposed in Cavalli et al 2008) INUE is going to calculate it")
            meandemar = manager.fentana(demarnp, da.mean)#This function calculates the mean by applying a 5x5 moving window 
            log_window.update() if log_window else None
            print(f"{int((2/7)*100)}% completed")
            restopotif, restopoar = manager.array_calculator(demarnp, meandemar, 'difference', resolution, epsg, otrs,'residual_topography')
            print(f"{int((3/7)*100)}% completed")
            War = manager.fentana(restopoar, da.std)#This function calculates the standard deviation by applying a 5x5 moving window 
            log_window.update() if log_window else None
            print(f"{int((4/7)*100)}% completed")
            manager.save(meandemar, 'meandem', resolution, epsg, otrs)
            print(f"{int((5/7)*100)}% completed")
            manager.save(War, 'RI_Cavalli2008', resolution, epsg, otrs)
            print(f"{int((6/7)*100)}% completed")
            Wtif = os.path.join(output_folder, 'RI_Cavalli2008.tif')
            log_window.update() if log_window else None
            manager.update_assetios('W_Index', Wtif, 'tiff', 'output')#loads the w index into assetios
            del wseberadu
            del meandemar
            del demarnp
            del restopoar
            del restopotif
            print(f"{int((7/7)*100)}% completed")
            print("Sediment Connector: Module 8 - Default W (RI index, Cavalli et al 2008) has been calculated by INUE")
        else:#The user choice is to use a Custom W Index
            Wtif = output_tiff["W_Index"]
            War = manager.open_array(Wtif)[1]            
            print(f"{int((2/2)*100)} % completed")
            print("Since you choose to use a custom W index INUE loaded it for further computations")
        
        # __________________WEIGHTS CALCULATED___________________________________________________________
        
        print("Sediment Connector: DDn component")
        # _________________Ddn________________________________DOWNSLOPE COMPONENT
        print("Sediment Connector: Module 9 - inv_WS is going to be calculated by INUE")
        ws = manager.array_calculator(War, Sar, 'times', resolution, epsg, otrs)
        print(f"{int((1/2)*100)}% completed")
        inv_WStif, inv_WSar = manager.array_calculator(1, ws, 'division', resolution, epsg, otrs, 'inv_WS')
        log_window.update() if log_window else None
        del ws
        print(f"{int((2/2)*100)}% completed")
        print("Sediment Connector: Module 9 - inv_WS has been calculated by INUE")
        
        # _________________Calculates X using TauDEM FlowLength : flowlength(dirfinal) with inv_ws as weight and downstream
        print("Sediment Connector: Module 10 - X is going to be calculated by TAUDEM")
        Xtif = tauexecuter('FlowLenght', resolution, epsg, otrs, output_folder, coro, demwg = inv_WStif, dirfleg = flowdir, rivfleg = rivermask)
        print(f"{int(1/3)*100}% completed")
        Xar = manager.open_array(Xtif)[1]
        Xar.astype(np.float32)
        print(f"{int(2/3)*100}% completed")
        manager.save(Xar, "X", resolution, epsg, otrs)
        log_window.update() if log_window else None
        del rivermask
        del Xtif
        print(f"{int(3/3)*100}% completed")
        print("Sediment Connector: Module 10 - X had been calculated by TAUDEM")
        #this modules uses the normal flow dir, calculated in the module 2. 
        
        # ((X == 0) * inv_ws) + X (Borselli et al. 2008)
        print("Sediment Connector: Module 11 - Ddn is going to be calculated by INUE")
        Ddnar = np.where(Xar == 0, inv_WSar, Xar)
        print(f"{int((1/3)*100)}% completed")
        manager.save(Ddnar, 'Ddn', resolution, epsg, otrs)
        log_window.update() if log_window else None
        print(f"{int((2/3)*100)}% completed")
        #ddtf = os.path.join(output_folder, 'Ddn.tif')
        #print("int((3/4)*100), % completed")
        #Ddntif = manager.open_array(ddtf)
        del inv_WStif
        del inv_WSar
        del Xar
        #del ddtf
        print(f"{int((3/3)*100)} completed'")
        print("Sediment Connector: Module 11 - Ddn successfully calculated")
        
        # Dup____________________________________________ UPSLOPE COMPONENT
        print("Sediment Connector: Dup component")
        # (DINFFLOWACC((DIRFINAL. w) + w) / ACCFINAL = Wmean
        print("Sediment Connector: Module 12 - Wmean and Smean are going to be calculated by TAUDEM and INUE")
        wmean1ar = tauexecuter('FlowAcc', resolution, epsg, otrs, output_folder, coro, scainput = dirmask, scaname='sca_wmean1', floac = 'wm1', demwg=Wtif)[1]
        print(f"{int((1/3)*100)} % completed")
        wmeannumar = manager.array_calculator(wmean1ar, War, 'sum', resolution, epsg, otrs)
        log_window.update() if log_window else None
        print(f"{int((2/3)*100)} % completed")
        Wmeanar = manager.array_calculator(wmeannumar, accfinalar, 'division', resolution, epsg, otrs, 'wmean')[1]#era accfinalar
        print(f"{int((3/3)*100)} % completed")
        print("Wmean calculated")
        
        # (DINFFLOWACC((DIRFINAL. s) + s) / ACCFINAL = Smean
        smean1ar = tauexecuter('FlowAcc', resolution, epsg, otrs, output_folder, coro, scainput = dirmask, scaname='sca_smean1', floac = 'sm1', demwg=Stif)[1]
        print(f"{int((1/3)*100)} % completed")
        smeannumar = manager.array_calculator(smean1ar, Sar, 'sum', resolution, epsg, otrs)
        log_window.update() if log_window else None
        print(f"{int((2/3)*100)} % completed")
        Smeanar = manager.array_calculator(smeannumar, accfinalar, 'division', resolution, epsg, otrs, 'smean')[1]#eraaccfinalar
        del War
        del Sar
        del Wtif
        del wmean1ar
        del wmeannumar
        del smean1ar
        del smeannumar
        print(f"{int((3/3)*100)} % completed")
        print("Sediment Connector: Module 12 - Wmean and Smean had been calculated by TAUDEM and INUE")
        
        # Dup = Wmean * Smean * Sqrt(ACCFINAL) * 25 
        print("Sediment Connector: Module 13 - Dup is going to be calculated by INUE")
        acf = np.where(accfinalar <= 0, np.nan, accfinalar)# this expression manages negative values to exclude results in the group of complex numbers since cannot be handled by rasters
        Dupar = Wmeanar*Smeanar*np.sqrt(acf)*25
        manager.save(Dupar, 'Dup', resolution, epsg, otrs)
        log_window.update() if log_window else None
        del Stif
        print("Sediment Connector: Module 13 - Dup successfully calculated by INUE")
        
        # IC________________
        print("Sediment Connector: Module 14 - INUE is going to calculate the Sediment Connectivity Index (IC)")
        # ic = log10(Dup / Ddn) Borselli et al. 2008
        icratioar = manager.array_calculator(Dupar, Ddnar, 'division', resolution, epsg, otrs)
        print(f"{int((1/8)*100)} % completed")
        icratioar[icratioar == 0] = np.nan #ignores the 0 values using np.nan
        print(f"{int((2/8)*100)} % completed")
        icar = np.log10(icratioar)
        print(f"{int((3/8)*100)} % completed")
        manager.save(icar, 'IC', resolution, epsg, otrs)
        log_window.update() if log_window else None
        icpath = os.path.join(output_folder, 'IC.tif')
        print(f"{int((4/8)*100)} % completed")
        icnorm = (icar - np.nanmin(icar)) / (np.nanmax(icar) - np.nanmin(icar))
        print(f"{int((5/8)*100)} % completed")
        manager.save(icnorm, 'normalizedIC', resolution, epsg, otrs)
        print(f"{int((6.5/8)*100)} % completed")
        icnat = os.path.join(output_folder, "normalizedIC.tif")
        print(f"{int((7/8)*100)} % completed")
        manager.update_assetios("normalized_IC", icnat, "tiff", "output")#loads the file path into assetios for further computation
        print(f"{int((8/8)*100)} % completed")
        log_window.update() if log_window else None
        manager.update_assetios('IC', icpath, 'tiff', 'output')#loads the file path into assetios for further computation
        mapper(icpath, 'Sediment Connectivity Index', 'PiYG_r', 'quantile', font_props)
        mapper(icnat, 'normalized Sediment Connectivity Index', 'PiYG_r', 'quantile', font_props)
        acabora = datetime.datetime.now()
        totale = acabora-cumintzora
        print(f"Total time required: {totale}")
        print("Sediment Connector - Module 14: INUE successfully calculated IC and normalized it.")
        print("INUE is cleaning memory! The cleaning can take a while, wait please!")
        del Dupar
        del Ddnar
        del icratioar
        del icar
        del icnat
        del icnorm
        print("INUE cleaned memory")
        print("Sediment Connector successfully finished its work.")
        print("Thank you for using this software. See you soon!")
        if log_window:
            log_window.mainloop()

    ic(DEM, output_folder, res, epss, otrss, coro)
