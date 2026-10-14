import numpy as np 
from datetime import datetime
from scipy.interpolate import CubicSpline
def get_traffic_factor(points):
    lon_min, lon_max = 38.875000, 39.095000
    lat_min, lat_max = 44.975000, 45.145000
    in_zone = any(lon_min <= p[0] <= lon_max and lat_min <= p[1] <= lat_max for p in points)
    current_hour = datetime.now().hour + datetime.now().minute / 60
    week_day = datetime.now().weekday()
    if in_zone:
        y = np.array([1, 0.5, 1.1, 1.3, 1.5, 1.8, 2.2, 2.6, 3.6])
        x = np.array(list(range(len(y))))
        f = CubicSpline(x,y)
        if week_day < 5:
            if 6.25 <= current_hour < 8.75:
                a = 0.035667 * (current_hour * 60 - 360) - 0.5350
            elif 8.75 <= current_hour < 9.5:
                a = -0.037778 * (current_hour * 60 - 360) + 11.5833
            elif 9.5 <= current_hour < 10.1667:
                a = -0.016250 * (current_hour * 60 - 360) + 7.0625
            elif 10.1667 <= current_hour < 16.3333:
                a = 0 * (current_hour * 60 - 360) + 3
            elif 16.3333 <= current_hour < 17.25:
                a = 0.007273 * (current_hour * 60 - 360) - 1.5091
            elif 17.25 <= current_hour < 17.75:
                a = 0.061667 * (current_hour * 60 - 360) - 38.2250
            elif 17.75 <= current_hour < 18.8:
                a = 0.015873 * (current_hour * 60 - 360) - 5.9405
            elif 18.8 <= current_hour < 20.5:
                a = -0.048529 * (current_hour * 60 - 360) + 43.5206
            elif 20.5 <= current_hour < 21.5:
                a = -0.009167 * (current_hour * 60 - 360) + 9.2750
            elif 21.5 <= current_hour < 23:
                a = -0.008333 * (current_hour * 60 - 360) + 8.5000
            else:  
                a = 0  
        else:
            if 6.0 <= current_hour < 8.0:
                a = 0.004167 * (current_hour * 60 - 360) + 0
            elif 8.0 <= current_hour < 10.0:
                a = 0.012500 * (current_hour * 60 - 360) - 1.0
            elif 10.0 <= current_hour < 12.0:
                a = 0.016667 * (current_hour * 60 - 360) - 2.0
            elif 12.0 <= current_hour < 15.0:
                a = 0.002778 * (current_hour * 60 - 360) + 3.0
            elif 15.0 <= current_hour < 18.0:
                a = -0.002778 * (current_hour * 60 - 360) + 6.0
            elif 18.0 <= current_hour < 20.5:
                a = -0.010000 * (current_hour * 60 - 360) + 11.2
            elif 20.5 <= current_hour < 22.0:
                a = -0.016667 * (current_hour * 60 - 360) + 17.0
            elif 22.0 <= current_hour <= 23.0:
                a = -0.016667 * (current_hour * 60 - 360) + 17.0
            else:
                a = 0
        return f(a)
    return 1