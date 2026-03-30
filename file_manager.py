# DISCLAIMER OF LIABILITY:
# This software is provided "as is", without any warranty
# The author is not responsible for any damages resulting from its use
# LICENSE:
# This file is part of INUE - INteractive and Userfriendly Emergency tool for burnt areas v. 1.1 'άλφα, released under the GNU Affero General Public License v3.
# See the LICENSE file or https://www.gnu.org/licenses/agpl-3.0.html for more details.
# Copyright Costantino Pala © 2025
# This file was created in the framework of a PhD funded by CNR-IRPI-PG and DSCG-UNICA
# Written by me, with coding support and suggestions from ChatGPT.

import customtkinter as ctk#GUI library.. here is used to manage the Preliminary Operation GUI
import numpy as np#....
import dask.array as da#Array management with multiprocessing
import os#File and OS management
import sys#OS parameters
from PIL import Image#Image management
import rasterio#Raster management
import rasterio.mask as mask#Raster masking
import rasterio.warp#Geospatial transformation of rasters
from rasterio.features import shapes#raster polygonization
from rasterio.windows import from_bounds#Creates a raster window from coordinates
from rasterio.transform import from_origin#Calculates raster transform
from rasterio.crs import CRS#Raster Coordinate Reference System 
import geopandas as gpd#Vectorial data management
from tkinter import filedialog, messagebox#GUI dialogs from tkinter
import subprocess#To load external processes
from dask_image.ndfilters import sobel, convolve#Image filters
from assetios import parameters#A dictionary from Assetios.py holding INUE parameters
import assetios#A module holding OS and INUE parameters, I/O paths
import psutil#OS resources monitoring
from scipy.ndimage import convolve#Image filter from scipy

# File Manager stores 99% of the functions used across the INUE modules.
# It contains functions to open, save, and manage both raster and vector data.
# Additionally, it includes functions useful for performing raster operations.
# The GUI and functions for the Preliminary Operations module are also stored here.
# File Manager's functions are highly generic and can be reused in other software dealing with raster data.
# SC = Sardinian | EN = English

#===================================================================================================
#                                               MODULES TO LOAD, OPEN AND SAVE
#===================================================================================================

#Function to load the files.. it is used in the Left panel of the GUI
def load_file(entry):
    try:
        filepath = filedialog.askopenfilename(filetypes=[ ("All files", "*.*"), ("JPEG2000 files", "*.jp2"), ("TIFF files", "*.tif"), ("ASC files", "*.asc")])
        if filepath:
            entry.delete(0, ctk.END)
            entry.insert(0, filepath)
            with rasterio.open(filepath) as src:
                raster_data = src.read(1)
                transform = src.transform
                print(f"Loaded raster with shape {raster_data.shape}, Transform: {transform}")
            return raster_data
        else:
            print("No file selected.")
            return None, None
    except Exception as e:
        print(f"Error loading file: {e}")
        return None, None

#Function called when hitting GUI > Select Output Directory
def load_directory(entry):
    dirpath = filedialog.askdirectory()
    if dirpath:
        entry.delete(0, ctk.END)
        entry.insert(0, dirpath)

#Function to open raster files as array        
def open_array(file):
    try:
        filename = os.path.splitext(os.path.basename(file))[0]
        with rasterio.open(file) as rd:
            rdar = rd.read(1)
            otrs = rd.transform
        return rd, rdar.astype(float), otrs
    except Exception as e:
        print(f"Error opening file {file}: {e}")
        return None, None

#Function to save array as raster
def save(result, otn, resolution, epsg, otrs):
    global output_folder
    output_folder = parameters["out_fold"]
    #Checks if the array is dask or numpy
    if isinstance(result, da.Array):
        #if the array is a dask_array it will be converted to numpy array. This operation is mandatory to save the result 
        result = result.compute()#Dask array ------> Numpy array
    elif not isinstance(result, np.ndarray):
        raise ValueError("Result must be a numpy or dask array.")
    
    #otn is the name of the raster.. 
    outname = f'{otn}.tif'
    outtif = os.path.join(output_folder, outname)

    #calculates some statistics for raster... also because it is useful in the INUE workflow!
    mean_val = np.nanmean(result)
    min_val = np.nanmin(result)
    max_val = np.nanmax(result)
    std_val = np.nanstd(result)
    np.nan_to_num(result, -9999, -9999, -9999)

    #building the CRS
    crs = CRS.from_epsg(epsg)

    #metadata writing
    metadata = {
        'mean': mean_val,
        'min': min_val,
        'max': max_val,
        'std': std_val
    }

    try:
        #saves raster as geotiff
        with rasterio.open(
            outtif,
            'w',
            driver='GTiff',
            height=result.shape[0],
            width=result.shape[1],
            count=1,  #one band only
            dtype='float32',  #data type
            crs=crs,
            transform=otrs,
            nodata=-9999,  
            metadata=metadata,  #changes the metadata
        ) as dst:
            dst.write(result, 1)  #writes the array in the first band of the raster.. (1)

        print(f"Raster saved as {outtif}")
    except Exception as e:
        print(f"Error saving raster: {e}")
        

