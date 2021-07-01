import cv2
import tensorflow as tf
from sklearn.metrics import f1_score
import requests
import xmltodict
import json
import numpy as np
import re
import warnings
warnings.filterwarnings("ignore")

plateCascade = cv2.CascadeClassifier('indian_license_plate.xml')


def plate_detect(img):
    plateImg = img.copy()
    roi = img.copy()
    plate_part = np.array([])
    plateRect = plateCascade.detectMultiScale(
        plateImg, scaleFactor=1.2, minNeighbors=7)
    for (x, y, w, h) in plateRect:
        roi_ = roi[y:y+h, x:x+w, :]
        plate_part = roi[y:y+h, x:x+w, :]
        cv2.rectangle(plateImg, (x+2, y), (x+w-3, y+h-5), (0, 255, 0), 3)
    # print(type(roi))
    # print(roi.shape)
    return plateImg, plate_part


def find_contours(dimensions, img):

    # finding all contours in the image using
    # retrieval mode: RETR_TREE
    # contour approximation method: CHAIN_APPROX_SIMPLE
    cntrs, _ = cv2.findContours(
        img.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Approx dimensions of the contours
    lower_width = dimensions[0]
    upper_width = dimensions[1]
    lower_height = dimensions[2]
    upper_height = dimensions[3]

    # Check largest 15 contours for license plate character respectively
    cntrs = sorted(cntrs, key=cv2.contourArea, reverse=True)[:15]

    ci = cv2.imread('contour.jpg')

    x_cntr_list = []
    target_contours = []
    img_res = []
    for cntr in cntrs:
        # detecting contour in binary image and returns the coordinates of rectangle enclosing it
        intX, intY, intWidth, intHeight = cv2.boundingRect(cntr)

        # checking the dimensions of the contour to filter out the characters by contour's size
        if intWidth > lower_width and intWidth < upper_width and intHeight > lower_height and intHeight < upper_height:
            x_cntr_list.append(intX)
            char_copy = np.zeros((44, 24))
            # extracting each character using the enclosing rectangle's coordinates.
            char = img[intY:intY+intHeight, intX:intX+intWidth]
            char = cv2.resize(char, (20, 40))
            cv2.rectangle(ci, (intX, intY), (intWidth+intX,
                          intY+intHeight), (50, 21, 200), 2)
            #plt.imshow(ci, cmap='gray')
            char = cv2.subtract(255, char)
            char_copy[2:42, 2:22] = char
            char_copy[0:2, :] = 0
            char_copy[:, 0:2] = 0
            char_copy[42:44, :] = 0
            char_copy[:, 22:24] = 0
            # List that stores the character's binary image (unsorted)
            img_res.append(char_copy)

    # return characters on ascending order with respect to the x-coordinate

    # plt.show()
    # arbitrary function that stores sorted list of character indeces
    indices = sorted(range(len(x_cntr_list)), key=lambda k: x_cntr_list[k])
    img_res_copy = []
    for idx in indices:
        # stores character images according to their index
        img_res_copy.append(img_res[idx])
    img_res = np.array(img_res_copy)

    return img_res


def segment_characters(image):

    # pre-processing cropped image of plate
    # threshold: convert to pure b&w with sharpe edges
    # erod: increasing the backgroung black
    # dilate: increasing the char white
    img_lp = cv2.resize(image, (333, 75))
    img_gray_lp = cv2.cvtColor(img_lp, cv2.COLOR_BGR2GRAY)
    _, img_binary_lp = cv2.threshold(
        img_gray_lp, 200, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    img_binary_lp = cv2.erode(img_binary_lp, (3, 3))
    img_binary_lp = cv2.dilate(img_binary_lp, (3, 3))

    LP_WIDTH = img_binary_lp.shape[0]
    LP_HEIGHT = img_binary_lp.shape[1]
    img_binary_lp[0:3, :] = 255
    img_binary_lp[:, 0:3] = 255
    img_binary_lp[72:75, :] = 255
    img_binary_lp[:, 330:333] = 255

    # estimations of character contours sizes of cropped license plates
    dimensions = [LP_WIDTH/6,
                  LP_WIDTH/2,
                  LP_HEIGHT/10,
                  2*LP_HEIGHT/3]
    #plt.imshow(img_binary_lp, cmap='gray')
    # plt.show()
    cv2.imwrite('contour.jpg', img_binary_lp)

    # getting contours
    char_list = find_contours(dimensions, img_binary_lp)

    return char_list


def f1score(y, y_pred):
    return f1_score(y, tf.math.argmax(y_pred, axis=1), average='micro')


def custom_f1score(y, y_pred):
    return tf.py_function(f1score, (y, y_pred), tf.double)


def fix_dimension(img):
    new_img = np.zeros((28, 28, 3))
    for i in range(3):
        new_img[:, :, i] = img
    return new_img


def get_vehicle_info(plate_number):
    r = requests.get(
        "http://www.regcheck.org.uk/api/reg.asmx/CheckIndia?RegistrationNumber={0}&username=asdf2".format(str(plate_number)))
    data = xmltodict.parse(r.content)
    jdata = json.dumps(data)
    df = json.loads(jdata)
    df1 = json.loads(df['Vehicle']['vehicleJson'])
    return df1


def plate_info(numberPlate):
    pattern = '^[A-Z]{2}[0-9]{1,2}([A-Z])?([A-Z]*)?[0-9]{4}$'
    if len(numberPlate) > 10:
        numberPlate = numberPlate[-10:]
        return get_vehicle_info(numberPlate)
#     else:
#         return get_vehicle_info(numberPlate)
    elif re.match(pattern, numberPlate) != None:
        return get_vehicle_info(numberPlate)
    else:
        return None
