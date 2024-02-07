'''
This module is used to calculate the speed of a track.
'''

from datetime import datetime
import numpy as np
from haversine import haversine
from scipy.optimize import least_squares

def get_points_from_time_window(data:dict, i:int,
                                delta_t:int=5, exclude_i=False, min_nb_points=0) -> list:
    '''
    Return the list of the points around the point i in the time window +/-delta_t.
    If exclude_i is True, the point i is not included in the list.
    If min_nb_points is specified, the list will be completed with the closest points
    until it has min_nb_points elements.
    INPUT:
        - data (dict): the data of the track
        - i (int): the index of the point
        - delta_t (int) (default: 5s): the time window
        - exclude_i (bool) (default: False): if True, the point i is not included in the list
        - min_nb_points (int) (default: 0): the minimum number of points in the list
    OUTPUT:
        - points (list): the list of the points around the point i
    '''
    time_i = datetime.fromisoformat(data[f"point{i}"]["time"])
    points = []
    j, k = i-1, i+1

    # Add the point i if exclude_i is False
    if not exclude_i:
        points.append(data[f"point{i}"])

    # Add the points before i
    while j > 0: # We don't add the first point because the speed is not defined
        time_j = datetime.fromisoformat(data[f"point{j}"]["time"])
        if (time_i - time_j).total_seconds() > delta_t:
            break
        points.append(data[f"point{j}"])
        j -= 1
    # Add the points after i
    while k < len(data):
        time_k = datetime.fromisoformat(data[f"point{k}"]["time"])
        if (time_k - time_i).total_seconds() > delta_t:
            break
        points.append(data[f"point{k}"])
        k += 1
    
    # Complete the list with the closest points if min_nb_points is specified
    if min_nb_points != -1:
        while len(points) < min_nb_points:
            # If there is no more points before or after, add the closest points
            if j <= 0:
                points.append(data[f"point{k}"])
                k += 1
                continue
            if k == len(data):
                points.append(data[f"point{j}"])
                j -= 1
                continue
            # Else, add the closest point
            time_j = datetime.fromisoformat(data[f"point{j}"]["time"])
            time_k = datetime.fromisoformat(data[f"point{k}"]["time"])
            if (time_i - time_j).total_seconds() < (time_k - time_i).total_seconds():
                points.append(data[f"point{j}"])
                j -= 1
            else:
                points.append(data[f"point{k}"])
                k += 1
    return points

def time_list_from_points(points:list, time_ref:float=-1) -> list:
    '''
    Return the list of the times of the points in the list points.
    If time_ref is specified, the times are relative to time_ref.
    INPUT:
        - points (list): the list of the points
        - time_ref (float) (default: -1): the reference time
    OUTPUT:
        - times (list): the list of the times of the points
    '''
    if time_ref != -1:
        time_ref = datetime.fromisoformat(time_ref)
        return [(datetime.fromisoformat(point["time"]) - time_ref).total_seconds()
                for point in points]
    return [datetime.fromisoformat(point["time"]).second for point in points]

def calculate_speed_of_track(data:dict) -> list:
    '''
    Return the list of the speeds of the track.
    INPUT:
        - data (dict): the data of the track
    OUTPUT:
        - speeds (list): the list of the speeds of the track
    '''
    speeds = []

    for i in range(len(data)-1):
        dist = max(1e-3,
                   haversine((data[f"point{i}"]["lat"], data[f"point{i}"]["lon"]),
                         (data[f"point{i+1}"]["lat"], data[f"point{i+1}"]["lon"]),
                         "m")
                    )
        time = (datetime.fromisoformat(data[f"point{i+1}"]["time"]) - \
                datetime.fromisoformat(data[f"point{i}"]["time"])).total_seconds()
        speeds.append(dist/time)

    # Add the first speed at the beginning of the list
    speeds.insert(0, speeds[0])

    return speeds