def update_assetios(output_name, file_path, file_type, io_type):#this function updates the assetios dictionaries
    """
    SC
    Annoat sos ditzionarios de sos archivios de input e de output cun su tretu tzeneradu

    Parametros:
        output_name (str): est sa crae de su ditzionariu
        file_path (str): su tretu intreu de s'archiviu tzeneradu.
        file_type (str): sa calidade de s'archiviu ('tiff' o 'shp').
        io_type (str): sa calidade de s'annou ('input' o 'output').
    
    Nche Torrat:
        bool: True si at annoadu, False si no b'est resurtadu.
    EN
    Uploads the dictionaries for parameters, input and output paths

    Parameters:
        output_name(str): dictionary key
        file_path: the file path
        file_type: the file type
        io_type: manages if the dictionary is for an input or output file

    Outputs:
        bool: True if the update was successful, False otherwise
    """
    #dictionary selection based on Input or Output
    if io_type == "output":
        if file_type == "tiff" or file_type == "JPEG 2000":
            target_dict = assetios.output_tiff
        elif file_type == "shp":
            target_dict = assetios.output_shp
        else:
            print(f"Error: filetype '{file_type}' is not handled by output dictionary.")
            return False
    elif io_type == "input":
        if file_type == "tiff" or file_type == "JPEG 2000":
            target_dict = assetios.input_tiff
        elif file_type == "shp":
            target_dict = assetios.input_shp
        else:
            print(f"Error: filetype '{file_type}' is not handled by input dictionary.")
            return False
    else:
        print(f"Error: '{io_type}' is not valid.")
        return False

    #this algorithm checks if the selected key exists in the dictionary
    if output_name in target_dict:
        target_dict[output_name] = file_path
        print(f"Dictionary {io_type} uploaded: {output_name} -> {file_path}")
        return True
    else:
        print(f"Dictionary: '{output_name}' not found in the dictionary {target_dict}.")
        return False


def shapadore(raster_path, shapefile_path, epsg):#function useful for raster polygonization... 
    """
    SC
    Nche bortat unu raster a shapefile.
    
    Parametros:
    - raster_path: Tretu de su raster de nche bortare. Raster path
    - shapefile_path: Tretu in ue nche depes ammentare su shapefile. Path where you want to save the shapefile
    - epsg: EPSG de su sistema de sas coordinadas (es. EPSG:32632).

    Nche Torrat:

    Su shapefile

    EN
    Function useful to convert a raster into a shapefile

    Inputs:
    raster_path: the path of the raster to convert
    shapefile_path_ the path where the shapefile will be stored
    epsg: the epsg of the coordinate system (es: EPSG: 32632)

    Output:
    
    The shapefile
    
    """
    with rasterio.open(raster_path) as src:
        image = src.read(1)  
        transform = src.transform
        nodata = src.nodata  

        results = [
            {"properties": {"value": v}, "geometry": s}
            for s, v in list(shapes(image, transform=transform))
            if np.isclose(v, 1) and (nodata is None or not np.isclose(v, nodata))
        ]

        gdf = gpd.GeoDataFrame.from_features(results, crs=f"EPSG:{epsg}")

        gdf.to_file(shapefile_path, driver="ESRI Shapefile")

    print(f"Shapefile succesfully created: {shapefile_path}")






