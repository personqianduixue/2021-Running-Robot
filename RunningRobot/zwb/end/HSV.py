

# ###############################绿色
# import cv2
# import numpy as np
#
# """
# 功能：读取一张图片，显示出来，转化为HSV色彩空间
#      并通过滑块调节HSV阈值，实时显示
# """
#
# image = cv2.imread('./green_bridge_2/227.jpg')  # 根据路径读取一张图片，opencv读出来的是BGR模式
# # image = cv2.imread('./save/1/23.jpg')  # 根据路径读取一张图片，opencv读出来的是BGR模式
# print(image.shape)
# cv2.imshow("BGR", image)  # 显示图片
#
#
# hsv_low = np.array([50, 75, 60])
# hsv_high = np.array([80, 255, 210])
#
# # 下面几个函数，写得有点冗余
#
#
# def h_low(value):
#     hsv_low[0] = value
#
#
# def h_high(value):
#     hsv_high[0] = value
#
#
# def s_low(value):
#     hsv_low[1] = value
#
#
# def s_high(value):
#     hsv_high[1] = value
#
#
# def v_low(value):
#     hsv_low[2] = value
#
#
# def v_high(value):
#     hsv_high[2] = value
#
#
# cv2.namedWindow('image', cv2.WINDOW_AUTOSIZE)
#
# # H low：
# #    0：指向整数变量的可选指针，该变量的值反映滑块的初始位置。
# #  179：表示滑块可以达到的最大位置的值为179，最小位置始终为0。
# # h_low：指向每次滑块更改位置时要调用的函数的指针，指针指向h_low元组，有默认值0。
# #（此函数的原型应为void
# #XXX(int, void *); ，其中第一个参数是轨迹栏位置，第二个参数是用户数据（请参阅下一个参数）。如果回调是NULL指针，则不调用任何回调，而仅更新值。）
# cv2.createTrackbar('H low', 'image', 0, 179, h_low)
# cv2.createTrackbar('H high', 'image', 0, 179, h_high)
# cv2.createTrackbar('S low', 'image', 0, 255, s_low)
# cv2.createTrackbar('S high', 'image', 0, 255, s_high)
# cv2.createTrackbar('V low', 'image', 0, 255, v_low)
# cv2.createTrackbar('V high', 'image', 0, 255, v_high)
#
# cv2.setTrackbarPos('H low', 'image',  hsv_low[0])
# cv2.setTrackbarPos('H high', 'image', hsv_high[0])
# cv2.setTrackbarPos('S low', 'image',  hsv_low[1])
# cv2.setTrackbarPos('S high', 'image',  hsv_high[1])
# cv2.setTrackbarPos('V low', 'image',  hsv_low[2])
# cv2.setTrackbarPos('V high', 'image', hsv_high[2])
#
#
# hsv_low2 = np.array([45, 75, 40])
# hsv_high2 = np.array([90, 255, 210])
# hsv_low3 = np.array([45, 110, 20])
# hsv_high3 = np.array([90, 255, 210])
#
# while True:
#     dst = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)  # BGR转HSV
#     dst1 = cv2.inRange(dst, hsv_low, hsv_high)  # 通过HSV的高低阈值，提取图像部分区域
#     dst2 = cv2.inRange(dst, hsv_low2, hsv_high2)
#     dst3 = cv2.inRange(dst, hsv_low3, hsv_high3)
#
#     dst_yu = dst1&dst2&dst3
#     dst_huo = dst1|dst2|dst3
#     cv2.imshow('dst1', dst1)
#     cv2.imshow('dst2', dst2)
#     cv2.imshow('dst3', dst3)
#     cv2.imshow('dst_yu', dst_yu)
#     cv2.imshow('dst_huo', dst_huo)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
# cv2.destroyAllWindows()



