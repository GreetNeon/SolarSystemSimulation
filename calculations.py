###################################################################################################################################################
# Description: This file contains the functions that are used to calculate the values required for the simulation.
###################################################################################################################################################

import math

def calculate_distance(planet1, planet2):
    # Calculating the distance between the 2 planets
    # To add: change the value distance to sun
    distance_x = planet2.x - planet1.x
    distance_y = planet2.y - planet1.y
    # Using the formula d = sqrt((x2 - x1)^2 + (y2 - y1)^2)
    distance = round(math.sqrt(distance_x ** 2 + distance_y ** 2), 7)
    return distance, distance_x, distance_y

def calculate_force(planet1, planet2, g_constant):
    # Calculating the force between the 2 planets
    distance, distance_x, distance_y = calculate_distance(planet1, planet2)
    # Using the formula F = (G * m1 * m2) / r^2
    force = (g_constant * planet1.mass * planet2.mass) / (distance ** 2)
    # Using the formula Fx = cos(theta) * F and Fy = sin(theta) * F
    theta = math.atan2(distance_y, distance_x)
    force_x = math.cos(theta) * force
    force_y = math.sin(theta) * force
    return force_x, force_y

