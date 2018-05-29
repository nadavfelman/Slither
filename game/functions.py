from math import atan2


def map_range(value, r1, r2):
    """
    translate a value from one range of values to another range of values.

    example: map_range(3, (1, 5), (1, 10)) => 6
    example: map_range(7, (1, 10), (1, 100)) => 70

    Arguments:
        value {int} -- the value to map
        min1 {int} -- minimum value of range 1
        max1 {int} -- maximum value of range 1
        min2 {int} -- minimum value of range 2
        max2 {int} -- maximum value of range 2

    Returns:
        int -- value in range 2
    """
    min1, max1 = r1
    min2, max2 = r2

    return min2 + (float(value) - min1) * (float(max2) - min2) / (float(max1) - min1)


def constraint(value, min, max):
    """    
    constraint a value to be between two values

    example: constraint(3, 10, 50) => 10
    example: constraint(7, 1, 10) => 7

    Arguments:
        value {int} --  a value to be constraint
        min {int} -- minimum value
        max {int} -- maximum value

    Returns:
        int -- constrainted value
    """

    if value < min:
        return min
    elif value > max:
        return max
    else:
        return value


def range_intersect(a1, a2, b1, b2):
    """
    checks if there is a intersect between two ranges.
    includes minimum-maximum protection.

    example: range_intersect(0, 8, 4, 9) -> True
    example: range_intersect(0, 8, 9, 17) -> False

    Arguments:
        a1 {int} -- first value of first range
        a2 {int} -- second value of first range
        b1 {int} -- first value of second range
        b2 {int} -- second value of second range

    Returns:
        bool -- does the ranges intersect
    """

    return max(a1, a2) >= min(b1, b2) and min(a1, a2) <= max(b1, b2)


def incline_angle(p1, p2):
    """[summary]

    Arguments:
        p1 {tuple} -- the first point. the tuple is (x, y)
        p2 {tuple} -- the second point. the tuple is (x, y)

    Returns:
        int -- angle of the incline in radians
    """
    x1, y1 = p1
    x2, y2 = p2

    dx = x1 - x2
    dy = y1 - y2
    return atan2(dy, dx)