'''
This module is used to calculate the slope of a track.
'''

from datetime import datetime
import numpy as np
from scipy.interpolate import UnivariateSpline
from scipy.optimize import least_squares
from haversine import haversine

def get_points_from_dist_window(data:dict, i:int, delta_dist:int,
                                exclude_i:bool=False, min_nb_points:int=0) -> list:
    '''
    Return the list of the points around the point i in the distance window +/-delta_dist.
    If exclude_i is True, the point i is not included in the list.
    If min_nb_points is specified, the list will be completed with the closest points
    until it has min_nb_points elements.
    INPUT:
        - data (dict) : dictionnary of the data.
        - i (int) : index of the point.
        - delta_dist (float) : distance window.
        - exclude_i (bool) (default: False) : wether the point i is included in the list or not.
        - min_nb_points (int) (default: 0) : minimum number of points in the list.
    OUTPUT:
        - points (list) : list of the points around the point i.
    '''
    pos_i = data[f"point{i}"]["cumulated_dist"]
    points = []
    j, k = i-1, i+1

    # Add the point i if exclude_i is False
    if not exclude_i:
        points.append(data[f"point{i}"])

    # Add the points before i
    while j > 0: # We don't add the first point because the slope is not defined
        pos_j = data[f"point{j}"]["cumulated_dist"]
        if pos_i - pos_j > delta_dist:
            break
        points.append(data[f"point{j}"])
        j -= 1
    # Add the points after i
    while k < len(data):
        pos_k = data[f"point{k}"]["cumulated_dist"]
        if pos_k - pos_i > delta_dist:
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
            pos_j = data[f"point{j}"]["cumulated_dist"]
            pos_k = data[f"point{k}"]["cumulated_dist"]
            if pos_i - pos_j < pos_k - pos_i:
                points.append(data[f"point{j}"])
                j -= 1
            else:
                points.append(data[f"point{k}"])
                k += 1
    return points

def dist_list_from_points(points:list, dist_ref:float=-1) -> list:
    '''
    Return the list of the distance of the points in the list points.
    If dist_ref is specified, the crossed distances are relative to the distance indicated.
    INPUT:
        - points (list) : list of the points.
        - dist_ref (float) (default: -1) : reference distance.
    OUTPUT:
        - dist_list (list) : list of the distance of the points.
    '''
    if dist_ref != -1:
        return [point["cumulated_dist"] - dist_ref for point in points]
    return [point["cumulated_dist"] for point in points]


def get_flatten_elevation(data:dict, s:float=20) -> UnivariateSpline:
    '''
    Returns the spline of the elevation of the track.
    We flatten the elevation by removing the points that have the same abscisse.
    INPUT:
        - data (dict) : dictionnary of the data.
        - s (float) (default: 20) : smoothing factor.
    OUTPUT:
        - spline_elevation (UnivariateSpline) : spline of the elevation of the track.
    '''
    data_elev = [p["elevation"] for p in data.values()]
    data_cumulated_dist = [p["cumulated_dist"] for p in data.values()]

    # We remove the points that have the same abscisse
    # and we replace them by the mean of the points
    i = 0
    while i < len(data_cumulated_dist):
        j = i + 1
        while j < len(data_cumulated_dist) and data_cumulated_dist[i] == data_cumulated_dist[j]:
            j += 1
        if j == i + 1:
            i += 1
            continue
        data_elev[i] = np.mean(data_elev[i:j])
        del data_cumulated_dist[i+1:j]
        del data_elev[i+1:j]
    
    # We create the spline
    spline_elevation = UnivariateSpline(data_cumulated_dist, data_elev, k=3, s=s)
    return spline_elevation

