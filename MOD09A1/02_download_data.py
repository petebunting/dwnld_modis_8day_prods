import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import nasa_cmr

# The pysondb database file
dwnld_db_file = "MOD09A1_dwnld_db.json"

# Output directory where data will be downloaded to.
out_dir = "/Users/pete/Temp/modis_processing/downloads"
if not os.path.exists(out_dir):
    os.mkdir(out_dir)

# This is your username and password for https://www.earthdata.nasa.gov
# To create this file you can use the rsgislib v5 command:
# rsgisuserpassfile.py earthdata_userpass.txt
user_pass_file = "/Users/pete/Temp/modis_processing/earthdata_userpass.txt"

nasa_cmr.download_granules_use_dwnld_db(dwnld_db_file, out_dir, user_pass_file, use_wget=False)