###############################蓝色
# import cv2
# import numpy as np
#
# """
# 功能：读取一张图片，显示出来，转化为HSV色彩空间
#      并通过滑块调节HSV阈值，实时显示
# """
#
# # image = cv2.imread('./save_blue_bridge_1/1.jpg')  # 根据路径读取一张图片，opencv读出来的是BGR模式
# image = cv2.imread('./blue_bridge_2/130.jpg')  # 根据路径读取一张图片，opencv读出来的是BGR模式
# print(image.shape)
# cv2.imshow("BGR", image)  # 显示图片
#
#
# hsv_low = np.array([50, 160, 110])
# hsv_high = np.array([120, 255, 255])
#
# # 下面几个函数，写得有点冗余
#
#
# def h_low(value):
#     hsv_low[0] = value
#
#
# def h_high(value):
#     hsv_high[0] = value
#
#
# def s_low(value):
#     hsv_low[1] = value
#
#
# def s_high(value):
#     hsv_high[1] = value
#
#
# def v_low(value):
#     hsv_low[2] = value
#
#
# def v_high(value):
#     hsv_high[2] = value
#
#
# cv2.namedWindow('image', cv2.WINDOW_AUTOSIZE)
#
# # H low：
# #    0：指向整数变量的可选指针，该变量的值反映滑块的初始位置。
# #  179：表示滑块可以达到的最大位置的值为179，最小位置始终为0。
# # h_low：指向每次滑块更改位置时要调用的函数的指针，指针指向h_low元组，有默认值0。
# #（此函数的原型应为void
# #XXX(int, void *); ，其中第一个参数是轨迹栏位置，第二个参数是用户数据（请参阅下一个参数）。如果回调是NULL指针，则不调用任何回调，而仅更新值。）
# cv2.createTrackbar('H low', 'image', 0, 179, h_low)
# cv2.createTrackbar('H high', 'image', 0, 179, h_high)
# cv2.createTrackbar('S low', 'image', 0, 255, s_low)
# cv2.createTrackbar('S high', 'image', 0, 255, s_high)
# cv2.createTrackbar('V low', 'image', 0, 255, v_low)
# cv2.createTrackbar('V high', 'image', 0, 255, v_high)
#
# cv2.setTrackbarPos('H low', 'image',  hsv_low[0])
# cv2.setTrackbarPos('H high', 'image', hsv_high[0])
# cv2.setTrackbarPos('S low', 'image',  hsv_low[1])
# cv2.setTrackbarPos('S high', 'image',  hsv_high[1])
# cv2.setTrackbarPos('V low', 'image',  hsv_low[2])
# cv2.setTrackbarPos('V high', 'image', hsv_high[2])
#
#
# hsv_low2 = np.array([50, 160, 60])
# hsv_high2 = np.array([120, 255, 255])
# hsv_low3 = np.array([50, 100, 110])
# hsv_high3 = np.array([120, 255, 255])
# while True:
#     dst = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)  # BGR转HSV
#     dst1 = cv2.inRange(dst, hsv_low, hsv_high)  # 通过HSV的高低阈值，提取图像部分区域
#     dst2 = cv2.inRange(dst, hsv_low2, hsv_high2)
#     dst3 = cv2.inRange(dst, hsv_low3, hsv_high3)
#     dst_yu = dst1&dst2&dst3
#     dst_huo = dst1|dst2|dst3
#     cv2.imshow('dst1', dst1)
#     cv2.imshow('dst2', dst2)
#     cv2.imshow('dst3', dst3)
#     cv2.imshow('dst_yu', dst_yu)
#     cv2.imshow('dst_huo', dst_huo)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
# cv2.destroyAllWindows()



##############################黑色
import cv2
import math
import numpy as np
import threading
import time
import datetime

import CMDcontrol

robot_IP = "192.168.110.42"
camera_out = "chest"
stream_pic = False
action_DEBUG = False
#################################################初始化#########################################################


cap_chest = cv2.VideoCapture(0)
cap_head = cv2.VideoCapture(2)
'''stream_head = "http://192.168.137.3:8082/?action=stream?dummy=param.mjpg"
cap_head = cv2.VideoCapture(stream_head)
stream_chest = "http://192.168.137.3:8080/?action=stream?dummy=param.mjpg"
cap_chest = cv2.VideoCapture(stream_chest)'''

box_debug = True
debug = False
img_debug = True


state = 1           #用数字用来标志第几关
step = 0
state_sel = 'hole'  #名称来标志第几关
reset = 0
skip = 0



