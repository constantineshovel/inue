INUE v1.1 άλφα 🛰️🔥
INteractive and User-friendly Emergency tool for Postfire Erosion Susceptibility Mapping from Remote Sensing Data
INUE is a rapid assessment tool designed to map erosion susceptibility in postfire landscapes. Built on the SUBSTR8 platform, it allows for fast prioritization of at-risk watersheds using remote sensing data during the critical emergency phase.

⚠️ Important Warnings
 * Fast Assessment, Not Precision: INUE is intended for rapid prioritization and screening, not for high-precision physical or hydrological modeling.
 * Relative Connectivity: The tool measures relative susceptibility based on connectivity, not actual sediment fluxes or mass yields.
 * Use Cases: Ideal for identifying watersheds at risk immediately after a fire when field data is limited.
 * 
🔬 Methodology: The FIREX Index
The core of the tool is the FIREX index, which models postfire sediment dynamics by adjusting a stable Sediment Connectivity Index based on burn severity and landscape factors.
 * IC_{normalized}: Normalized Sediment Connectivity Index.
 * dNBR_{normalized}: Reclassified Burn Severity.
 * gDI: Geomorphologic Sediment Disconnection Index (for landforms like terraces).
 * VRf: Sediment Disconnection due to Vegetation Recovery.
 * cf: Local variables or triggering phenomena (optional).
 * 
🛠️ System Requirements
 * OS: Windows 10/11 (64-bit).
 * CPU: Dual-Core 3.10 GHz or equivalent.
 * RAM: 8 GB.
 * Mandatory Software: TauDEM v5.3.7 or higher.
 * Input Data: DEM (10m to 1m resolution suggested), Study Area Shapefile, Road Network Shapefile, and NIR/SWIR satellite imagery (Sentinel-2 or Landsat).
 * 
🚀 Workflow
 * Preliminary Operations: Set the EPSG, Spatial Resolution, and NDVI Threshold. Use the Resample and Crop tools to ensure all input rasters match in extent and resolution.
 * Module Execution: Run the DEMROAD Crafter, Sediment Connectivity Calculator, and Burnt Area Analyzer plus the additional indexes for sediment disconnection as required by your analysis 
 * Hazard Scenario (HS) Selection: Configure the GUI switchers to match your area's local conditions (vegetation recovery and/or landforms).
 * Final Map: Generate the Postfire Erosion Susceptibility map - FIREX.
 * 
Hazard Scenarios (HS)
| Scenario | Configuration | Disconnecting Landforms | Description |
|---|---|---|---|
| HS1 | Postfire | No | Bare burned area or sparse regrowth. |
| HS2 | Postfire | Yes | Burned area with terraces or retaining structures. |
| HS3 | Veg. Recovery | No | Areas with significant dense vegetation regrowth. |
| HS4 | Veg. Recovery | Yes | Terraced slopes with dense vegetation recovery. |

🔍 Quick Guide for interpretation

*Sampling: Identify the highest FIREX values for HS1 or HS2 scenarios in areas immediately outside the burned perimeter (unburned/vegetated conditions).

*Safety Threshold: These values define the Safety Threshold and the lower limit for the low-susceptibility class within the burned area.

*Hazard Assessment: * Values > Safety Threshold: Indicate higher susceptibility.

*Proportionality: The higher the value, the higher the susceptibility.

📄 License & Contact
 * License: GNU Affero General Public License v3.0 (AGPL-3.0).
 * Developer: Costantino Pala (Geoscientist, GIS Specialist, PhD)
 * Contact: costantino.pala.geo@proton.me
 * 
📚 Bibliography
 * Borselli, L., Cassi, P., & Torri, D. (2008). Prolegomena to sediment and flow connectivity in the landscape. Catena, 75(3), 268–277.\n
*Cavalli, M., Tarolli, P., Marchi, L., & Dalla Fontana, G. (2008). The effectiveness of airborne LiDAR data in the recognition of channel-bed morphology. CATENA, 73(3), 249–260. https://doi.org/10.1016/j.catena.2007.11.001\n
*Cavalli, M., Trevisani, S., Comiti, F., & Marchi, L. (2013). Geomorphometric assessment of spatial sediment connectivity. Geomorphology, 188, 31–41.\n
*Key, C. H., & Benson, N. C. (2006). Landscape assessment: Ground measure of severity, the Composite Burn Index. USDA Forest Service.\n
*Keeley, J. E. (2009). Fire intensity, fire severity and burn severity. Int. J. Wildland Fire, 18(1), 116–126.\n
*Martini, L., Faes, L., Picco, L., Iroumé, A., Lingua, E., Garbarino, M., & Cavalli, M. (2020). Assessing the effect of fire severity on sediment connectivity in central Chile. Science of The Total Environment, 728, 139006. https://doi.org/10.1016/j.scitotenv.2020.139006\n
*Rouse, J. W., Haas, R. H., Schell, J. A., & Deering, D. W. (1974). Monitoring vegetation systems with ERTS. NASA, ERTS Symposium.\n
*European Space Agency (ESA). (2016 - present). Sentinel-2 L2A imagery. Retrieved from Copernicus Open Access Hub.\n
*Tarboton, D. G. (2023). TauDEM: Terrain Analysis Using Digital Elevation Models. Utah State University. Retrieved from https://hydrology.usu.edu/taudem\n
*OpenAI. (2025). ChatGPT (versione GPT-4). https://openai.com/chatgpt\n
*Google. (2025). Gemini [Large language model]. Retrieved from https://gemini.google.com\n
*Powered by SUBSTR8 version 1.0, platform for the quick creation of Standalone, Modular and Fast Spatial Analysis Tools (Unpublished).