#===================================================================================================
#                                               MODULE FOR MEMORY OPTIMIZATION
#===================================================================================================
def calculate_chunk_size(dtype=np.float32, target_memory_fraction=0.5, max_chunk_size=1000):
    """
    SC
    Assettat sa mannaria de sos chunks in d-una manera chi sa machina no s'atoghet, impreande bene sa memoria sua
    
    Parametros:
        dtype (np.dtype): su tipu de s'array: su de base est np.float32.
        target_memory_fraction (float): su peschentu de sa memoria chi si podet impreare pro sos chunks. Su de base est a su 50% (0.5).
        max_chunk_size (int): sa prus manna mannaria permitida pro sos chunks: (e.g., 1000x1000). Est a tenore de sa memoria chi tenet libera sa machina.
        
    Nche Torrat:
        chunk_size (tuple): Sa mannaria de sos chunks, che a una tupla (e.g., (500, 600)).
    EN

        This function manages the size of the chunks for dask array. Size management is based on available memory in the system.

        Parameters:
        dtype (np.dtype): type of the array... The type is np.float32 by default
        target_memory_fraction (float): is the percentage of memory available for chunking.. Default is 50% (0.5)
        max_chunk_size (int): is the maximum chunk size allowed... It depends by the memory available in the machine

        Output:
        chunk_size (tuple): is the chunk size as a tuple. e.g.: (500, 600)
    """
    total_memory = psutil.virtual_memory().total  # In bytes
    target_memory = total_memory * target_memory_fraction
    element_size = np.dtype(dtype).itemsize  # Size in bytes per element
    chunk_area = target_memory // element_size  # Number of elements per chunk
    
    # Here we allow for non-square chunks, calculating width and height separately
    chunk_width = int((chunk_area / 2) ** 0.5)  # For example, calculate width and height with a 2:1 ratio
    chunk_height = chunk_area // chunk_width  # The height is adjusted based on the width
    
    if chunk_width > max_chunk_size:
        chunk_width = max_chunk_size
        chunk_height = chunk_area // chunk_width  # Recalculate the height
    
    return (chunk_width, chunk_height)

#===================================================================================================
#                                               MODULES FOR OPERATIONS BETWEEN ARRAYS
#===================================================================================================
def array_calculator(iarray1, iarray2, operation, resolution, epsg, otrs, otn='None'):
    
    """
    SC
    Custa funtzione faghet operatziones intra Raster o costantes impreande protzedimentos paralleos cun Dask. Retzit sa mannaria majore chi si podet impreare, mudat sos array a dask (si esseret serbidu)
    e faghet sas operatziones.. Si nc'assetas unu nomene pro su raster l'as a ammentare in sa memoria.. Si no nche l'assettas no as a ammentare raster perunu.
    

    Parametros in bintrada

    iarray1 = unu raster o unu numeru
    iarray2 = unu raster o unu numeru
    operation = s'operatzione chi cheres faghere...
        sum = summa
        difference = diferéntzia
        times = multíprica
        division = partidura
    resolution = sa risolutzione de su file
    epsg = s'epsg
    otrs = sa transforme
    otn (istringa) = su nomene de su file, si l'esseres crefidu ammentare in sa memoria.. e.g.: 'nomene_de_su_raster'

    Nche Torrat

   Si otn != 'None':
   resurtadu = array_calculator(array1, array2, operatzione, risoluzione, epsg, otrs, 'nomene')
   resurtadu = ('C:/Users/Constantine/Desktop/MyFolder/nomene.tif', [0,1,2,3])
   resurtadu[0] = 'C:/Users/Constantine/Desktop/MyFolder/nomene.tif'
   resurtadu[1] = [0,1,2,3]

   Si otn== None:
   resurtadu = array_calculator(array1, array2, operatzione, risoluzione, epsg, otrs)
   resurtadu = [0,1,2,3]

   EN
   This function allow to manage raster operations using parallel processing with dask. It uses the maximum chunk size allowed by the machine, converts the numpy array to a dask array (if the case)
   and manages the desidered mathematical operations...If you set a name (otn) you will save the result as a raster. If you leave otn = None no raster will be saved.

   Input parameters:
   
    iarray1 = raster or number
    iarray2 = raster or number
    operation = the desired operation
        sum = sum
        difference = difference
        times = moltiplication
        division = division
    resolution = file resolution
    epsg = epsg
    otrs = transform
    otn (string) = if you want to save the result, write a name for the output raster.. e.g.: 'raster1'

    Output

   If otn != 'None':
   resurtadu = array_calculator(array1, array2, operatzione, risoluzione, epsg, otrs, 'name')
   resurtadu = ('C:/Users/Constantine/Desktop/MyFolder/name.tif', [0,1,2,3])
   resurtadu[0] = 'C:/Users/Constantine/Desktop/MyFolder/name.tif'
   resurtadu[1] = [0,1,2,3]

   If otn== None:
   resurtadu = array_calculator(array1, array2, operatzione, risoluzione, epsg, otrs)
   resurtadu = [0,1,2,3]

    """
    chdx, chsx = calculate_chunk_size(dtype=np.float32, target_memory_fraction=0.5, max_chunk_size=1000)
    match iarray1:
        case np.ndarray():
            array1 = iarray1.astype(np.float32)
            array1 = da.from_array(iarray1, chunks=(chdx, chsx))
        case da.Array():
            array1 = iarray1
        case int():
            array1 = iarray1
        case float():
            array1 = iarray1
    match iarray2:
        case np.ndarray():
            array2 = iarray2.astype(np.float32)
            array2 = da.from_array(iarray2, chunks=(chdx, chsx))
        case da.Array():
            array2 = iarray2
        case int():
            array2 = iarray2
        case float():
            array2 = iarray2

    try:
        if isinstance(array1, (np.ndarray, da.Array)) and isinstance(array2, (np.ndarray, da.Array)):
            #check the array shape is the same. this is mandatory
            if array1.shape != array2.shape:
                raise ValueError("Arrays must have the same shape for the operation.")
    except ValueError as e:
        messagebox.showerror("Error", str(e))

    global output_folder
    output_folder = parameters['out_fold']

    if operation == 'sum':
        result = array1 + array2
    elif operation == 'difference':
        result = array1 - array2
    elif operation == 'times':
        result = array1 * array2
    elif operation == 'division':
        result = array1/array2

    if otn != 'None':
        result.compute()  #dask to numpy conversion.. needed for saving the file
        save(result, otn, resolution, epsg, otrs)
        otif = otn + '.tif'
        resultif = os.path.join(output_folder, otif)
        return resultif, result #if otn != None outputs a path and a array pointer
    else:
        return result.compute() #outputs an array numpy only if otn = None