chest_ret = False     # 读取图像标志位--\
ret = False           # 读取图像标志位  |
ChestOrg_img = None   # 原始图像更新    |
HeadOrg_img = None    # 原始图像更新    |这四个都是读取摄像头时的返回参数
ChestOrg_copy = None
HeadOrg_copy = None


chest_r_width = 480
chest_r_height = 640
head_r_width = 640
head_r_height = 480


################################################读取图像线程#################################################
def get_img():
    global ChestOrg_img,HeadOrg_img,chest_ret,ret
    global cap_chest,cap_head
    while True:
        if cap_chest.isOpened():
            
            chest_ret, ChestOrg_img = cap_chest.read()
            ret, HeadOrg_img = cap_head.read()
            if (chest_ret == False) or (ret == False):
                print("ret faile ------------------")
            if HeadOrg_img is None:
                print("HeadOrg_img error")
            if ChestOrg_img is None:
                print("ChestOrg_img error")
                
        else:
            time.sleep(0.01)
            ret=True
            print("58L pic  error ")

# 读取图像线程
th1 = threading.Thread(target=get_img)
th1.setDaemon(True)
th1.start()

"""
功能：读取一张图片，显示出来，转化为HSV色彩空间
     并通过滑块调节HSV阈值，实时显示
"""


Corg_img0 = ChestOrg_img.copy()
Corg_img0 = np.rot90(Corg_img0)
Corg_img = Corg_img0.copy()
image = cv2.imread(Corg_img)  # 根据路径读取一张图片，opencv读出来的是BGR模式
# image = cv2.imread('./save/1/23.jpg')  # 根据路径读取一张图片，opencv读出来的是BGR模式
print(image.shape)
cv2.imshow("BGR", image)  # 显示图片


hsv_low = np.array([0, 0, 0])
hsv_high = np.array([100, 160, 55])

# 下面几个函数，写得有点冗余


def h_low(value):
    hsv_low[0] = value


def h_high(value):
    hsv_high[0] = value


def s_low(value):
    hsv_low[1] = value


def s_high(value):
    hsv_high[1] = value


def v_low(value):
    hsv_low[2] = value


def v_high(value):
    hsv_high[2] = value


cv2.namedWindow('image', cv2.WINDOW_AUTOSIZE)

# H low：
#    0：指向整数变量的可选指针，该变量的值反映滑块的初始位置。
#  179：表示滑块可以达到的最大位置的值为179，最小位置始终为0。
# h_low：指向每次滑块更改位置时要调用的函数的指针，指针指向h_low元组，有默认值0。
#（此函数的原型应为void
#XXX(int, void *); ，其中第一个参数是轨迹栏位置，第二个参数是用户数据（请参阅下一个参数）。如果回调是NULL指针，则不调用任何回调，而仅更新值。）
cv2.createTrackbar('H low', 'image', 0, 179, h_low)
cv2.createTrackbar('H high', 'image', 0, 179, h_high)
cv2.createTrackbar('S low', 'image', 0, 255, s_low)
cv2.createTrackbar('S high', 'image', 0, 255, s_high)
cv2.createTrackbar('V low', 'image', 0, 255, v_low)
cv2.createTrackbar('V high', 'image', 0, 255, v_high)

cv2.setTrackbarPos('H low', 'image',  hsv_low[0])
cv2.setTrackbarPos('H high', 'image', hsv_high[0])
cv2.setTrackbarPos('S low', 'image',  hsv_low[1])
cv2.setTrackbarPos('S high', 'image',  hsv_high[1])
cv2.setTrackbarPos('V low', 'image',  hsv_low[2])
cv2.setTrackbarPos('V high', 'image', hsv_high[2])


hsv_low2 = np.array([0, 0, 0])
hsv_high2 = np.array([120, 200, 60])
hsv_low3 = np.array([0, 0, 0])
hsv_high3 = np.array([120, 200, 50])

