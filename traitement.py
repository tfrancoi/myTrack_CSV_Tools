# -*- encoding: utf-8 -*-

from datetime import datetime
from dataset import DataSet, DataSet_cleaner, ON_TOTAL, ON_STEP
from tools import to_hour_min_sec, to_km_per_hour
from filter import precision_filter, speed_filter, prune_filter, low_speed_filter
import sys

now = datetime.now()
FILENAME = 'Roumanie J4.csv'
LISSAGE = False

def lissage(datas, i, key, r=2):
    total = 0
    nb = 0
    for j in range(i - r, i + r + 1):
        if not j < 0 and not j >= len(datas):
            nb += 1
            total += float(datas[j][key])
    return total / float(nb)
    
    
if len(sys.argv) < 2:
    print "Please provide a csv filename"

filename = sys.argv[1]
if len(sys.argv) > 2:
    if sys.argv[2] == 'clean':
        print "clean CSV File"
        cleaner = DataSet_cleaner(filename)
        filename = cleaner.export("CLEAN_")


    
track_data_set = DataSet(filename)
track_data_set.filter_list.extend([precision_filter])
#track_data_set.post_filter_list.extend([speed_filter, low_speed_filter])
print "dataset len", track_data_set.len()

if LISSAGE:
    for i, data in enumerate(track_data_set.datas): 
        data["Altitude Lissage"] = lissage(track_data_set.datas, i, "Altitude (m)", 20)
        data['Latitude'] = lissage(track_data_set.datas, i, 'Latitude', 2)
        data['Longitude'] = lissage(track_data_set.datas, i, 'Longitude', 2)

track_data_set.pre_process()
#pre_lissage
track_data_set.filter()
print "dataset len", track_data_set.len()
track_data_set.process()
#track_data_set.post_filter()
#lissage
for i, data in enumerate(track_data_set.datas): 
    speed = data['speed']
    data['speed'] = lissage(track_data_set.datas, i, 'speed', 40)
    print "%s - %s", speed, data['speed']



    


print 'distance total', track_data_set.distance_total / 1000, 'km'  
print 'total time %s:%s:%s' % to_hour_min_sec(track_data_set.total_time)
print 'total not moving time %s:%s:%s' % to_hour_min_sec(track_data_set.not_moving_time)
print 'mean speed on step', to_km_per_hour(track_data_set.get_mean_speed(ON_STEP))
print "mean speed on total", to_km_per_hour(track_data_set.get_mean_speed(ON_TOTAL))
print "positive denivele (m)", track_data_set.positive_denivele 
print "negative denivele (m)", track_data_set.negative_denivele


export_file_name = track_data_set.export()
print 'Export data to file %s' % export_file_name


#TODO total dénivelé