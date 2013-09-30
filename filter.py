KEY_PRECISION = "Precision (m)"
PRECISION_RANGE = 25

def precision_filter(data, datas):
    if data[KEY_PRECISION] == 0:
        return False
    if data[KEY_PRECISION] > PRECISION_RANGE:
        return False
    return True


MAX_SPEED_KM = 15
KEY_SPEED_1 = "Vitesse (m/s)"
KEY_SPEED_2 = "speed"
 
def speed_filter(data, datas):
    max_speed_m_s = MAX_SPEED_KM / 3.6
    if data[KEY_SPEED_1] > max_speed_m_s or data[KEY_SPEED_2] > max_speed_m_s:
        return False
    return True

MIN_SPEED_KM = 1 

def low_speed_filter(data, datas):
    max_speed_m_s = MIN_SPEED_KM / 3.6
    if data[KEY_SPEED_1] < max_speed_m_s or data[KEY_SPEED_2] < max_speed_m_s:
        return False
    return True


DIVIDE_DATASET_BY = 4
KEY_POINT = "Point"

def prune_filter(data, datas):
    if data[KEY_POINT] % DIVIDE_DATASET_BY == 0:
        return True
    return False
    