def slope(demar):

    """
    SC
    Calculat sa pendente.

    Parametros:

    demar = unu dem abertu che a array dask

    Nche Torrat:

    unu raster de sa pendente

    EN
    Calculates the slope.

    Inputs:

    demar = a DEM open as a dask array

    Outputs:

    a slope raster

    """
    chdx, chsx = calculate_chunk_size(dtype=np.float32, target_memory_fraction=0.5, max_chunk_size=1000)
    #nche lu mudat a dask array
    demar_dask = da.from_array(demar, chunks=(chdx, chsx))  

    #calculat su gradient cun sobel
    grad_x = sobel(demar_dask, axis=0)
    grad_y = sobel(demar_dask, axis=1)

    #calculat sa pendentzia in radiantes
    slope = da.arctan(da.sqrt(grad_x**2 + grad_y**2))

    # Kernel pro sa media mobile 3 pro 3
    kernel = da.ones((3, 3)) / 9  

    #Convolutzione
    slopesmooth = convolve(slope, kernel, mode="nearest")

    #Cunversione a grados
    slope_degrees = da.degrees(slopesmooth)

    return slope_degrees  #est un'array dask



def fentana(arr, funtz, epsg=None, otrs=None, resolution=None, window_size=5):
    """
    SC
    Nche movet una fentana in d-un'array Dask pro calculare sa média o sa cansàda istandard
    
    Parametros:
    - arr: s'array NumPy o Dask inue nche depes movere sa fentana
    - funtz: sa funtzione de nc'applicare (da.mean o da.std).
    - epsg: codighe EPSG.
    - otrs: su sistema de riferimentu.
    - resolution: risolutzione ispatziale.
    - window_size: sa mannaria de sa fentana.
    
    Nche Torrat:
    - Un'array dask cun su risultadu de s'operatzione.

    EN

    Applies a moving window over a dask array to calculate mean or standard deviation.

    Parameters:
    -arr: the numpy or dask array over you want to apply the moving window
    -funtz: the function to apply (da-mean or da.std)
    -epsg: the epsg code
    -otrs: the reference system
    -resolution: the resolution
    -window_size: the size of the moving window

    Output:
    An array dask with the result of the operation
    """
    
    if funtz not in [da.mean, da.std]:
        raise ValueError("The function must be da.mean or da.std")
    
    if not isinstance(arr, da.Array):
        chdx, chsx = calculate_chunk_size(dtype=np.float32, target_memory_fraction=0.5, max_chunk_size=1000)
        arr = da.from_array(arr, chunks=(chdx, chsx))

    arr = arr.astype(np.float32)
    #creates a kernel for the moving window
    kernel = np.ones((window_size, window_size)) / (window_size ** 2)

    #obtains a local mean
    mean_local = convolve(arr, kernel, mode='reflect')

    #Match and case
    match funtz:
        case da.mean:
            return mean_local
        case da.std:
            mean_squared_local = convolve(arr**2, kernel, mode='reflect')
            return da.sqrt(mean_squared_local - mean_local**2)




