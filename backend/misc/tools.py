

def calc_center(points) -> (float, float):
    x = [float(p[0]) for p in points]
    y = [float(p[1]) for p in points]
    return sum(x) / len(points), sum(y) / len(points)
