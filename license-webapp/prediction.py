from preprocess import plate_detect, find_contours, segment_characters, f1score, custom_f1score, fix_dimension, get_vehicle_info, plate_info
import matplotlib.pyplot as plt
from keras import models
import keras.backend as K
import cv2
import numpy as np
import warnings
warnings.filterwarnings("ignore")

# import all preprocess functions

model = models.load_model('license_plate_character.pkl', custom_objects={
                          'custom_f1score': custom_f1score})


def fix_dimension(img):
    new_img = np.zeros((28, 28, 3))
    for i in range(3):
        new_img[:, :, i] = img
    return new_img


def show_results(pl_char):
    dic = {}
    characters = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    for i, c in enumerate(characters):
        dic[i] = c

    output = []
    for i, ch in enumerate(pl_char):
        img_ = cv2.resize(ch, (28, 28), interpolation=cv2.INTER_AREA)
        img = fix_dimension(img_)
        img = img.reshape(1, 28, 28, 3)
        y_ = model.predict_classes(img)[0]
        character = dic[y_]
        output.append(character)

    plate_number = ''.join(output)

    return plate_number


def runVideo(vpath):
    # license_video.mp4 have to be yours, I haven't uploaded for privacy concern
    cam = cv2.VideoCapture(vpath)
    if cam.isOpened() == False:
        print("Video not imported")

    plate_list = []
    info_list = []
    while(cam.isOpened()):
        ret, frame = cam.read()
        if ret == True:
            car_plate, plate_img = plate_detect(frame)
            #cv2.imshow("License Video", car_plate)
            if len(plate_img) > 0:
                plate_char = segment_characters(plate_img)
                # print(plate_char)
                number_plate = show_results(plate_char)
                if number_plate not in plate_list:
                    final_result = plate_info(number_plate)
                    if final_result != None:
                        plate_list.append(number_plate)
                        info_list.append(final_result)
                        break
                    # print(final_result)

            if cv2.waitKey(1) == 27:
                break
        else:
            break

    cam.release()
    cv2.destroyAllWindows()
    return info_list[0]
