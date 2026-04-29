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
