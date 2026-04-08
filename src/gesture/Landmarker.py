import os

import cv2 as cv
import mediapipe as mp

class Landmarker():
    def __init__(self, cam_index:int = 0, model_path:str = 'hand_landmarker.task', preserveVideo:bool = False):
        self.index = cam_index
        self.model_path = model_path
        self.preserve = preserveVideo

    def open_cam(self):
        self.cam = cv.VideoCapture(self.index)
        width = int(self.cam.get(cv.CAP_PROP_FRAME_WIDTH))
        height = int(self.cam.get(cv.CAP_PROP_FRAME_HEIGHT))

        # I love geeksforgeeks
        fourcc = cv.VideoWriter.fourcc(*'mp4v')
        self.out = cv.VideoWriter('out.mp4', fourcc, 20.0, (width, height))

        while True:
            ret, frame = self.cam.read()
            self.out.write(frame)
            cv.imshow('Video', frame)

            if cv.waitKey(1) == ord('q'):
                break
        self.close_cam()

    def close_cam(self):
        self.cam.release()
        self.out.release()
        cv.destroyAllWindows()
        if not self.preserve:
            print('Deleting Output Video, this can behavior can be disabled via the flag --preserveOutput')
            os.remove('out.mp4')


if __name__ == "__main__":
    L = Landmarker()
