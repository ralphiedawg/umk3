from ..media.Client import Client

import os
import cv2 as cv
import mediapipe as mp
import time

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

#FPS = 60
class Landmarker():
    def __init__(self, cam_index:int = 0, model_path:str = 'hand_landmarker.task', preserveVideo:bool = False):
        self.index = cam_index
        self.model_path = model_path
        self.preserve = preserveVideo
        BaseOptions = mp.tasks.BaseOptions
        HandLandmarker = mp.tasks.vision.HandLandmarker
        HandLandmarkerOpts = mp.tasks.vision.HandLandmarkerOptions
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
    def fingers_status(detection_result):
        """Returns List of bools whether fingers are raised or not (tip above knuckle)"""

        status_all_hands = []

        THUMB_TIP, THUMB_IP = 4, 3
        FINGER_TIPS = [8, 12, 16, 20]
        FINGER_MCPS = [5, 9, 13, 17] # Knuckles

        if not detection_result.hand_landmarks:
            return status_all_hands

        # Must account for whether webcam is flipped or not:
        for index, hand_landmarks in enumerate(detection_result.hand_landmarks):
            raised_fingers = []
            is_right = detection_result.handedness[index][0].category_name == 'Right'
            # Flipping Landmarks are different per hand though
            if is_right:
                thumb_up = hand_landmarks[THUMB_TIP].x < hand_landmarks[THUMB_IP].x
                flipped = hand_landmarks[THUMB_IP].x > hand_landmarks[17].x
            else:
                thumb_up = hand_landmarks[THUMB_TIP].x > hand_landmarks[THUMB_IP].x
                flipped = hand_landmarks[THUMB_IP].x < hand_landmarks[17].x
            thumb_up = not thumb_up if flipped else thumb_up
            raised_fingers.append(thumb_up)

            for tip, knuckle in zip(FINGER_TIPS, FINGER_MCPS):
                raised_fingers.append(hand_landmarks[tip].y < hand_landmarks[knuckle].y)
            status_all_hands.append(raised_fingers)
        return status_all_hands

    @staticmethod
    def check_pose(finger_data, index):
        """Check the passed hands data against the dictionary of hand poses"""
        # 0-4, 0 being thumb. True means extended
        poses = {
            "open_palm": [True, True, True, True, True],
            "peace": [False, True, True, False, False],
            "shaka": [True, False, False, False, True],
            "closed_fist": [False, False, False, False, False],
            "i": [False, False, False, False, True],
            "point": [False, True, False, False, False],
            "spiderman": [False, True, False, False, True],
            "justin": [False, False, True, False, False],
            "rock_on": [True, True, False, False, True]
        }

        target = finger_data[index]
        pose = [key for key, val in poses.items() if val == target]

        return(pose[0])

    @staticmethod
    def draw_landmarks_on_image(rgb_image, detection_result):
        """Draws the landmarks of each hand on the image"""
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

    @staticmethod
    def pose_to_cmd(pose):
        commands = {
            "open_palm": "pause",
            "i":"back5",
            "point":"skip5",
            "shaka":"listen",
        }

        print(commands.get(pose, "No command found"))
        return commands.get(pose, "No command found")

    def open_cam(self):
        """Open camera at the previously chosen index & begin gesture recognition"""
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

            status_fingers = self.fingers_status(res)
            num_hands = len(status_fingers)
            try:
                if num_hands >= 1:
                    first = self.check_pose(status_fingers, 0)
                    print(first)
                    #Client.recieve_command(self.pose_to_cmd(first).encode('utf-8'))
                if num_hands >= 2:
                    second = self.check_pose(status_fingers, 1)
                    print(second)
                    #Client.recieve_command(self.pose_to_cmd(second).encode('utf-8'))
            except IndexError:
                # Most likely because hands offscreen, ignore
                pass

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
