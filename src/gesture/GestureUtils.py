import math
class GestureUtils:
    def __init__(self):
        pass
    @staticmethod
    def fingertip_distance(landmarks, first:int = 0, second: int = 1):
        """ Calculate the Euclidean distance between the fingertips of the given indices"""
        tip1 = landmarks[first]
        tip2 = landmarks[second]

        dist = math.sqrt((tip1.x - tip2.x)**2 + (tip1.y - tip2.y)**2)
        return dist
