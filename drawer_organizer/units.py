import math


def adjust_to_half_unit(value, unit):
    # Find the smallest interval of 0.5 * unit >= value
    interval = 0.5 * unit
    n = math.ceil(value / interval)
    return n * interval
