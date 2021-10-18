import cv2
import numpy as np
import math
color_range = {
    'yellow_door': [(20, 140, 60), (40, 240, 150)],
    'black_door': [(25, 25, 10), (110, 150, 30)],
    'black_gap': [(0, 0, 0), (180, 255, 70)],
    'yellow_hole': [(20, 120, 95), (30, 250, 190)],
    'black_hole': [(5, 80, 20), (40, 255, 100)],
    'chest_red_floor': [(0, 40, 60), (20, 200, 190)],
    'chest_red_floor1': [(0, 100, 60), (20, 200, 210)],
    'chest_red_floor2': [(110, 100, 60), (180, 200, 210)],
    'green_bridge': [(45, 75, 40), (90, 255, 210)],
    # 'green_bridge': [(52, 106, 91), (90, 255, 255)],
    'blue_bridge': [(50, 160, 60), (120, 255, 255)],
    # 'black_dilei': [(0, 0, 0), (110, 160, 70)],
    'black_dilei': [(0, 0, 0), (120, 255, 50)],
    'white_dilei': [(60, 0, 70), (100, 255, 255)],
    'blue_langan': [(50, 160, 60), (120, 255, 255)]
}
OrgFrame= cv2.imread('./images/langan4/pic_head74.png')

hsv = cv2.cvtColor(OrgFrame, cv2.COLOR_BGR2HSV)
hsv = cv2.GaussianBlur(hsv, (3, 3), 0)
Imask = cv2.inRange(hsv, color_range['blue_langan'][0], color_range['blue_langan'][1])
Imask = cv2.erode(Imask, None, iterations=2)
Imask = cv2.dilate(Imask, np.ones((3, 3), np.uint8), iterations=2)

_, contours, hierarchy = cv2.findContours(Imask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)  # 找出所有轮廓
# print("contours lens:",len(contours))
def get_all_area(contours,contour_area_threshold = 0):
    contour_area_sum = 0
    for c in contours:
        contour_area_now = math.fabs(cv2.contourArea(c))
        if contour_area_now > contour_area_threshold:
            contour_area_sum += contour_area_now
    return contour_area_sum
area = get_all_area(contours, 500)
print('area:',area)
cv2.drawContours(OrgFrame, contours, -1, (255, 0, 255), 2)
cv2.imshow('src',OrgFrame)
cv2.imshow('Imask',Imask)
cv2.waitKey(0)

