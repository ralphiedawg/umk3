import os

import cv2 as cv
import mediapipe as mp
import time

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

FPS = 60
class Landmarker():
    def __init__(self, cam_index:int = 0, model_path:str = 'hand_landmarker.task', preserveVideo:bool = False):
        self.index = cam_index
        self.model_path = model_path
        self.preserve = preserveVideo
        BaseOptions = mp.tasks.BaseOptions
        HandLandmarker = mp.tasks.vision.HandLandmarker
        HandLandmarkerOpts = mp.tasks.vision.HandLandmarkerOptions
        HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult
        VisionRunningMode = mp.tasks.vision.RunningMode
        self.opts = HandLandmarkerOpts(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=VisionRunningMode.LIVE_STREAM,
            result_callback=self.print_result
        )
        self.landmarker = HandLandmarker.create_from_options(self.opts)

    @staticmethod
    def print_result(result, output_image: mp.Image, timestamp_ms: int):
        print('hand landmarker result: {}'.format(result))

    @staticmethod
    def detect_pose():
        pass
    @staticmethod
    #Taken straight from google solutions idc
    def draw_landmarks_on_image(rgb_image, detection_result):
        MARGIN = 10  # pixels
        FONT_SIZE = 1
        FONT_THICKNESS = 1
        HANDEDNESS_TEXT_COLOR = (88, 205, 54) # vibrant green

        mp_hands = mp.tasks.vision.HandLandmarksConnections
        mp_drawing = mp.tasks.vision.drawing_utils
        mp_drawing_styles = mp.tasks.vision.drawing_styles

        hand_landmarks_list = detection_result.hand_landmarks
        handedness_list = detection_result.handedness
        annotated_image = cv.cvtColor(rgb_image, cv.COLOR_RGB2BGR)

        # Loop through the detected hands to visualize.
        for idx in range(len(hand_landmarks_list)):
            hand_landmarks = hand_landmarks_list[idx]
            handedness = handedness_list[idx]

            # Draw the hand landmarks.
            mp_drawing.draw_landmarks(
                annotated_image,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())

            # Get the top left corner of the detected hand's bounding box.
            height, width, _ = annotated_image.shape
            x_coordinates = [landmark.x for landmark in hand_landmarks]
            y_coordinates = [landmark.y for landmark in hand_landmarks]
            text_x = int(min(x_coordinates) * width)
            text_y = int(min(y_coordinates) * height) - MARGIN

            # Draw handedness (left or right hand) on the image.
            cv.putText(annotated_image, f"{handedness[0].category_name}",
                       (text_x, text_y), cv.FONT_HERSHEY_DUPLEX,
                       FONT_SIZE, HANDEDNESS_TEXT_COLOR, FONT_THICKNESS, cv.LINE_AA)

        return annotated_image

    def open_cam(self):
        self.cam = cv.VideoCapture(self.index)
        width = int(self.cam.get(cv.CAP_PROP_FRAME_WIDTH))
        height = int(self.cam.get(cv.CAP_PROP_FRAME_HEIGHT))

        # I love geeksforgeeks
        fourcc = cv.VideoWriter.fourcc(*'mp4v')
        self.out = cv.VideoWriter('out.mp4', fourcc, 20.0, (width, height))

        base_opts = python.BaseOptions(model_asset_path='hand_landmarker.task')
        opts = vision.HandLandmarkerOptions(base_options = base_opts, num_hands = 2)

        detector = vision.HandLandmarker.create_from_options(opts)

        while True:
            ret, raw = self.cam.read()
            if not ret:
                break
            self.out.write(raw)

            raw_rgb = cv.cvtColor(raw, cv.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=raw_rgb)

            res = detector.detect(mp_image)
            frame = self.draw_landmarks_on_image(raw_rgb, res)
            #time.sleep(1/FPS)

            cv.imshow('Video', frame)

            if cv.waitKey(1) == ord('q'):
                break
        self.close_cam()

    def close_cam(self):
        self.cam.release()
        self.out.release()
        cv.destroyAllWindows()
        if not self.preserve:
            print('Deleting output video, this can behavior can be disabled via the flag --preserveOutput')
            os.remove('out.mp4')

if __name__ == "__main__":
    L = Landmarker()
    L.open_cam()