def cubic_function(x:list, t:float) -> float:
    '''
    Returns the value of the cubic function with the coefficients x at the point t.
    INPUT:
        - x (list) : list of the coefficients of the cubic function.
        - t (float) : point.
    OUTPUT:
        - value (float) : value of the cubic function at the point t.
    '''
    return x[0]*t**3 + x[1]*t**2 + x[2]*t + x[3]

def fun(x:list, t:list, y:list) -> list:
    '''
    Returns the difference between the cubic function and the points.
    INPUT:
        - x (list) : list of the coefficients of the cubic function.
        - t (list) : list of the points.
        - y (list) : list of the values of the points.
    OUTPUT:
        - diff (list) : difference between the cubic function and the points.
    '''
    return cubic_function(x, t) - y

def robust_regression(data:dict, i:int) -> float:
    '''
    Returns the speed of the point i calculated with a robust regression.
    INPUT:
        - data (dict) : dictionnary of the data.
        - i (int) : index of the point.
    OUTPUT:
        - speed (float) : speed of the point i.
    '''
    x0 = np.zeros(4)

    neighbours = get_points_from_time_window(data, i, 5, exclude_i=True, min_nb_points=5)

    d = np.array(time_list_from_points(neighbours, time_ref=data[f"point{i}"]["time"]))
    y = np.array([p["speed"] for p in neighbours])

    res_robust = least_squares(fun, x0, loss='soft_l1', args=(d, y))

    return cubic_function(res_robust.x, 0)

def filter_outlying_speeds(data:dict, max_allowed_speed:float=50/3.6) -> list:
    '''
    Interpolates the speed of the points that have a speed greater than max_allowed_speed
    or lower than 0.
    INPUT:
        - data (dict): the data of the track
    OUTPUT:
        - speeds (list): the list of the speeds of the track
    '''
    speeds = []

    for i in range(1, len(data)):
        if data[f"point{i}"]["speed"] > max_allowed_speed or data[f"point{i}"]["speed"] < 0:
            speeds.append(max(0, min(max_allowed_speed,
                                     robust_regression(data, i))))
        else:
            speeds.append(data[f"point{i}"]["speed"])

    # The first speed is by definition the same as the second one
    speeds.insert(0, speeds[0])
    
    return speeds

def evaluate_stop_period(data:dict, i:int,
                         max_dist_stop:int=5, max_speed_stop:float=5/3.6, min_time_stop:int=5) -> int:
    '''
    Evaluate if the point i is the start of a stop period.
    If it is the case, return the index of the end of the stop period.
    Otherwise, return -1.
    A stop period is defined by:
        - a distance less than max_dist_stop
        - a speed less than max_speed_stop
        - a time greater than min_time_stop
    INPUT:
        - data (dict) : dictionnary of the data.
        - i (int) : index of the point.
        - max_dist_stop (int) (default: 5) : maximum distance allowed.
        - max_speed_stop (float) (default: 5/3.6) : maximum speed allowed.
        - min_time_stop (int) (default: 5) : minimum time allowed.
    OUTPUT:
        - j (int) : index of the end of the stop period.
    '''
    lat1, lon1 = data[f"point{i}"]["lat"], data[f"point{i}"]["lon"]
    for j in range(i+1, len(data)):
        lat2, lon2 = data[f"point{j}"]["lat"], data[f"point{j}"]["lon"]

        # If the distance or the speed is greater than the maximum allowed, the stop period is finished
        if (haversine((lat1, lon1), (lat2, lon2), "m") > max_dist_stop or
            data[f"point{j}"]["speed"] > max_speed_stop):
            if (datetime.fromisoformat(data[f"point{j-1}"]["time"]) -
                datetime.fromisoformat(data[f"point{i}"]["time"])).total_seconds() < min_time_stop:
                return -1
            return j-1

        # If we are at the end of the track, we check if the stop period is long enough
        if j == len(data)-1:
            if (datetime.fromisoformat(data[f"point{j}"]["time"]) -
                datetime.fromisoformat(data[f"point{i}"]["time"])).total_seconds() < min_time_stop:
                return -1
            return j
    return -1

