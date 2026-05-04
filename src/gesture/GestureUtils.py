import math
class gestureutils:
    def __init__(self):
        pass
    @staticmethod
    def fingertip_distance(landmarks, first:int = 0, second: int = 1):
        """ calculate the euclidean distance between the fingertips of the given indices"""
        tip1 = landmarks[first]
        tip2 = landmarks[second]

        dist = math.dist((tip1.x, tip1.y), (tip2.x, tip2.y))
        return dist
    @staticmethod
    def normalize_quantize(dist: float, min_dist: float, max_dist: float, steps: int) -> float:
        """ Converts given distance to the increments"""
        if dist <= min_dist:
            percent = 0.0
        elif dist >= max_dist:
            percent = 1.0
        else: 
            percent = (dist - min_dist) / (max_dist - min_dist)
        return round(percent * steps) / steps
