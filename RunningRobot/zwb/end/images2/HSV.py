#
#
# ###############################绿色
# import cv2
# import numpy as np
#
# """
# 功能：读取一张图片，显示出来，转化为HSV色彩空间
#      并通过滑块调节HSV阈值，实时显示
# """
#
# image = cv2.imread('./all3/140.jpg')  # 根据路径读取一张图片，opencv读出来的是BGR模式
# # image = cv2.imread('./green_bridge_1/pic_chest_1.png')  # 根据路径读取一张图片，opencv读出来的是BGR模式
# print(image.shape)
# cv2.imshow("BGR", image)  # 显示图片
#
#
# hsv_low = np.array([50, 100, 80])#绿色桥
# hsv_high = np.array([80, 255, 255])
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
# # hsv_low2 = np.array([45, 75, 40])#正常
# # hsv_high2 = np.array([90, 255, 210])
# # hsv_low2 = np.array([50, 75, 30])#前射强光
# # hsv_high2 = np.array([100, 255, 210])
# hsv_low2 = np.array([60, 90, 40])#绿色坑
# hsv_high2 = np.array([80, 255, 255])
# hsv_low3 = np.array([60, 100, 80])#晚上，进入前
# hsv_high3 = np.array([80, 255, 255])
# # hsv_low3 = np.array([60, 55, 40])#晚上，进入后
# # hsv_high3 = np.array([80, 255, 255])
# while True:
#     dst = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)  # BGR转HSV
#     dst1 = cv2.inRange(dst, hsv_low, hsv_high)  # 通过HSV的高低阈值，提取图像部分区域
#     dst2 = cv2.inRange(dst, hsv_low2, hsv_high2)
#     dst3 = cv2.inRange(dst, hsv_low3, hsv_high3)
#
#     # dst_yu = dst1&dst2&dst3
#     # dst_huo = dst1|dst2|dst3
#     cv2.imshow('dst1', dst1)
#     cv2.imshow('dst2', dst2)
#     cv2.imshow('dst3', dst3)
#     # cv2.imshow('dst_yu', dst_yu)
#     # cv2.imshow('dst_huo', dst_huo)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
# cv2.destroyAllWindows()



# #############################蓝色
# # import cv2
# # import numpy as np
# #
# # """
# # 功能：读取一张图片，显示出来，转化为HSV色彩空间
# #      并通过滑块调节HSV阈值，实时显示
# # """
# #
# # # image = cv2.imread('./blue_bridge_1/pic_chest_51.png')  # 根据路径读取一张图片，opencv读出来的是BGR模式
# # image = cv2.imread('./all/pic_head114.png')  # 根据路径读取一张图片，opencv读出来的是BGR模式
# # print(image.shape)
# # cv2.imshow("BGR", image)  # 显示图片
# #
# #
# # hsv_low = np.array([50, 160, 40])
# # hsv_high = np.array([120, 255, 255])
# #
# # # 下面几个函数，写得有点冗余
# #
# #
# # def h_low(value):
# #     hsv_low[0] = value
# #
# #
# # def h_high(value):
# #     hsv_high[0] = value
# #
# #
# # def s_low(value):
# #     hsv_low[1] = value
# #
# #
# # def s_high(value):
# #     hsv_high[1] = value
# #
# #
# # def v_low(value):
# #     hsv_low[2] = value
# #
# #
# # def v_high(value):
# #     hsv_high[2] = value
# #
# #
# # cv2.namedWindow('image', cv2.WINDOW_AUTOSIZE)
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
# # hsv_low2 = np.array([50, 160, 110])#正常
# # hsv_high2 = np.array([120, 255, 255])
# # hsv_low2 = np.array([50, 95, 90])#前射强光
# # hsv_high2 = np.array([120, 255, 255])
# hsv_low2 = np.array([50, 160, 40])#新的蓝色（栏杆）
# hsv_high2 = np.array([120, 255, 255])
# # hsv_low2 = np.array([50, 95, 120])#新的蓝色（桥）
# # hsv_high2 = np.array([120, 255, 255])
# # hsv_low2 = np.array([68, 105, 53])#新的蓝色（坑）
# # hsv_high2 = np.array([120, 255, 255])
# hsv_low3 = np.array([50, 95, 120])
# hsv_high3 = np.array([120, 255, 255])
# while True:
#     dst = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)  # BGR转HSV
#     dst1 = cv2.inRange(dst, hsv_low, hsv_high)  # 通过HSV的高低阈值，提取图像部分区域
#     dst2 = cv2.inRange(dst, hsv_low2, hsv_high2)
#     dst3 = cv2.inRange(dst, hsv_low3, hsv_high3)
#     # dst_yu = dst1&dst2&dst3
#     # dst_huo = dst1|dst2|dst3
#     cv2.imshow('dst1', dst1)
#     cv2.imshow('dst2', dst2)
#     cv2.imshow('dst3', dst3)
#     # cv2.imshow('dst_yu', dst_yu)
#     # cv2.imshow('dst_huo', dst_huo)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
# cv2.destroyAllWindows()
# #
#

##############################黑色
import cv2
import numpy as np

"""
功能：读取一张图片，显示出来，转化为HSV色彩空间
     并通过滑块调节HSV阈值，实时显示
"""


image = cv2.imread('./IMG_20211016_133814.jpg')  # 根据路径读取一张图片，opencv读出来的是BGR模式
# Chest_img_copy = cv2.resize(image, (480, 640), interpolation=cv2.INTER_CUBIC)
# image = cv2.imread('./save/1/23.jpg')  # 根据路径读取一张图片，opencv读出来的是BGR模式
print(image.shape)
cv2.imshow("BGR", image)  # 显示图片


hsv_low = np.array([0, 0, 0])#新的黑色
hsv_high = np.array([110, 160, 80])

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


hsv_low2 = np.array([0, 0, 0])#晚上地雷(白天可以，更好
hsv_high2 = np.array([130, 160, 80])
hsv_low3 = np.array([0, 0, 0])
hsv_high3 = np.array([120, 255, 50])

while True:
    dst = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)  # BGR转HSV
    dst1 = cv2.inRange(dst, hsv_low, hsv_high)  # 通过HSV的高低阈值，提取图像部分区域
    dst2 = cv2.inRange(dst, hsv_low2, hsv_high2)
    dst3 = cv2.inRange(dst, hsv_low3, hsv_high3)

    # dst_yu = dst1&dst2&dst3
    # dst_huo = dst1|dst2|dst3
    cv2.imshow('dst1', dst1)
    cv2.imshow('dst2', dst2)
    cv2.imshow('dst3', dst3)
    # cv2.imshow('dst_yu', dst_yu)
    # cv2.imshow('dst_huo', dst_huo)
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