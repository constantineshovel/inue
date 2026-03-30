INUE v1.1 άλφα 🛰️🔥
INteractive and User-friendly Emergency tool for Postfire Erosion Susceptibility Mapping from Remote Sensing Data
INUE is a rapid assessment tool designed to map erosion susceptibility in postfire landscapes. Built on the SUBSTR8 platform, it allows for fast prioritization of at-risk watersheds using remote sensing data during the critical emergency phase.

⚠️ Important Warnings
 * Fast Assessment, Not Precision: INUE is intended for rapid prioritization and screening, not for high-precision physical or hydrological modeling.
 * Relative Connectivity: The tool measures relative susceptibility based on connectivity, not actual sediment fluxes or mass yields.
 * Use Cases: Ideal for identifying watersheds at risk immediately after a fire when field data is limited.
🔬 Methodology: The FIREX Index
The core of the tool is the FIREX index, which models postfire sediment dynamics by adjusting a stable Sediment Connectivity Index based on burn severity and landscape factors.
 * IC_{normalized}: Normalized Sediment Connectivity Index.
 * dNBR_{normalized}: Reclassified Burn Severity.
 * gDI: Geomorphologic Sediment Disconnection Index (for landforms like terraces).
 * VRf: Sediment Disconnection due to Vegetation Recovery.
 * cf: Local variables or triggering phenomena (optional).
🛠️ System Requirements
 * OS: Windows 10/11 (64-bit).
 * CPU: Dual-Core 3.10 GHz or equivalent.
 * RAM: 8 GB.
 * Mandatory Software: TauDEM v5.3.7 or higher.
 * Input Data: DEM (10m to 1m resolution suggested), Study Area Shapefile, Road Network Shapefile, and NIR/SWIR satellite imagery (Sentinel-2 or Landsat).
🚀 Workflow
 * Preliminary Operations: Set the EPSG, Spatial Resolution, and NDVI Threshold. Use the Resample and Crop tools to ensure all input rasters match in extent and resolution.
 * Module Execution: Run the DEMROAD Crafter, Sediment Connectivity Calculator, and Burnt Area Analyzer plus the additional indexes for sediment disconnection as required by your analysis 
 * Hazard Scenario (HS) Selection: Configure the GUI switchers to match your area's local conditions (vegetation recovery and/or landforms).
 * Final Map: Generate the Postfire Erosion Susceptibility map - FIREX.
Hazard Scenarios (HS)
| Scenario | Configuration | Disconnecting Landforms | Description |
|---|---|---|---|
| HS1 | Postfire | No | Bare burned area or sparse regrowth. |
| HS2 | Postfire | Yes | Burned area with terraces or retaining structures. |
| HS3 | Veg. Recovery | No | Areas with significant dense vegetation regrowth. |
| HS4 | Veg. Recovery | Yes | Terraced slopes with dense vegetation recovery. |
📄 License & Contact
 * License: GNU Affero General Public License v3.0 (AGPL-3.0).
 * Developer: Costantino Pala (Geoscientist, PhD)
 * Contact: costantino.pala.geo@proton.me
📚 Selected Bibliography
 * Borselli et al. (2008) - Prolegomena to sediment and flow connectivity in the landscape.
 * Cavalli et al. (2008) - The effectiveness of airborne LiDAR data in the recognition of channel-bed morphology.
 * Martini et al. (2020) - Assessing the effect of fire severity on sediment connectivity.
 * Tarboton, D. G. (2023) - TauDEM: Terrain Analysis Using Digital Elevation Models.