#===================================================================================================
#                                               MODULES USED IN THE FILE MANAGER GUI
#===================================================================================================

def set_resolution(resolution_entry):
    """
    SC: serbit a nc'assettare sa risoluzione de usare in INUE
    EN: manages the resolution to use in INUE
    """
    global resolut
    try:
        resolut = float(resolution_entry.get())
        parameters["resolution"] = resolut
        if resolut <= 0:
            raise ValueError("Resolution must be a positive number.")
        print(f"Final resolution is set to", parameters["resolution"])
        return parameters["resolution"]
    except ValueError:
        messagebox.showerror("Error","Invalid resolution. Please enter a valid positive number.")
        return None  


#Funtzione pro nc'assettare s'EPSG
def set_epsg(epsg_entry):
    """
    SC: serbit a nc'assettare s'EPSG de usare in INUE
    EN: manages the EPSG to use in INUE

    """
    global epsg
    epiessegi = epsg_entry.get()
    parameters["epsg"] = epiessegi
    print(f"EPSG is set to", parameters["epsg"] )
    return parameters["epsg"]

#Fubtzione pro nc'assettare su limite NDVI
def set_thr(thr_entry):
    """
    SC: serbit a nc'assettare su nemenaxu pro su nmenaxadore de s'NDVI
    EN: manages the NDVi threshold
    """
    global thrs
    thrs = thr_entry.get()
    thr = float(thrs)
    parameters["ndvi_thr"] = thr
    print(f"NDVI threshold is set to", parameters["ndvi_thr"] )
    return parameters["ndvi_thr"]

def rastercutter(raster1_entry, raster2_entry, output_dir):
    """
    SC
    Custa funtzione serbit a segare unu raster a sa mannaria sa prus pitica.
    Nche leat duos raster in bintrada, unu depet essere prus mannu de s'ateru.
    Sa funtzione los ponet a pare pro cumprendere cal'est su prus piticu e cale su prus mannu.
    Su prus mannu benit segadu a tenore de su piticu pro tennere sa matessi mannaria sua e nche l'ammentat in su tretu in bessida.

    Parametros:
    raster1_entry: est unu raster
    raster2_entry: aterunu raster
    output_dir: su tretu in-ue nch'as a ammentare su raster segadu

    Nche Torrat:
    su raster prus mannu segadu a tenore de su piticu

    EN
    This function is useful to cut a raster to a smaller size.
    It loads two raster, one of them is larger.
    The function compares the raster size to understand which one is smaller.
    The bigger one is cutted at the extent of the smaller one and saves the result in the output folder.

    Parameters:
    raster1_entry: one raster
    raster2_entry: the other raster
    output_dir: the saving path

    Output:
    The bigger raster cutted at the extent of the smaller one
    """
    #Reads the raster name and stores it
    raster_name1 = os.path.splitext(os.path.basename(raster1_entry))[0]
    new_name1 = f"crop_{raster_name1}.tif"
    out_new_name1 = os.path.join(output_dir, new_name1)

    raster_name2 = os.path.splitext(os.path.basename(raster2_entry))[0]
    new_name2 = f"crop_{raster_name2}.tif"
    out_new_name2 = os.path.join(output_dir, new_name2)
    try:
        #Loads the two rasters
        with rasterio.open(raster1_entry) as src1, rasterio.open(raster2_entry) as src2:
            #Measures their size
            bounds1 = src1.bounds
            bounds2 = src2.bounds

            #Compares the areas
            area1 = (bounds1.right - bounds1.left) * (bounds1.top - bounds1.bottom)
            area2 = (bounds2.right - bounds2.left) * (bounds2.top - bounds2.bottom)

            #Uses the smallest bounding box
            if area1 >= area2:#if raster1_entry is bigger...
                crop_bounds = bounds2
                larger_raster = src1
                larger_output = out_new_name1
            else:#if raster2_entry is bigger
                crop_bounds = bounds1
                larger_raster = src2
                larger_output = out_new_name2

            #final extent
            window = from_bounds(*crop_bounds, larger_raster.transform)

            #cutting!!!
            cropped_data = larger_raster.read(window=window)
            cropped_transform = larger_raster.window_transform(window)

            #reading metadata...
            meta = larger_raster.meta.copy()

            #and storing them in the final file
            meta.update({
                'driver': 'GTiff',
                "height": cropped_data.shape[1],
                "width": cropped_data.shape[2],
                "transform": cropped_transform
            })

        #saving the cutted raster 
        with rasterio.open(larger_output, 'w', **meta) as dst:
            dst.write(cropped_data)
        #OK, Done
        messagebox.showinfo("Success", f"Raster cropped and saved at {larger_output}")
    
    except Exception as e:
        #Error!
        messagebox.showerror("Error", f"Error cutting: {e}")




