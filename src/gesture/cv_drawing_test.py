import cv2 as cv
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


mp_hands = mp.tasks.vision.HandLandmarksConnections
mp_drawing = mp.tasks.vision.drawing_utils
mp_drawing_styles = mp.tasks.vision.drawing_styles

MARGIN = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
HANDEDNESS_TEXT_COLOR = (88, 205, 54) # vibrant green

def draw_landmarks_on_image(rgb_image, detection_result):
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

image_path = 'example_images/lavigne.jpeg'

base_opts = python.BaseOptions(model_asset_path='hand_landmarker.task')
opts = vision.HandLandmarkerOptions(base_options = base_opts, num_hands = 2)

detector = vision.HandLandmarker.create_from_options(opts)

image = mp.Image.create_from_file(image_path)

res = detector.detect(image)

annotated = draw_landmarks_on_image(image.numpy_view(), res)
cv.imshow('Window', annotated)

#
#img = cv.imread(image_path)
#if img is None:
#    print('Bad image')
#else:
#    cv.imshow(image_path, img)
#
#    cv.waitKey(0)
#    cv.destroyAllWindows()

#dimensions = (500,500, 3)
#canvas = np.zeros(dimensions, dtype='uint8')
#cv.circle(canvas,(250,250), 50, (0,0,255), -1)
#
#cv.imshow('Canvas', canvas)
cv.waitKey(0)
cv.destroyAllWindows()
