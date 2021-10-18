#!/usr/bin/env python3
# coding:utf-8

import cv2
import math
import numpy as np
import threading
import time
import datetime
import CMDcontrol 

cap_chest = cv2.VideoCapture(0)
cap_head = cv2.VideoCapture(2)  #扑捉到的视频流

chest_ret = False     # 读取胸部图像标志位
head_ret = False      # 读取头部图像标志位  
ChestOrg_img = None   # 胸部图像当前帧      
HeadOrg_img = None    # 头部图像当前帧      

################################################读取图像线程#################################################
# 接收视频流，转化为一帧帧图像；未成功接收报错
# def get_img():
#    global cap_chest,cap_head
#    global ChestOrg_img,HeadOrg_img,chest_ret,head_ret
#    while True:
        

# 开启读取图像线程
# th1 = threading.Thread(target=get_img)
# th1.setDaemon(True)
# th1.start()

####################################################主程序###################################################
if __name__ == '__main__':
    
    while True:
        if cap_chest.isOpened() and cap_head.isOpened():      #摄像头初始化成功？
            chest_ret, ChestOrg_img = cap_chest.read()
            head_ret, HeadOrg_img = cap_head.read()    #读取该帧图像，及是否成功的标志位
            if (chest_ret == False) or (head_ret == False):
                print("faile ------------------")
            if HeadOrg_img is None:
                print("HeadOrg_img error")
            if ChestOrg_img is None:
                print("ChestOrg_img error")           # 接收有问题就报错
            else:
                ChestOrg_img_gray = cv2.cvtColor(ChestOrg_img,cv2.COLOR_BGR2GRAY)
                cv2.imshow('Head_image', HeadOrg_img) # 显示实时图像，标题为'current_image_gray'
                if cv2.waitKey(1) & 0xFF == ord('q'): # 接收到键盘的ASCII码和q一样；每帧播放25秒
                    break
        else:
            time.sleep(0.01)
            print("58L pic error")    #报错,摄像头未成功开启
             
    cap_chest.release()
    cap_head.release
    cv2.destroyAllWindows()
    print('end')
            
        