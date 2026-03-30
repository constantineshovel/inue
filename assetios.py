# DISCLAIMER OF LIABILITY:
# This software is provided "as is", without any warranty
# The author is not responsible for any damages resulting from its use
#LICENSE:
# This file is part of INUE - INteractive and Userfriendly Emergency tool for burnt areas v. 1.0.0 'άλφα, released under the GNU Affero General Public License v3.
# See the LICENSE file or https://www.gnu.org/licenses/agpl-3.0.html for more details.
#Copyright Costantino Pala © 2025
#This file was created in the framework of a PhD funded by CNR-IRPI-PG and DSCG-UNICA

#Assetios holds dictionaries and general settings allowing them to be available to every module. Assetios = settings, configuration, in Sardinian obviously :)
#File_manager.py has a function useful to update the following dictionaries. 
import os

parameters = {
    "sistema": None, #Windows or Linux, comes from INUE.py
    "coro": os.cpu_count(), #number of cores of your machine
    "resolution": None, #Preliminary operations > Set Resolution
    "epsg": None, #Preliminary Operations > Set EPSG
    "trs_csi": None, #Affine for Consedinx. Is defined in GUI (match and case for the inputs..)
    "trs_l2a": None, #Affine for Fogu (Burnt Area Analyzer).  Is defined in GUI (match and case for the inputs..)
    "trs_arb": None,#Affine for Arbures (NDVI thresholder).  Is defined in GUI (match and case for the inputs..)
    "trs_pfes": None,#Affine for PFES.  Is defined in GUI (match and case for the inputs..)
    "ndvi_thr": None, #threshold useful to perform Vegetation recovery disconnection
    "out_fold": None, #output directory. GUI > Select Processed Files Directory
    "Algorithm": "D∞", #Was linked to a previous switcher to allow the use of D8 or Dinf while calculating sediment connectivity index. 
    "W Index": 'Default', #W index switcher. The default setting is to use the Cavalli et al 2008 RI
    "Area Configuration": "Postfire", #The area is recently burnt or is experiencing a significative postfire vegetation growth (the so called vegetation regrowth..)?
    "Disconnecting Landforms": "No", #Does terraces or similar landforms exist in the area?
    "Demroad": "On"#Do you want to consider the effect of roads? If yes, you must calculate DEMROAD with the DEMROAD crafter, if not DEMROAD = DEM. 
    }

#Dictionary storing the paths for TIFF input files loaded from left panel

input_tiff = { 
    "DEM": None,
    "DEMROAD": None,
    'roadmask': None,
    "PFES": None,
    "PREFIRE_NIR": None,
    "PREFIRE_SWIR": None,
    "POSTFIRE_NIR": None,
    "POSTFIRE_SWIR": None,
    "Red_NDVI_Thresholder": None, #Sentinel 2 L2A image for vegetation recovery
    "NIR_NDVI_Thresholder": None, #Sentinel 2 L2A image for vegetation recovery
    "DISCONNECTING_INDEX": None, #raster of disconnected areas.
    "Custom_Variable": None #raster for optional input
    }

#Dictionary storing the paths for SHP input files loaded from left panel
input_shp = {
    "ROADS": None,#roads raster for roadmask
    "STUDY_AREA": None,#mask raster for roadmask
    "DISCSHAPE": None#areas with sediment disconnected by landforms
    }

#Dictionary storing the paths of some outputs which are useful for further processing....

output_tiff = {
    "IC": None,
    "normalized_IC": None,
    "dNBR": None,
    "dNBR+": None,
    "Burn Severity Map": None,
    "rBS": None,#reclassified burn severity (1-->5). 
    "Wildfire_Perimeter": None,
    "NDVI": None,
    "VRf": None, #the raster tiff of NDVI threshold to take into account vegetation recovery 
    "PFES": None, #pfes obtained by postfire and no disconnecting landforms configuratio, without vegetation recovery
    "DPFES": None, #pfes obtained immediately after fire, without vegetation recovery but disconnecting landforms are present
    "PFESVRT": None, #pfes obtained after vegetation recovery. disconnecting landform can be present or absent
    "PFESDVRT": None, #pfes for burned area disconnected after vegetation recovery
    "PFESOP": None, #pfes with optional input
    "W_Index": None #the W index for IC computation. It is calculate dby consedinx if default W is choosen (W by Cavalli et al 2008 procedure) or is the customized W loaded by the user.
    }
