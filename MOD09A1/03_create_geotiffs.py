import glob
import os

def create_modis_hdf_to_gtiff(input_file, output_img):
    import rioxarray
    modis_obj = rioxarray.open_rasterio(input_file, masked=True)
    modis_obj = modis_obj.isel(band=0)
    # Geotiff outputted is not tiled or compressed and pyramids not built.
    # Would benefit from running through gdal_translate and then building datasets
    # stats and pyramids. Also, would be help to reorder bands.
    modis_obj.rio.to_raster(raster_path=output_img)

# Output directory where data will be downloaded to.
out_dir = "/Users/pete/Temp/modis_processing/gtiffs"
if not os.path.exists(out_dir):
    os.mkdir(out_dir)


# Get Modis files
modis_files = glob.glob("/Users/pete/Temp/modis_processing/downloads/*.hdf")
#modis_files = ["/Users/pete/Temp/modis_processing/downloads/MOD09A1.A2020361.h17v03.061.2021012072432.hdf"]
# Loop through and create geotiffs
for modis_file in modis_files:
    print(f"Input: {modis_file}")
    file_name = os.path.split(modis_file)[1].replace(".hdf", "").replace(".", "_").lower()
    output_img = os.path.join(out_dir, "{}.tif".format(file_name))
    print(f"Output: {output_img}")
    create_modis_hdf_to_gtiff(modis_file, output_img)

