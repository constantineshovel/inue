# DISCLAIMER OF LIABILITY:
# This software is provided "as is", without any warranty
# The author is not responsible for any damages resulting from its use
# LICENSE:
# This file is part of INUE - INteractive and Userfriendly Emergency tool for burnt areas v. 1.1 'άλφα, released under the GNU Affero General Public License v3.
# See the LICENSE file or https://www.gnu.org/licenses/agpl-3.0.html for more details.
# Copyright Costantino Pala © 2025
# This file was created in the framework of a PhD funded by CNR-IRPI-PG and DSCG-UNICA
# Written by me, with coding support and suggestions from ChatGPT and Google Gemini.

import os
import sys
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog
import file_manager as manager 
import consedinx as csi 
import burntareanalyzer 
import disconnector as disc 
import ndvithresholder 
import PFES 
import roadmask 
import about 
import assetios 
from assetios import input_tiff, input_shp, output_tiff, parameters 
from functools import partial 
import threading as tred
from concurrent.futures import ThreadPoolExecutor
import customvariable 
from PIL import Image, ImageTk

#___________________________________________________GUI_______________________________________________________________

def resource_path(relative_path):
    """The module obtains the proper path for the file, even when executed in an exe."""
    if getattr(sys, 'frozen', False):  
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def GUI():
    # Initialize the main window
    ctk.set_appearance_mode("light")  
    root = ctk.CTk()
    root.title("INUE - INteractive and Userfriendly Emergency tool for postfire erosion susceptibility mapping v. 1.1 'άλφα'")

    sistema = parameters["sistema"]
    if sistema == 2:
        try: root.iconbitmap(resource_path("inue_YQZ_icon.ico"))
        except: pass
    elif sistema == 1:
        try: root.iconbitmap(resource_path("inue256.png"))        
        except: pass

    # Set window size
    dwith = root.winfo_screenwidth()
    dheig = root.winfo_screenheight()
    root.geometry(f"{dwith}x{dheig}")

    # Define colors
    panel_color = "#ECEFF1"
    button_color = "#003366" 

    # Set the window background color
    root.configure(bg=panel_color)

    # Set Segoe UI font in bold
    font_style = ("Open Sans", 14, "bold")
    font_header = ("Open Sans", 16, "bold")

    # ---------------------------------------------------------
    # 0. LOGICA SWITCHER (Anticipata per il Top Frame)
    # ---------------------------------------------------------
    def update_switcher_value(title, value):
        parameters[title] = value 
        print(f"Updated {title} to {value}")

    switcher_config = [
        {"title": "Demroad", "sx_label": "On", "dx_label": "Off", "true": "Off", "false": "On"},
        {"title": "W Index", "sx_label": "Default", "dx_label": "Your own", "true": "Your own", "false": "Default"},
        {"title": "Area Configuration", "sx_label": "Postfire", "dx_label": "Veg. Recov.", "true": "Vegetation recovering", "false": "Postfire"},
        {"title": "Disconnecting Landforms", "sx_label": "No", "dx_label": "Yes", "true": "Yes", "false": "No"}
    ]
    
    # Colori hover per gli switch
    switch_colors = ('#00cc66', '#0066FF', '#FF4F00', '#8000FF')

    def switch_callback(title, switch, true, false):
        current_value = switch.get()
        print(f"Switch state for '{title}': {switch.get()}")
        update_switcher_value(title, current_value)

    # ---------------------------------------------------------
    # 1. TOP FRAME (Header Ribbon: Logo SX, Switch DX)
    # ---------------------------------------------------------
    top_frame = ctk.CTkFrame(root, fg_color=panel_color)
    top_frame.pack(side="top", padx=0, pady=5, fill="x", expand=False)

    # A. LOGO (Sinistra) - SMART RESIZING
    try:
        logo_path = resource_path("inue.png")  
        pil_image = Image.open(logo_path)
        
        # --- CALCOLO PROPORZIONI ---
        desired_height = 120
        aspect_ratio = pil_image.width / pil_image.height
        desired_width = int(desired_height * aspect_ratio)
        
        # Creiamo l'immagine CTk
        logo = ctk.CTkImage(light_image=pil_image, size=(desired_width, desired_height))
        
        logo_label = ctk.CTkLabel(top_frame, image=logo, text="", fg_color="transparent")
        logo_label.pack(side="left", padx=20, pady=5)
    except Exception as e:
        print(f"Errore caricamento logo: {e}")
        ctk.CTkLabel(top_frame, text="INUE", font=font_header).pack(side="left", padx=20)

    # Function to enable window dragging
    def start_drag(event):
        global offset_x, offset_y
        offset_x = event.x
        offset_y = event.y

    def do_drag(event):
        x = root.winfo_x() - offset_x + event.x
        y = root.winfo_y() - offset_y + event.y
        root.geometry(f"+{x}+{y}")

    # Bindings per il drag
    top_frame.bind("<Button-1>", start_drag)
    top_frame.bind("<B1-Motion>", do_drag)
    try:
        logo_label.bind("<Button-1>", start_drag)
        logo_label.bind("<B1-Motion>", do_drag)
    except: pass

    # B. SWITCHER CONTAINER (Destra)
    switcher_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
    switcher_frame.pack(side="right", padx=20, pady=5)

    # Generazione Switcher (Orizzontale)
    for i, config in enumerate(switcher_config):
        single_switch_box = ctk.CTkFrame(switcher_frame, fg_color="transparent")
        single_switch_box.pack(side="left", padx=10) 
        
        ctk.CTkLabel(single_switch_box, text=config["title"], font=("Open Sans", 12, "bold"), text_color="#555555").pack(side="top", pady=(0,2))
        
        ctrl_row = ctk.CTkFrame(single_switch_box, fg_color="transparent")
        ctrl_row.pack(side="top")
        
        ctk.CTkLabel(ctrl_row, text=config["sx_label"], font=("Open Sans", 10)).pack(side="left", padx=5)
        
        switcher = ctk.CTkSwitch(
            ctrl_row,
            text="",
            onvalue=config["true"], 
            offvalue=config["false"], 
            switch_width=24,
            switch_height=14,
            border_width=3,
            fg_color='grey',
            progress_color='grey',
            button_color='#003366', 
            button_hover_color=switch_colors[i],
            width=30,
            height=20
        )
        switcher.pack(side="left", padx=0)
        switcher.configure(command=partial(switch_callback, title=config["title"], switch=switcher, true=config["true"], false=config["false"]))
        
        ctk.CTkLabel(ctrl_row, text=config["dx_label"], font=("Open Sans", 10)).pack(side="left", padx=5)


    top_frame.grid_columnconfigure(0, weight=1, minsize=200)  
    top_frame.grid_columnconfigure(1, weight=0)  

    #______________________________Definition of a Saving Folder____________________________________________
    def select_outdir():
        outpath = filedialog.askdirectory(title="Select the Processed Files Directory")
        parameters['out_fold'] = outpath
        if outpath: 
            print(f"Selected directory:", parameters['out_fold'])
            global output_folder
            output_folder = parameters['out_fold']

    #_______________________________UI refresh (AUTOMATION)_________________________________________________
    # Dizionario per memorizzare i widget dei bottoni target
    monitored_buttons = {}
    
    # AGGIUNTO DEMROAD ALLA LISTA
    TARGET_KEYS = ["normalized_IC", "dNBR", "DISCONNECTING_INDEX", "VRf", "DEMROAD"]

    def annoadore(window):
        annoa()
        window.after(1000, lambda: annoadore(window))

    def annoa():
        # DEFINIZIONE PALETTE
        # Palette ROSSA (Fire/Emergency)
        RED_READY = "#C62828"   
        RED_WAIT = "#EF5350"
        
        # Palette VIOLA (IC/Geomorphology) - per DEMROAD
        PURPLE_READY = "#512DA8"
        PURPLE_WAIT = "#9575CD"
        
        for key in TARGET_KEYS:
            if key in monitored_buttons:
                button = monitored_buttons[key]
                path = assetios.input_tiff.get(key) or assetios.output_tiff.get(key)
                
                # SELEZIONE COLORE IN BASE AL TIPO DI BOTTONE
                if key == "DEMROAD":
                    ready_col = PURPLE_READY
                    wait_col = PURPLE_WAIT
                else:
                    ready_col = RED_READY
                    wait_col = RED_WAIT

                # APPLICAZIONE STATO
                if path is not None:
                    button.configure(fg_color=ready_col)
                else:
                    button.configure(fg_color=wait_col)

    # ________________________FILE SELECTOR____________________________________________________

    def browse(btn_instance, label, ext, f_type, dark_color, dict_key):
        
        # Gestione Funzioni speciali
        if "Select the" in label and "Directory" in label and ext == "function":
            select_outdir()
            if parameters.get('out_fold'):
                btn_instance.configure(fg_color=dark_color)
            return
            
        elif label == "Preliminary\nOperations" and ext == "function":
            manager.file_manager()
            return

        elif label == "Help\n&\nAbout" and ext == "function":
             about.about()
             return

        # Gestione selezione File
        if ext != "function":
            filetypes = (("All files", "*.*"), (f"{f_type} Files", f"*{f_type}"))
            var_name = label.replace("Select\n", "").replace(" ", "_").replace("\n", "_")
            
            filename = filedialog.askopenfilename(
                title=f"Select {var_name} File",
                initialdir="/",
                filetypes=filetypes
            )

            print(f"Selected {label}: {filename}")

            if filename: 
                # 1. Aggiorna Grafica (colore immediato al click)
                btn_instance.configure(fg_color=dark_color)
                
                # 2. Normalizza percorso
                filename = os.path.normpath(filename)
                
                # 3. Logica di business
                match var_name:
                    case "DEM":
                        print(var_name, filename, ext)
                        manager.update_assetios(var_name, filename, ext, 'input')
                        DEM = input_tiff["DEM"]
                        if DEM: parameters["trs_csi"] = manager.open_array(DEM)[2]
                    case "PREFIRE_NIR":
                        print(var_name, filename, ext)
                        manager.update_assetios(var_name, filename, ext, 'input')
                        b12l2a = input_tiff["PREFIRE_NIR"]
                        if b12l2a: parameters["trs_l2a"] = manager.open_array(b12l2a)[2]
                    case "Red_NDVI_Thresholder":
                        print(var_name, filename, ext)
                        manager.update_assetios(var_name, filename, ext, 'input')
                        nb4 = input_tiff["Red_NDVI_Thresholder"] 
                        if nb4: parameters["trs_arb"] = manager.open_array(nb4)[2]
                    case "normalized_IC":
                        manager.update_assetios('normalized_IC', filename, 'tiff', 'output')
                        dsm = output_tiff["normalized_IC"]
                        if dsm: parameters["trs_csi"] = manager.open_array(dsm)[2]
                    case "dNBR":
                        manager.update_assetios('dNBR', filename, 'tiff', 'output')
                        dNBR = output_tiff["dNBR"]
                        if dNBR: parameters["trs_l2a"] = manager.open_array(dNBR)[2]
                    case "Vegetation_Recovery_Factor":
                        manager.update_assetios("VRf", filename, 'tiff', 'output')
                        nb4 = output_tiff["VRf"]
                        if nb4: parameters["trs_arb"] = manager.open_array(nb4)[2]
                    case "Custom_W":
                        manager.update_assetios("W_Index", filename, 'tiff', 'output')
                    case "Custom_Variable":
                        manager.update_assetios("Custom_Variable", filename, 'tiff', 'input')
                    case "DISCONNECTING_INDEX_shapefile":
                        manager.update_assetios('DISCSHAPE', filename, 'shp', 'input')
                    case "DISCONNECTING_INDEX_raster":
                        manager.update_assetios('DISCONNECTING_INDEX', filename, 'tiff', 'input')
                    case "PFES":
                        print(var_name, filename, ext)
                        manager.update_assetios(var_name, filename, ext, 'output')
                        pfestif = output_tiff["PFES"]
                        if pfestif: parameters["trs_pfes"] = manager.open_array(pfestif)[2]
                    case "Output_Directory":
                        select_outdir()
                    case _:
                        print(var_name, filename, ext)
                        manager.update_assetios(var_name, filename, ext, 'input')

                print(f"Raw file path for {label}: {filename}")
                              
    # ---------------------------------------------------------
    # 2. MAIN LAYOUT (Left & Right Frames)
    # ---------------------------------------------------------
    
    color_themes = {
        "setup":    ("#A0A0A0", "#404040"), 
        "IC":       ("#9575CD", "#512DA8"), 
        "BA":       ("#FFA726", "#E65100"), 
        "gDI":      ("#42A5F5", "#0D47A1"), 
        "VRF":      ("#66BB6A", "#1B5E20"), 
        "CF":       ("#26A69A", "#00695C"), 
        "FIREX":    ("#EF5350", "#C62828"), 
        "default":  (button_color, "#14375e") 
    }

    # Frame canvas
    canvas_frame = ctk.CTkFrame(root, fg_color=panel_color, border_width=0)
    canvas_frame.pack(fill="both", expand=True, padx=0, pady=0)

    canvas = ctk.CTkCanvas(canvas_frame, bg=panel_color, bd=0, highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)

    yscrollbar = ctk.CTkScrollbar(canvas_frame, command=canvas.yview)
    yscrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=yscrollbar.set)

    content_frame = ctk.CTkFrame(canvas, fg_color="transparent")
    canvas.create_window((0, 0), window=content_frame, anchor="nw")

    def update_scrollregion(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))

    content_frame.bind("<Configure>", update_scrollregion)

    # ---------------------------------------------------------
    # 3. LEFT FRAME (Smart Buttons)
    # ---------------------------------------------------------
    left_frame = ctk.CTkFrame(content_frame, fg_color=panel_color)
    left_frame.pack(side="left", padx=10, pady=10, fill="both", expand=False)

    # Manteniamo la tua mappatura personalizzata
    left_buttons_text = [
        ("Preliminary\nOperations", "function", "file_manager", "setup", None),
        ("Select the\nProcessed Files\nDirectory", "function", "select_outdir", "setup", "out_fold"),
        ("Select\nDEM", "tiff", ".tif", "IC", "DEM"),
        ("Select\nSTUDY AREA", "shp", "shp", "IC", "STUDY_AREA"),
        ("Select\nROADS", "shp", "shp", "IC", "ROADS"),
        ("Select\nDEMROAD", "tiff", "tiff", "IC", "DEMROAD"),
        ("Select\nCustom W", "tiff", ".tif", "IC", "W_Index"),
        ("Select\nDISCONNECTING\nINDEX\nshapefile", "shp", "shp", "gDI", "DISCSHAPE"),
        ("Select\nPREFIRE\nNIR", "JPEG 2000", ".jp2", "BA", "PREFIRE_NIR"), 
        ("Select\nPREFIRE\nSWIR","JPEG 2000", ".jp2", "BA", "PREFIRE_SWIR"), 
        ("Select\nPOSTFIRE\nNIR", "JPEG 2000", ".jp2", "BA", "POSTFIRE_NIR"), 
        ("Select\nPOSTFIRE\nSWIR", "JPEG 2000", ".jp2", "BA", "POSTFIRE_SWIR"),
        ("Select\nRed NDVI\nThresholder", "JPEG 2000", ".jp2", "VRF", "Red_NDVI_Thresholder"), 
        ("Select\nNIR NDVI\nThresholder", "JPEG 2000", ".jp2", "VRF", "NIR_NDVI_Thresholder"),
        ("Select\nCustom\nVariable", "tiff", ".tif", "CF", "Custom_Variable"),
        ("Select\nnormalized IC", "tiff", ".tif", "FIREX", "normalized_IC"),
        ("Select\ndNBR", "tiff", ".tif", "FIREX", "dNBR"),
        ("Select\nDISCONNECTING\nINDEX raster", "tiff", ".tif", "FIREX", "DISCONNECTING_INDEX"),
        ("Select\nVegetation\nRecovery\nFactor", 'tiff', '.tiff', "FIREX", "VRf"),  
        ("Help\n&\nAbout", "function", "about", "default", None)
    ]

    def create_smart_button(index, button_data):
        text, ext, f_type, theme_key, dict_key = button_data
        row = index // 5
        col = index % 5
        
        # 1. Recupera colori
        light_c, dark_c = color_themes.get(theme_key, color_themes["default"])
        
        # 2. Logica STATO INIZIALE
        start_color = light_c
        try:
            is_loaded = False
            if dict_key:
                if dict_key in input_tiff and input_tiff[dict_key]: is_loaded = True
                elif dict_key in output_tiff and output_tiff[dict_key]: is_loaded = True
                elif dict_key in input_shp and input_shp[dict_key]: is_loaded = True
                elif dict_key in parameters and parameters[dict_key]: is_loaded = True
            
            if is_loaded:
                start_color = dark_c
        except Exception as e:
            pass 

        button = ctk.CTkButton(
            left_frame,
            text=text,
            font=font_style,
            width=100,
            height=100,
            fg_color=start_color 
        )
        
        button.configure(command=lambda: browse(button, text, ext, f_type, dark_c, dict_key))
        button.grid(row=row, column=col, columnspan=1, padx=10, pady=10, sticky="nsew")

        # --- MONITORAGGIO ---
        # Se la chiave del bottone è nella lista target, salviamo il riferimento
        if dict_key in TARGET_KEYS:
            monitored_buttons[dict_key] = button

    for i, data in enumerate(left_buttons_text):
        create_smart_button(i, data)

    # Configurazione Griglia Left
    for i in range(5): 
        left_frame.grid_columnconfigure(i, weight=1, minsize=120)
    num_rows = (len(left_buttons_text) // 5) + 1
    for i in range(num_rows):
        left_frame.grid_rowconfigure(i, weight=1,minsize=120)


    # ---------------------------------------------------------
    # 4. RIGHT FRAME (Bilanciato e Coerente con Left)
    # ---------------------------------------------------------
    right_frame = ctk.CTkFrame(content_frame, fg_color=panel_color)
    right_frame.pack(side="right", padx=10, pady=10, fill="x", expand=False, anchor="n")

    c_blue   = color_themes["gDI"][1] 
    c_purple = color_themes["IC"][1] 
    c_teal   = color_themes["CF"][1] 
    c_orange = color_themes["BA"][1] 
    c_green  = color_themes["VRF"][1] 
    c_red    = color_themes["FIREX"][1] 

    def buttfunction(label, funtzione):
        # Funzione interna che esegue i calcoli (il "lavoro sporco")
        if label == "DEMROAD Crafter" and funtzione == "funtz": 
            roadmask.roadmask()
        elif label == "Sediment Connectivity\n Calculator" and funtzione == "funtz":
            csi.aberi_ic()
        elif label == "Burnt Area\nAnalyzer" and funtzione == "funtz":
            burntareanalyzer.fogu()
        elif label == "Sediment\nDisconnector" and funtzione == "funtz":
            disc.disconnector()
        elif label == "NDVI\nThresholder" and funtzione == "funtz":
            ndvithresholder.arbures()
        elif label == "Custom Variables\nApplier" and funtzione == "funtz":
            customvariable.scc()
        elif label == "Postfire Erosion Susceptibility Map Crafter" and funtzione == "funtz":
            PFES.pfes()

            
    right_buttons_text = [
        ("DEMROAD Crafter", "funtz", "#512DA8"),            
        ("Sediment Connectivity\n Calculator", "funtz", "#512DA8"), 
        ("Sediment\nDisconnector", "funtz", "#0D47A1"),     
        ("Burnt Area\nAnalyzer", "funtz", "#E65100"),     
        ("NDVI\nThresholder", "funtz", "#1B5E20"),         
        ("Custom Variables\nApplier", "funtz", "#00695C")   
    ]

    btn_height_right = 128 

    for i, (textr, funtz, btn_col) in enumerate(right_buttons_text):
        row = i // 2  
        col = i % 2   
        button = ctk.CTkButton(
            right_frame,
            text=textr,
            font=font_style,
            width=96,
            height=btn_height_right, 
            fg_color=btn_col,
            command=lambda label=textr, funtzione=funtz: buttfunction(label, funtzione)
        )
        button.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

    postfire_button = ctk.CTkButton(
        right_frame,
        text="Postfire\nErosion\nSusceptibility\nMap Crafter",
        font=font_style,
        width=120, 
        height=btn_height_right, 
        fg_color="#C62828",          
        command=lambda label="Postfire Erosion Susceptibility Map Crafter", funtzione="funtz": buttfunction(label, funtzione)
    )
    
    postfire_button.grid(row=0, column=2, rowspan=3, padx=10, pady=10, sticky="nsew")

    for i in range(3): 
        right_frame.grid_columnconfigure(i, weight=1, minsize=110)
    
    for i in range(3): 
        right_frame.grid_rowconfigure(i, weight=0, minsize=btn_height_right + 20) 

    def update_scroll_region(event=None):
        canvas.config(scrollregion=canvas.bbox("all"))

    content_frame.bind("<Configure>", update_scroll_region)

    # AVVIA L'ANNOADORE (REFRESH AUTOMATICO)
    annoadore(root)

    root.mainloop()

#_____________________________END OF THE GUI________________________________________________________________________
