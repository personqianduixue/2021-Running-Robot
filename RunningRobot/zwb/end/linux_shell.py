import time
# import eventlet#导入eventlet这个模块
# # eventlet.monkey_patch()#必须加这条代码
# import cv2
# from urllib import request
# import requests
import os
def restart_camera():
    global stream_head
    try:
        r = requests.get(url=stream_head, timeout=0.5)
        print(r.elapsed.microseconds)
    except:
        print('摄像头无响应，执行重启')
        res1=os.system("sudo service livestream.sh stop")
        res2=os.system("sudo service livestream.sh start")
        print(res1,res2)
def get_img():
    global ChestOrg_img, HeadOrg_img, chest_ret, ret
    global cap_chest, cap_head
    while True:
        if cap_chest.isOpened():

            chest_ret, ChestOrg_img = cap_chest.read()
            ret, HeadOrg_img = cap_head.read()
            if (chest_ret == False) or (ret == False):
                print("ret faile ------------------")
                # continue
            if HeadOrg_img is None:
                print("HeadOrg_img error")
                # continue
            if ChestOrg_img is None:
                print("ChestOrg_img error")
                # continue

        else:
            time.sleep(0.01)
            ret = True
            print("58L pic  error ")

# stream_head = "http://192.168.137.2:8082/?action=stream?dummy=param.mjpg"
# stream_chest = "http://192.168.137.2:8080/?action=stream?dummy=param.mjpg"
# print('start')
#
# from func_timeout import func_set_timeout
# import time
# import func_timeout
#
# @func_set_timeout(1)
# def task():
#     cap_head = cv2.VideoCapture(stream_head)
#     cap_chest = cv2.VideoCapture(stream_chest)
#     print('ok')
# task()
# r = requests.get(url=stream_head, timeout=1)
# # r = requests.get(url='https://www.baidu.com', timeout=0.5)
# print(r.elapsed.microseconds)
# # restart_camera()
# # res=request.urlopen(stream_head)
# # print(res)
# cap_head = cv2.VideoCapture(stream_head)
# cap_chest = cv2.VideoCapture(stream_chest)
#
# print(cap_chest.isOpened())
def restart():
    res1=os.system("sudo service livestream.sh stop")
    res2=os.system("sudo service livestream.sh start")
    print(res1,res2)

restart()