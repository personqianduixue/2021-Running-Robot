# import cv2
# import numpy
#
# cap = cv2.VideoCapture(0)
# print(cap)
# while(True):
#     ret, frame = cap.read()
#     gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
#     cv2.imshow('frame',gray)
#     if cv2.waitKey(1)&0xFF == ord('q'):
#         break
#
# cap.release()
# # cv2.destroyAllWindows()

import cv2 as cv
import time
import numpy as np

def video_demo_chest():
    stream_chest = "http://192.168.137.4:8080/?action=stream?dummy=param.mjpg"
    cap_chest = cv.VideoCapture(stream_chest)
    j=1
    while True:
        # 调用摄像机
        ref, frame = cap_chest.read()
        # 输出图像,第一个为窗口名字
        frame=np.rot90(frame)
        #frame=frame[230:585, 0:480]
        # cv.imshow('frame', frame)
        # 10s显示图像，若过程中按“Esc”退出,若按“s”保存照片并推出
        c = cv.waitKey(1) & 0xff
        if c == 27:
            # 简单暴力释放所有窗口
            cv.destroyAllWindows()
            break

        print(j)
        # cv.imwrite('./images/pic_chest_%s.png'%j, frame)
        cv.imwrite('./images/%s.jpg' % j, frame)
        j=j+1
        time.sleep(0.1)

def video_demo_head():
    # 0是代表摄像头编号，只有一个的话默认为0
    stream_head = "http://192.168.137.3:8082/?action=stream?dummy=param.mjpg"
    cap_head = cv.VideoCapture(stream_head)
    i=1
    while True:
        # 调用摄像机
        ref, frame = cap_head.read()
        # 输出图像,第一个为窗口名字
        cv.imshow('frame', frame)
        # 10s显示图像，若过程中按“Esc”退出,若按“s”保存照片并推出
        c = cv.waitKey(10) & 0xff
        if c == 27:
            # 简单暴力释放所有窗口
            cv.destroyAllWindows()
            break

        print(i)
        cv.imwrite('./images/pic_head%s.png'%i, frame)
        i=i+1
        time.sleep(0.1)

def video_demo_all():
    # 0是代表摄像头编号，只有一个的话默认为0
    stream_head = "http://192.168.137.4:8082/?action=stream?dummy=param.mjpg"
    cap_head = cv.VideoCapture(stream_head)
    stream_chest = "http://192.168.137.4:8080/?action=stream?dummy=param.mjpg"
    cap_chest = cv.VideoCapture(stream_chest)
    i=1
    while True:
        # 调用摄像机
        ref_head, frame_head = cap_head.read()
        ref_head, frame_chest = cap_chest.read()
        frame_chest_rot = np.rot90(frame_chest)

        # 输出图像,第一个为窗口名字
        # cv.imshow('frame_head', frame_head)
        # cv.imshow('frame_chest', frame_chest)
        # 10s显示图像，若过程中按“Esc”退出,若按“s”保存照片并推出
        c = cv.waitKey(10) & 0xff
        if c == 27:
            # 简单暴力释放所有窗口
            cv.destroyAllWindows()
            break

        print(i)
        cv.imwrite('./images/pic_head%s.png'%i, frame_head)
        cv.imwrite('./images/pic_chest%s.png' % i, frame_chest)
        cv.imwrite('./images/pic_chest_rot%s.png' % i, frame_chest_rot)
        i=i+1
        time.sleep(0.5)


if __name__ == '__main__':
    cv.waitKey()
    # video_demo_chest()
    #video_demo_head()
    video_demo_all()