def resample(raster_path, resolution, output_dir):
    """
    SC
    Custa funtzione mudat sa risolutzione finale de su raster a sa chi as assettadu...

    Parametros:
    raster_path: su tretu de su raster de mudare a una risolutzione noa
    resolution: sa risolutzione finale chi cheres
    output_dir: su tretu in-ue nche l'ammentare

    Nche Torrat:

    Su raster cun sa risolutzione noa

    EN
    This function changes the final resolution of the raster to the one you choose

    Parameters:
    raster_path: the path of the raster to resample
    resolution: the final resolution
    output_dir: the path of the folder where you want to save the resampled file

    Outputs:

    The raster with the new resolution
    """
    rastername = os.path.splitext(os.path.basename(raster_path))[0]
    newname = f"resampled_{rastername}_{resolution}m_res.tif"
    out_newname = os.path.join(output_dir, newname)
    
    try:
        # Ensure resolution is an integer
        resolution = int(resolution)
        
        with rasterio.open(raster_path) as src:
            # Original transform and resolution
            transform = src.transform
            
            # Calculate the new transform based on the desired resolution
            new_transform = rasterio.Affine(
                resolution, transform.b, transform.c,
                transform.d, -resolution, transform.f
            )
            
            # Calculate the new width and height based on the resolution
            target_width = int(src.width * (src.res[0] / resolution))
            target_height = int(src.height * (src.res[1] / resolution))
            
            # Copy metadata and update it with the new transform, width, and height
            resampled_meta = src.meta.copy()
            resampled_meta.update({'driver': 'GTiff', "transform": new_transform, "width": target_width, "height": target_height, "crs": src.crs})

            resalg = rasterio.enums.Resampling.bilinear
            
            # Read the data with resampling applied
            data = src.read(
                out_shape=(src.count, target_height, target_width),
                resampling=resalg
            )

        # Write the resampled data to the output file
        with rasterio.open(out_newname, "w", **resampled_meta) as dst:
            dst.write(data)
        
        # Display success message
        messagebox.showinfo("Success", f"Resampled raster saved at {out_newname}")
    
    except Exception as e:
        # Show error message if something goes wrong
        messagebox.showerror("Error", f"Error during resampling: {e}")


