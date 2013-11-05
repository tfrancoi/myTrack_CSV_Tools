# -*- encoding: utf-8 -*-
import csv
from csv_helper import UnicodeWriter
from tools import to_hour_min_sec, to_cartesian, distance, duration
from datetime import datetime

#mean speed method
ON_TOTAL = "on_total"
ON_STEP = "on_step"

SEGMENT_KEY = "Segment"

class DataSet:
    """
        length unit is meter
        time unit is second
    """
    
    
    def __init__(self, filename):
        self.filename = filename
        f = file(self.filename, 'r')
        self.csv_reader = csv.reader(f, quotechar='"', delimiter=',')
        self.header = self.csv_reader.next()
        self.datas = []
        self._load_data()
        self.__init_first_step()
        self.__prepare_data()
        self.distance_total = 0
        self.total_time = 0
        self.not_moving_time = 0
        self.filter_list = []
        self.positive_denivele = 0
        self.negative_denivele = 0
        
    def _load_data(self):
        for line in self.csv_reader:
            self.datas.append(dict(zip(self.header, line)))
            
    def __init_first_step(self):
        self.datas[0]["Vitesse (m/s)"] = '0,0'
        self.datas[0]["distance_total"] = 0
        self.datas[0]["distance_previous"] = 0
        self.datas[0]["duration_total"] = 0
        self.datas[0]["duration_previous"] = 0
        self.datas[0]['speed'] = 0 
        self.datas[0]['move'] = False
        self.datas[0]['den'] = 0
            
    def __prepare_data(self):
        for data in self.datas:
            data["time"] = self.__to_datetime(data['Duree'])
            data["Latitude"] = float(data["Latitude"].replace(',', '.') or '0.0')
            data["Longitude"] = float(data["Longitude"].replace(',', '.') or '0.0')
            data["Vitesse (m/s)"] = float(data["Vitesse (m/s)"].replace(',', '.') or '0.0')
            data["Precision (m)"] = float(data["Precision (m)"].replace(',', '.') or '0.0')
            data["Altitude (m)"] = float(data["Altitude (m)"].replace(',', '.') or '0.0')
            data["Point"] = int(data["Point"])

    def __to_datetime(self, data_time):
        return datetime.strptime(data_time[:10] + ' ' + data_time[11:19],   "%Y-%m-%d %H:%M:%S")
    
    def pre_process(self):
        """
            Compute extra data based on the current data only (not neightboor data)
        """
        for data in self.datas:
            data["coordo"] = to_cartesian(float(data['Latitude']), float(data['Longitude']))
           
            
    def filter(self):
        new_datas = []
        remove_datas = []
        for data in self.datas:
            filter_answer = [f(data, self.datas) for f in self.filter_list]
            if all(filter_answer):
                new_datas.append(data)
            else:
                remove_datas.append(data)
        self.datas = new_datas
        self.__init_first_step()
        return remove_datas
    
    def process(self):
        #Take into account segment
        for i in xrange(1, len(self.datas)):
            denivele = float(self.datas[i]["Altitude (m)"]) - float(self.datas[i-1]["Altitude (m)"])
            if denivele > 0:
                self.positive_denivele += denivele
            else:
                self.negative_denivele -= denivele
                
            self.datas[i]["den"] = denivele
            d = distance(self.datas[i]["coordo"], self.datas[i - 1]["coordo"])
            self.distance_total += d
            self.datas[i]["distance_total"] = self.distance_total
            self.datas[i]["distance_previous"] = d
            
            dur = duration(self.datas[i]["time"], self.datas[i - 1]["time"])
            self.total_time += dur
            self.datas[i]["duration_total"] = self.total_time
            self.datas[i]["duration_previous"] = dur
            
            self.datas[i]['speed'] = self.datas[i]["duration_previous"] \
                                and self.datas[i]["distance_previous"] / self.datas[i]["duration_previous"] \
                                or 0
            self.datas[i]['move'] = self.datas[i]['speed'] and True or False  
            if self.datas[i]['speed'] < 0.19:
                #print "not moving", i
                self.not_moving_time += dur
            #TODO filter in case of refuse based calculation on next
    
    def export(self, prefix="PROCESS_"):
        def to_str(data):
            str_data = dict(data)
            if str_data.get('time'):
                str_data['time'] = str_data['time'].strftime("%Y-%m-%d %H:%M:%S") 
            for k, v in str_data.items():
                str_data[k] = str(v).replace('.', ',')
            return str_data 
          
        print "Export..."
        c = UnicodeWriter(open(prefix + self.filename, "wb"))
        c.writerow(self.datas[0].keys())
        for d in self.datas:
            c.writerow([to_str(d)[k] for k in d.keys()])
        return prefix + self.filename
        
        
        
    def get_column(self, key, default=False):
        return [d.get(key, default) for d in self.datas]
    
    def __get_mean_speed_on_total(self):
        return (self.distance_total /  self.total_time)
    
    def __get_mean_speed_on_step(self):
        return sum([speed * time / self.total_time 
                        for speed, time in zip(
                                self.get_column("speed"), 
                                self.get_column("duration_previous"))
                    ])
        
    def get_mean_speed(self, method=ON_TOTAL):
        if method == ON_TOTAL:
            return self.__get_mean_speed_on_total()
        elif method == ON_STEP:
            return self.__get_mean_speed_on_step()
        return 0
    
    def len(self):
        return len(self.datas)
    
HEADER_MAPPING = {
    "Latitude (degrés)" : "Latitude",
    "Longitude (degrés)" : "Longitude",
    "Précision (m)" : "Precision (m)",
    "Durée" : "Duree",

}

REMOVE_COLUMN_LIST = ["Puissance (W)", "Cadence (tr/min)", "Fréquence cardiaque (bpm)", "Relèvement (degrés)"]
    

    
class DataSet_cleaner(DataSet):
    def __init__(self, filename):
        self.filename = filename
        f = file(self.filename, 'r')
        self.csv_reader = csv.reader(f, quotechar='"', delimiter=',')
        self.__delete_row()
        self.header = self.csv_reader.next()
        self.header = self.__rename_header(HEADER_MAPPING)
        self.datas = []
        self._load_data()
        self.__delete_column(REMOVE_COLUMN_LIST)
        
    def __rename_header(self, mapping):
        new_header = []
        for h in self.header:
            if mapping.get(h):
                new_header.append(mapping.get(h))
            else:
                new_header.append(h)
        return new_header
        
    def __delete_row(self):
        self.csv_reader.next()
        self.csv_reader.next()
        self.csv_reader.next()
        
    def __delete_column(self, column_list):
        for c in column_list:
            try:
                self.header.remove(c)
            except ValueError:
                print 'Error: %s is not in the header' % c
            
        for d in self.datas:
            for c in column_list:
                try:
                    d.pop(c)
                except KeyError:
                    print 'Error: %s is not present in the data' % c
                    
    def merge(self, dataset):
        """
            @param dataset: a DataSet object 
        """
        #take last segment
        last_segment = int(self.datas[-1][SEGMENT_KEY])
        for d in dataset.datas:
            new_data = {}
            for c in self.header:
                if c == SEGMENT_KEY:
                    new_data[c] = str(int(d.get(c, 1)) + last_segment - 1)
                else:
                    new_data[c] = d.get(c, '')
            self.datas.append(new_data)
        
        