def filter_speed_stop_track(data:dict,
                            max_dist_stop:int=5, max_speed_stop:float=5/3.6, min_time_stop:int=5) -> list:
    '''
    Filter the speed of the points that are in a stop period and assign them to 0.
    INPUT:
        - data (dict): the data of the track
        - max_dist_stop (int) (default: 5) : maximum distance allowed.
        - max_speed_stop (float) (default: 5/3.6) : maximum speed allowed.
        - min_time_stop (int) (default: 5) : minimum time allowed.
    OUTPUT:
        - speeds (list): the list of the speeds of the track
    '''
    speeds = []

    i = 0
    while i < len(data):
        if data[f"point{i}"]["speed"] < max_speed_stop:
            end_of_stop_period = evaluate_stop_period(data, i, max_dist_stop, max_speed_stop, min_time_stop)

            # If a stop period is detected
            if end_of_stop_period != -1:
                for _ in range(i, end_of_stop_period+1):
                    speeds.append(0)
                i = end_of_stop_period + 1
            else:
                speeds.append(data[f"point{i}"]["speed"])
                i += 1
        else:
            speeds.append(data[f"point{i}"]["speed"])
            i += 1
    
    # The first speed is by definition the same as the second one
    speeds.insert(0, speeds[0])

    return speeds


def adjust_speed_according_to_acceleration(data:dict, i:int, delta_t:float,
                                           max_allowed_speed:float=25,
                                           min_allowed_acc:float=-3, max_allowed_acc:float=3) -> float:
    '''
    Calculate the robust regression of the speed of the points i and adjust
    it according to the authorized acceleration with the point i-1.
    INPUT:
        - data (dict) : dictionnary of the data.
        - i (int) : index of the point.
        - delta_t (float) : time delay between the point i and the point i-1.
        - max_allowed_speed (float) (default: 25) : maximum speed allowed.
        - min_allowed_acc (float) (default: -3) : minimum acceleration allowed.
        - max_allowed_acc (float) (default: 3) : maximum acceleration allowed.
    OUTPUT:
        - speed (float) : speed of the point i.
    '''
    speed = robust_regression(data, i)
    speed = max(0, min(max_allowed_speed, speed))

    acceleration = (speed - data[f"point{i-1}"]["speed"])/delta_t

    # If the acceleration is not in the authorized range, we adjust the speed
    if acceleration > max_allowed_acc:
        speed = max(0, min(max_allowed_speed,
                           data[f"point{i-1}"]["speed"] + max_allowed_acc * delta_t))
    elif acceleration < min_allowed_acc:
        speed = max(0, min(max_allowed_speed,
                           data[f"point{i-1}"]["speed"] + min_allowed_acc * delta_t))

    return speed

def filter_unrealistic_accelerations(data:dict,
                                     max_allowed_speed:float=50/3.6,
                                     max_acceleration:float=5, min_deceleration:float=-5) -> list:
    '''
    Filter the unrealistic accelerations.
    INPUT:
        - data (dict) : dictionnary of the data.
        - max_allowed_speed (float) (default: 50/3.6) : maximum speed allowed.
        - max_acceleration (float) (default: 5) : maximum acceleration allowed.
        - min_deceleration (float) (default: -5) : minimum deceleration allowed.
    OUTPUT:
        - speeds (list) : list of the speeds of the points.
    '''
    speeds = []

    for i in range(1, len(data)):
        delta_t = (datetime.fromisoformat(data[f"point{i}"]["time"]) -\
                   datetime.fromisoformat(data[f"point{i-1}"]["time"])).total_seconds()
        acceleration = (data[f"point{i}"]["speed"] - data[f"point{i-1}"]["speed"])/delta_t
        if acceleration > max_acceleration or acceleration < min_deceleration:
            speeds.append(adjust_speed_according_to_acceleration(data, i, delta_t, max_allowed_speed,
                                                                 min_deceleration, max_acceleration))
        else:
            speeds.append(data[f"point{i}"]["speed"])
    
    # The first speed is by definition the same as the second one
    speeds.insert(0, speeds[0])

    # Reduce the number of significant digits
    speeds = [round(speed, 3) for speed in speeds]

    return speeds