def calculate_slope_of_track(data:dict, s:float=20) -> list:
    '''
    Returns the raw slope of the track.
    INPUT:
        - data (dict) : dictionnary of the data.
        - s (float) (default: 20) : smoothing factor.
    OUTPUT:
        - slope (list) : list of the slope of the track.
    '''
    spline_elevation = get_flatten_elevation(data, s)
    data_cumulated_dist = [p["cumulated_dist"] for p in data.values()]

    return 100 * np.array(spline_elevation.derivative(1)(data_cumulated_dist))

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
    Returns the slope of the point i calculated with a robust regression.
    INPUT:
        - data (dict) : dictionnary of the data.
        - i (int) : index of the point.
    OUTPUT:
        - slope (float) : slope of the point i.
    '''
    x0 = np.zeros(4)

    neighbours = get_points_from_dist_window(data, i, 10, exclude_i=True, min_nb_points=5)

    d = np.array(dist_list_from_points(neighbours, dist_ref=data[f"point{i}"]["cumulated_dist"]))
    y = np.array([p["slope"] for p in neighbours])

    res_robust = least_squares(fun, x0, loss='soft_l1', args=(d, y))

    return cubic_function(res_robust.x, 0)

def filter_outlying_slopes(data:dict, max_allowed_slope:float=25) -> list:
    '''
    Interpolates the slopes of the points that have a slope greater than max_allowed_slope in absolute.
    INPUT:
        - data (dict) : dictionnary of the data.
        - max_allowed_slope (float) (default: 20) : maximum slope allowed.
    OUTPUT:
        - slopes (list) : list of the slopes of the points.
        '''
    slopes = []

    for i in range(1, len(data)):
        if abs(data[f"point{i}"]["slope"]) > max_allowed_slope:
            new_slope = robust_regression(data, i)
            slopes.append(np.sign(new_slope) * min(max_allowed_slope, new_slope))
        else:
            slopes.append(data[f"point{i}"]["slope"])

    # The first slope is by definition the same as the second one
    slopes.insert(0, slopes[0])
    
    return slopes

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

def filter_slope_stop_track(data:dict,
                       max_dist_stop:int=5, max_speed_stop:float=5/3.6, min_time_stop:int=5) -> list:
    '''
    Returns the slopes of the points of the track after having calculated mean slopes
    during the stop periods.
    INPUT:
        - data (dict) : dictionnary of the data.
        - max_dist_stop (int) (default: 5) : maximum distance allowed.
        - max_speed_stop (float) (default: 5/3.6) : maximum speed allowed.
        - min_time_stop (int) (default: 5) : minimum time allowed.
    OUTPUT:
        - slopes (list) : list of the slopes of the points.
    '''
    slopes = []

    i = 0
    while i < len(data):
        end_of_stop_period = evaluate_stop_period(data, i,
                                                  max_dist_stop, max_speed_stop, min_time_stop)
        # If the point i is the start of a stop period
        if end_of_stop_period != -1:
            # We calculate the mean slope of the stop period
            mean_slope = np.mean([data[f"point{j}"]["slope"]
                                  for j in range(i, end_of_stop_period+1)])
            for j in range(i, end_of_stop_period+1):
                slopes.append(mean_slope)
            i = end_of_stop_period + 1
        else:
            slopes.append(data[f"point{i}"]["slope"])
            i += 1

    return slopes

def adjust_slope_according_to_derivate(data:dict, i:int, delta_dist:float,
                                       max_allowed_slope:float=25, max_derivate_slope:float=3) -> float:
    '''
    Calculate the robust regression of the slope of the points i and adjust
    it according to the authorized slope derivate with the point i-1.
    INPUT:
        - data (dict) : dictionnary of the data.
        - i (int) : index of the point.
        - delta_dist (float) : distance between the point i and the point i-1.
        - max_allowed_slope (float) (default: 25) : maximum slope allowed.
        - max_derivate_slope (float) (default: 3) : maximum slope derivate allowed.
    OUTPUT:
        - slope (float) : slope of the point i.
    '''
    slope = robust_regression(data, i)
    slope = np.sign(slope) * min(max_allowed_slope, abs(slope))

    slope_derivate = (slope - data[f"point{i-1}"]["slope"])/delta_dist

    # If the slope derivate is greater than the maximum allowed, we adjust the slope
    if abs(slope_derivate) > max_derivate_slope:
        slope = np.sign(data[f"point{i-1}"]["slope"]) * \
            min(max_allowed_slope,
                data[f"point{i-1}"]["slope"] + \
                    np.sign(data[f"point{i-1}"]["slope"]) * max_derivate_slope * delta_dist)

    return slope

def filter_unrealistic_slope_derivate(data:dict,
                                      max_allowed_slope:float=25, max_derivate_slope:float=3) -> list:
    '''
    Filter the unrealistic slope derivate.
    INPUT:
        - data (dict) : dictionnary of the data.
        - max_allowed_slope (float) (default: 25) : maximum slope allowed.
        - max_derivate_slope (float) (default: 3) : maximum slope derivate allowed.
    OUTPUT:
        - slopes (list) : list of the slopes of the points.
    '''
    slopes = []

    for i in range(1, len(data)):
        # We calculate the distance between the points i and i-1
        delta_dist = max(1e-3,
                        haversine(
                            (data[f"point{i}"]["lat"], data[f"point{i}"]["lon"]),
                            (data[f"point{i-1}"]["lat"], data[f"point{i-1}"]["lon"]),
                            "m")
                        )

        derivate = (data[f"point{i}"]["slope"] - data[f"point{i-1}"]["slope"])/delta_dist

        if abs(derivate) > max_derivate_slope:
            slopes.append(adjust_slope_according_to_derivate(data, i, delta_dist,
                                                             max_allowed_slope, max_derivate_slope))
        else:
            slopes.append(data[f"point{i}"]["slope"])

    # The first slope is by definition the same as the second one
    slopes.insert(0, slopes[0])

    # We reduce the precision of the slopes
    slopes = [round(s, 3) for s in slopes]

    return slopes
    