#===================================================================================================
#                                                                       GUIDED USER INTERFACE
#===================================================================================================
def resource_path(relative_path):
    if getattr(sys, 'frozen', False):  # Se il programma è eseguito come .exe
        base_path = sys._MEIPASS  # PyInstaller estrae i file qui
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def file_manager():
    ctk.set_appearance_mode("light")
    window = ctk.CTk()
    window.title("INUE v1.1 άλφα - Preliminary Operations")
    window.geometry("500x600")
    # Define colors
    panel_color = "#ECEFF1"
    button_color = "#003366"
    
    sistema = parameters["sistema"]
    if sistema == 2:
        window.iconbitmap(resource_path("inue_YQZ_icon.ico"))
    elif sistema == 1:
        window.iconbitmap(resource_path("inue256.png"))     

    # Set the window background color
    window.configure(bg=panel_color)

    # Set Segoe UI font in bold
    font_style = ("Open Sans", 14)
    font_style_executor = ("Open Sans", 15, "bold", "italic")
    font_header = ("Open Sans", 16)

    # Top panel
    frame_top = ctk.CTkFrame(window, fg_color=panel_color)
    frame_top.pack(side='top', fill='both', expand=True, padx=10, pady=10)

    # Create a container frame for the entries and buttons, stacked vertically
    frame_entries = ctk.CTkFrame(frame_top, fg_color=panel_color)
    frame_entries.pack(side='top', fill='x', padx=5, pady=5)

    # EPSG Entry and Button (stacked vertically)
    epsg_entry = ctk.CTkEntry(frame_entries, width=200, placeholder_text="Type here...", placeholder_text_color='grey')
    epsg_entry.pack(side='top', pady=5)
    ctk.CTkButton(frame_entries, text="Set EPSG", font=font_style_executor, fg_color=button_color, command=lambda: set_epsg(epsg_entry)).pack(side='top', pady=5)

    # Resolution Entry and Button (stacked vertically below EPSG)
    resolution_entry = ctk.CTkEntry(frame_entries, width=200, placeholder_text="Type here...", placeholder_text_color='grey')
    resolution_entry.pack(side='top', pady=5)
    ctk.CTkButton(frame_entries, text="Set Resolution", font=font_style_executor, fg_color=button_color, command=lambda: set_resolution(resolution_entry)).pack(side='top', pady=5)

    # NDVI threshold for ARBURES Entry and Button (stacked vertically below Resolution)
    thr_entry = ctk.CTkEntry(frame_entries, width=200, placeholder_text="Type here...", placeholder_text_color='grey')
    thr_entry.pack(side='top', pady=5)
    ctk.CTkButton(frame_entries, text="Set NDVI Threshold", font=font_style_executor, fg_color=button_color, command=lambda: set_thr(thr_entry)).pack(side='top', pady=5)

   # Left panel (cropping)
    frame_right = ctk.CTkFrame(window, fg_color=panel_color)
    frame_right.pack(side="right", fill="both", expand=True, padx=10, pady=10)
    ctk.CTkLabel(frame_right, text="Cropping Tool").pack(pady=5)
    
    raster1_entry = ctk.CTkEntry(frame_right, width=200, placeholder_text="Type the path here...", placeholder_text_color='grey')
    raster1_entry.pack(pady=5)
    ctk.CTkButton(frame_right, font = font_style, fg_color=button_color, text="Select Raster", command=lambda: load_file(raster1_entry)).pack(pady=5)
    
    raster2_entry = ctk.CTkEntry(frame_right, width=200, placeholder_text="Type the path here...", placeholder_text_color='grey')
    raster2_entry.pack(pady=5)
    ctk.CTkButton(frame_right, font = font_style, fg_color=button_color, text="Select Raster", command=lambda: load_file(raster2_entry)).pack(pady=5)
    
    output_dir_entry = ctk.CTkEntry(frame_right, width=200, placeholder_text="Type the path here...", placeholder_text_color='grey')
    output_dir_entry.pack(pady=5)
    ctk.CTkButton(frame_right, font = font_style, fg_color=button_color, text="Select Output Folder", command=lambda: load_directory(output_dir_entry)).pack(pady=5)
    
    ctk.CTkButton(frame_right, font = font_style_executor, fg_color=button_color, text="Crop", command=lambda: rastercutter(raster1_entry.get(), raster2_entry.get(), output_dir_entry.get())).pack(pady=10)

    # Right panel (resampling)
    frame_left = ctk.CTkFrame(window, fg_color=panel_color)
    frame_left.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    ctk.CTkLabel(frame_left, text="Resampling Tool").pack(pady=5)
    
    resample_entry = ctk.CTkEntry(frame_left, width=200, placeholder_text="Type the path here...", placeholder_text_color='grey')
    resample_entry.pack(pady=5)
    ctk.CTkButton(frame_left, text="Select Raster", font=font_style, fg_color=button_color, command=lambda: load_file(resample_entry)).pack(pady=5)
    
    
    output_resample_entry = ctk.CTkEntry(frame_left, width=200, placeholder_text="Type the path here...", placeholder_text_color='grey')
    output_resample_entry.pack(pady=5)
    ctk.CTkButton(frame_left, text="Select Output Folder", font = font_style, fg_color=button_color, command=lambda: load_directory(output_resample_entry)).pack(pady=5)
    
    ctk.CTkButton(frame_left, text="Resample", font=font_style_executor, fg_color=button_color, command=lambda: resample(resample_entry.get(), resolution_entry.get(), output_resample_entry.get())).pack(pady=10)


    window.mainloop()