while True:
    dst = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)  # BGR转HSV
    dst1 = cv2.inRange(dst, hsv_low, hsv_high)  # 通过HSV的高低阈值，提取图像部分区域
    dst2 = cv2.inRange(dst, hsv_low2, hsv_high2)
    dst3 = cv2.inRange(dst, hsv_low3, hsv_high3)

    dst_yu = dst1&dst2&dst3
    dst_huo = dst1|dst2|dst3
    cv2.imshow('dst1', dst1)
    cv2.imshow('dst2', dst2)
    cv2.imshow('dst3', dst3)
    cv2.imshow('dst_yu', dst_yu)
    cv2.imshow('dst_huo', dst_huo)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cv2.destroyAllWindows()






# ###############################白色
# import cv2
# import numpy as np
#
# """
# 功能：读取一张图片，显示出来，转化为HSV色彩空间
#      并通过滑块调节HSV阈值，实时显示
# """
#
# image = cv2.imread('./save_dilei3/210.jpg')  # 根据路径读取一张图片，opencv读出来的是BGR模式
# # image = cv2.imread('./save/1/23.jpg')  # 根据路径读取一张图片，opencv读出来的是BGR模式
# print(image.shape)
# cv2.imshow("BGR", image)  # 显示图片
#
#
# hsv_low = np.array([60, 0, 70])
# hsv_high = np.array([100, 255, 255])
#
# # 下面几个函数，写得有点冗余
#
#
# def h_low(value):
#     hsv_low[0] = value
#
#
# def h_high(value):
#     hsv_high[0] = value
#
#
# def s_low(value):
#     hsv_low[1] = value
#
#
# def s_high(value):
#     hsv_high[1] = value
#
#
# def v_low(value):
#     hsv_low[2] = value
#
#
# def v_high(value):
#     hsv_high[2] = value
#
#
# cv2.namedWindow('image', cv2.WINDOW_AUTOSIZE)
#
# # H low：
# #    0：指向整数变量的可选指针，该变量的值反映滑块的初始位置。
# #  179：表示滑块可以达到的最大位置的值为179，最小位置始终为0。
# # h_low：指向每次滑块更改位置时要调用的函数的指针，指针指向h_low元组，有默认值0。
# #（此函数的原型应为void
# #XXX(int, void *); ，其中第一个参数是轨迹栏位置，第二个参数是用户数据（请参阅下一个参数）。如果回调是NULL指针，则不调用任何回调，而仅更新值。）
# cv2.createTrackbar('H low', 'image', 0, 179, h_low)
# cv2.createTrackbar('H high', 'image', 0, 179, h_high)
# cv2.createTrackbar('S low', 'image', 0, 255, s_low)
# cv2.createTrackbar('S high', 'image', 0, 255, s_high)
# cv2.createTrackbar('V low', 'image', 0, 255, v_low)
# cv2.createTrackbar('V high', 'image', 0, 255, v_high)
#
# cv2.setTrackbarPos('H low', 'image',  hsv_low[0])
# cv2.setTrackbarPos('H high', 'image', hsv_high[0])
# cv2.setTrackbarPos('S low', 'image',  hsv_low[1])
# cv2.setTrackbarPos('S high', 'image',  hsv_high[1])
# cv2.setTrackbarPos('V low', 'image',  hsv_low[2])
# cv2.setTrackbarPos('V high', 'image', hsv_high[2])
#
#
# hsv_low2 = np.array([45, 75, 40])
# hsv_high2 = np.array([90, 255, 210])
# hsv_low3 = np.array([45, 110, 20])
# hsv_high3 = np.array([90, 255, 210])
#
# while True:
#     dst = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)  # BGR转HSV
#     dst1 = cv2.inRange(dst, hsv_low, hsv_high)  # 通过HSV的高低阈值，提取图像部分区域
#     dst2 = cv2.inRange(dst, hsv_low2, hsv_high2)
#     dst3 = cv2.inRange(dst, hsv_low3, hsv_high3)
#
#     dst_yu = dst1&dst2&dst3
#     dst_huo = dst1|dst2|dst3
#     cv2.imshow('dst1', dst1)
#     cv2.imshow('dst2', dst2)
#     cv2.imshow('dst3', dst3)
#     cv2.imshow('dst_yu', dst_yu)
#     cv2.imshow('dst_huo', dst_huo)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
# cv2.destroyAllWindows()