#!/usr/bin/env python3
# coding:utf-8

import cv2
import math
import numpy as np
import threading
import time
import datetime
import CMDcontrol

'''stream_head = "http://192.168.137.67:8082/?action=stream?dummy=param.mjpg"
stream_chest = "http://192.168.137.67:8080/?action=stream?dummy=param.mjpg"
cap_chest = cv2.VideoCapture(stream_chest)
cap_head = cv2.VideoCapture(stream_head)  #扑捉到的视频流'''

cap_chest = cv2.VideoCapture(0)
cap_head = cv2.VideoCapture(2)  

chest_ret = False     # 读取胸部图像标志位
head_ret = False      # 读取头部图像标志位  
ChestOrg_img = None   # 胸部图像当前帧      
HeadOrg_img = None    # 头部图像当前帧      

action_DEBUG = False

################################################读取图像线程#################################################
# 接收视频流，转化为一帧帧图像；未成功接收报错
def get_img():
    global cap_chest,cap_head
    global ChestOrg_img,HeadOrg_img,chest_ret,head_ret
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
            time.sleep(0.01)
            print("58L pic error")    #报错,摄像头未成功开启

# 开启读取图像线程
th1 = threading.Thread(target=get_img)
th1.setDaemon(True)
th1.start()

################################################动作执行线程#################################################
def move_action():
    global org_img
    global step, level
    global golf_angle_hole
    global golf_angle_ball, golf_angle
    global golf_dis, golf_dis_y
    global golf_angle_flag, golf_dis_flag
    global golf_angle_start, golf_dis_start
    global golf_ok
    global golf_hole, golf_ball

    CMDcontrol.CMD_transfer()

# 动作执行线程
th2 = threading.Thread(target=move_action)
th2.setDaemon(True)
th2.start()

acted_name = ""
def action_append(act_name):
    global acted_name

    if action_DEBUG == False:
        if act_name == "forwardSlow0403" and (acted_name == "Forwalk02RL" or acted_name == "Forwalk02L"):
            acted_name = "Forwalk02LR"
        elif act_name == "forwardSlow0403" and (acted_name == "Forwalk02LR" or acted_name == "Forwalk02R"):
            acted_name = "Forwalk02RL"
        elif act_name != "forwardSlow0403" and (acted_name == "Forwalk02LR" or acted_name == "Forwalk02R"):
            print(act_name,"动作未执行 执行 Stand")
            acted_name = "Forwalk02RS"
        elif act_name != "forwardSlow0403" and (acted_name == "Forwalk02RL" or acted_name == "Forwalk02L"):
            print(act_name,"动作未执行 执行 Stand")
            acted_name = "Forwalk02LS"
        elif act_name == "forwardSlow0403":
            acted_name = "Forwalk02R"
        else:
            acted_name = act_name

        CMDcontrol.actionComplete = False
        if len(CMDcontrol.action_list) > 0 :
            print("队列超过一个动作")
            CMDcontrol.action_list.append(acted_name)
        else:
            CMDcontrol.action_list.append(acted_name)
        CMDcontrol.action_wait()

    else:
        print("-----------------------执行动作名：",act_name)
        time.sleep(2)

####################################################主程序###################################################
if __name__ == '__main__':
    
    i = 0
    while True:
        if chest_ret == True and HeadOrg_img is not None:
            chest = ChestOrg_img.copy()
            chest = np.rot90(chest)
            head = HeadOrg_img.copy()
            cv2.imshow('current_chest', chest) # 显示实时图像，标题为'current_image_gray'
            cv2.imshow('head', head)
            #cv2.imwrite('./image/chest_stair_'+str(i)+'.jpg',chest)
            cv2.imwrite('./picture/4/head_4_'+str(i)+'.jpg', head)
            i = i+1
            print(i)
            cv2.waitKey(5)
            #action_append('forwardSlow0403')
            #if cv2.waitKey(25) & 0xFF == ord('b'):
            #    action_append('stand')
            #if cv2.waitKey(25) & 0xFF == ord('s'): 
            #   cv2.imwrite(str(i) + '.jpg', ChestOrg_img)
            #   i = i + 1
            #if cv2.waitKey(25) & 0xFF == ord('q'): 
            #   break
        else :
             print('failed')
        
    cap_chest.release()
    cap_head.release()
    cv2.destroyAllWindows()
    print('end')
            
        