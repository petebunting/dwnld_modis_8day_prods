import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import nasa_cmr
import datetime

start_date = datetime.datetime(year=2016, month=1, day=1)
end_date = datetime.datetime(year=2020, month=12, day=31)
bbox_wales = [-5.8, -2.4, 51.25, 53.6]
granules_lst = nasa_cmr.find_all_granules("MOD09A1", version="061",bbox=bbox_wales, start_date=start_date, end_date=end_date, page_size=100, max_n_pages=5)
print("\tN Granules: {}".format(len(granules_lst)))

if len(granules_lst) > 0:
    tot_file_size = nasa_cmr.get_total_file_size(granules_lst)
    print("Total File Size: {}".format(tot_file_size))
    # The database will be a JSON file but created with pysondb library
    dwnld_db_file = "MOD09A1_dwnld_db.json"
    miss_granules = nasa_cmr.create_cmr_dwnld_db(db_json=dwnld_db_file, granule_lst=granules_lst, dwnld_file_mime_type="application/x-hdfeos")
    print("\tMissed Granules: {}\n".format(len(miss_granules)))
