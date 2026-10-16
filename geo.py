import math
lon1, lat1, lon2, lat2 = float(38.975), float(45.035), float(39.0), float(45.05)
def haversine(lon1, lat1, lon2, lat2):
    lo1, la1, lo2, la2 = math.radians(lon1), math.radians(lat1), math.radians(lon2), math.radians(lat2)  
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    c = math.asin(math.sqrt(h)) * 2
    d = c * 6371
    return(d)
if __name__ == "__main__":
    print(haversine(38.975, 45.035, 39.0, 45.05))