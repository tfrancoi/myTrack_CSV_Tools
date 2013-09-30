import math   
 
def to_hour_min_sec(second):
    h = second / 3600
    m = second % 3600 / 60
    s = second % 60
    return (h, m, s) 

#Earth Radius in m
RADIUS = 40000000 / (2 * math.pi)

def to_cartesian(phi, theta):
    phi = phi * math.pi / 180
    theta = theta * math.pi / 180
    z = RADIUS * math.sin(phi)
    r = RADIUS * math.cos(phi)
    
    x =  r * math.sin(theta)
    y =  r * math.cos(theta)
    return (x, y, z)

def distance(coordo1, coordo2):
    return math.sqrt(sum([(c1 - c2) ** 2 for c1, c2 in zip(coordo1, coordo2)]))


def duration(t1, t2):
    """
        @param t1: Time of the current step
        @param t2: Time of the previous step
        @return: t1 - t2 in second 
    """
    return (t1 - t2).seconds

def to_km(length):
    return length / 1000.0

def to_km_per_hour(speed):
    return speed * 3.6