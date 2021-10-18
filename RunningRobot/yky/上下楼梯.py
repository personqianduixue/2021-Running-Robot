#!/usr/bin/env python3
# coding:utf-8

import cv2
import math
import numpy as np
import threading
import time
import datetime
import CMDcontrol 

action_DEBUG = False

'''stream_head = "http://192.168.137.3:8082/?action=stream?dummy=param.mjpg"
stream_chest = "http://192.168.137.3:8080/?action=stream?dummy=param.mjpg"
cap_chest = cv2.VideoCapture(stream_chest)
cap_head = cv2.VideoCapture(stream_head)  #扑捉到的视频流'''

cap_head = cv2.VideoCapture(2)
cap_chest = cv2.VideoCapture(0)  #扑捉到的视频流

chest_ret = False     # 读取胸部图像标志位
head_ret = False      # 读取头部图像标志位  
ChestOrg_img = None   # 胸部图像当前帧      
HeadOrg_img = None    # 头部图像当前帧 

################################################读取图像线程#################################################
# 接收视频流，转化为一帧帧图像；未成功接收报错
def get_img():
    global cap_chest,cap_head
    global ChestOrg_img,HeadOrg_img,chest_ret,head_ret
    while True:
        if cap_chest.isOpened() and cap_head.isOpened():      #摄像头初始化成功？
            chest_ret, ChestOrg_img = cap_chest.read()
            ChestOrg_img = np.rot90(ChestOrg_img)
            head_ret, HeadOrg_img = cap_head.read()    #读取该帧图像，及是否成功的标志位
            if (chest_ret == False) or (head_ret == False):
                print("fail ------------------")
            if ChestOrg_img is None:
                print("ChestOrg_img error") 
            if HeadOrg_img is None:
                print("HeadOrg_img error")          # 接收有问题就报错
                
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

###################################################找最大轮廓###################################################
def getAreaMaxContour_stair(contours):
    r_w = 480
    r_h = 480
    contour_area_temp = 0
    contour_area_max = 0
    area_max_contour = None
    box_rect_max = None

    for con in contours:  # 历遍所有轮廓
        contour_area_temp = math.fabs(cv2.contourArea(con))  # 计算轮廓面积
        # print(math.fabs(cv2.contourArea(con)))
        if contour_area_temp > 25:
            if contour_area_temp >= contour_area_max:
                contour_area_max = contour_area_temp
                area_max_contour = con

    if contour_area_max == 0:
        return contour_area_max, area_max_contour, box_rect_max
    
    top_right = area_max_contour[0][0] 
    top_left = area_max_contour[0][0] 
    bottom_right = area_max_contour[0][0] 
    bottom_left = area_max_contour[0][0]

    for c in area_max_contour:
        if c[0][0] + 1.5*c[0][1] < top_left[0] + 1.5*top_left[1]:
            top_left = c[0]
        if (r_w - c[0][0]) + 1.5*c[0][1] < (r_w - top_right[0]) + 1.5*top_right[1]:
            top_right = c[0]
        if c[0][0] + 0.5 *(r_h - c[0][1]) < bottom_left[0] + 0.5 *(r_h - bottom_left[1]):
            bottom_left = c[0]
        if c[0][0] + 0.5 *c[0][1] > bottom_right[0] + 0.5 *bottom_right[1]:
            bottom_right = c[0]
    
    box_rect_max = [top_left,top_right,bottom_right,bottom_left]

    return contour_area_max, area_max_contour, box_rect_max   # 返回最大的轮廓廓

###################################################关卡：楼梯#################################################
def stair():

    global state,state_sel,ChestOrg_img
    step_color = 1 # 0：识别蓝色；1：识别绿色；2：识别红色
    step_stair_flag = 1 # 进入第几阶段
    j = 0

    while True:

        if ChestOrg_img is None:
            continue

        ChestOrg_90 = ChestOrg_img[160:,:,:]
        ChestOrg_copy = ChestOrg_90.copy()
        ChestOrg_draw = ChestOrg_90.copy()
        Chest_gauss = cv2.GaussianBlur(ChestOrg_copy,(3,3),0)
        Chest_hsv = cv2.cvtColor(Chest_gauss,cv2.COLOR_BGR2HSV)
        
        #图像处理 蓝色，绿色，红色
        if step_color == 0:
            Chest_blue = cv2.inRange(Chest_hsv,(100,80,46),(124,255,255))
            Chest_opened = cv2.morphologyEx(Chest_blue, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))  # 开运算 去噪点
        if step_color == 1 :
            Chest_green = cv2.inRange(Chest_hsv,(50,75,70),(84, 255, 210))
            Chest_opened = cv2.morphologyEx(Chest_green, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))  # 开运算 去噪点
        if step_color == 2 :
            Chest_red1 = cv2.inRange(Chest_hsv,(0,43,46),(1,255,255))
            Chest_red2 = cv2.inRange(Chest_hsv,(165,43,46),(180,255,255))
            Chest_red = cv2.bitwise_or(Chest_red1, Chest_red2)
            Chest_opened = cv2.morphologyEx(Chest_red, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))  # 开运算 去噪点
        Chest_closed = cv2.morphologyEx(Chest_opened, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))  # 闭运算 封闭连接
        (contours, hierarchy) = cv2.findContours(Chest_closed, cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)  # 找出轮廓cv2.CHAIN_APPROX_NONE
        
        max_area, max_contour, max_box= getAreaMaxContour_stair(contours)
        if max_area == 0:
            print("未识别到轮廓,站立等待")
            action_append("Stand")
            continue

        top_left = max_box[0]
        top_right = max_box[1]
        bottom_right = max_box[2]
        bottom_left = max_box[3]
            
        #计算参数
        Chest_top_center_x = int((top_right[0] + top_left[0]) / 2)
        Chest_top_center_y = int((top_right[1] + top_left[1]) / 2)
        Chest_bottom_center_x = int((bottom_right[0] + bottom_left[0]) / 2)
        Chest_bottom_center_y = int((bottom_right[1] + bottom_left[1]) / 2)
        Chest_top_bottom = math.fabs(Chest_top_center_x - Chest_bottom_center_x)
        Chest_bottom_angle = - math.atan((bottom_right[1] - bottom_left[1]) / (bottom_right[0] - bottom_left[0])) * 180.0 / math.pi
        Chest_top_angle = - math.atan((top_right[1] - top_left[1]) / (top_right[0] - top_left[0])) * 180.0 / math.pi
            
        #画图
        cv2.drawContours(ChestOrg_draw, np.array([max_box]), 0, (0, 255, 255), 2)  
        cv2.circle(ChestOrg_draw, (top_right[0], top_right[1]), 3, [0, 0, 255], 2)
        cv2.circle(ChestOrg_draw, (top_left[0], top_left[1]), 3, [0, 0, 255], 2)
        cv2.circle(ChestOrg_draw, (bottom_right[0], bottom_right[1]), 3, [0, 0, 255], 2)
        cv2.circle(ChestOrg_draw, (bottom_left[0], bottom_left[1]), 3, [0, 0, 255], 2) 
        cv2.circle(ChestOrg_draw, (Chest_top_center_x, Chest_top_center_y), 3, [0, 255, 255], 2)
        cv2.circle(ChestOrg_draw, (Chest_bottom_center_x, Chest_bottom_center_y), 3, [0, 255, 255], 2)

        cv2.putText(ChestOrg_draw, "Chest_top_angle:" + str(int(Chest_top_angle)), (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255, 255, 255), 2)
        cv2.putText(ChestOrg_draw, "Chest_top_center_x:" + str(int(Chest_top_center_x)), (30, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 255), 2)    
        cv2.putText(ChestOrg_draw,"Chest_bottom_angle:" + str(int(Chest_bottom_angle)), (30, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255, 255, 255), 2)
        cv2.putText(ChestOrg_draw,"Chest_bottom_center_x:" + str(int(Chest_bottom_center_x)), (30, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255, 255, 255), 2)
        cv2.putText(ChestOrg_draw, "Chest_bottom_center_y:" + str(int(Chest_bottom_center_y)), (30, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255, 255, 255), 2)  
            
        cv2.imshow('current_image', ChestOrg_draw)
        cv2.imshow('image_colsed', Chest_closed)
        cv2.waitKey(5)

        ChestOrg_img_forshow0 = np.vstack((ChestOrg_90, ChestOrg_draw))
        cv2.imwrite('stair_'+str(j)+'.jpg', ChestOrg_90)
        cv2.imwrite('stair_'+str(j)+'_0.jpg', ChestOrg_img_forshow0)
        cv2.imwrite('stair_'+str(j)+'_1.jpg', Chest_closed)
        j = j + 1

        #上楼梯
        if  step_stair_flag == 0:
    
            if Chest_bottom_center_y < 150:
                if Chest_bottom_angle > 3:
                    action_append('turn001L')
                    print('左转')
                if Chest_bottom_angle < -3:
                    action_append('turn001R')
                    print('右转')
                if math.fabs(Chest_bottom_angle) <3:
                    action_append('fastForward01')
                    action_append("Stand")
                    print('go1')                   
                
            if Chest_bottom_center_y >= 150 and Chest_bottom_center_y < 340:
                
                if max_box[0][0] > 240 :
                    action_append("Left02move")
                    print("too")
                    continue
                if max_box[1][0] < 240 :
                    action_append("Right02move")
                    print("too")
                    continue
                
                if Chest_bottom_angle > 5:
                    action_append('turn001L')
                    print('左转')
                    continue
                if Chest_bottom_angle < -5:
                    action_append('turn001R')
                    print('右转')
                    continue
                
                if Chest_bottom_center_x >= 240:
                    action_append("Right02move")
                    print('右移') 
                if Chest_bottom_center_x <= 220:
                    action_append("Left02move")
                    print('左移') 
                else:
                    action_append('Forwalk01')
                    print('go2') 

            if Chest_bottom_center_y >= 340:
                if Chest_bottom_angle > 3:
                    action_append('turn001L')
                    print('左转')
                if Chest_bottom_angle< -3:
                    action_append('turn001R')
                    print('右转')
                if Chest_bottom_angle >= -3 and Chest_bottom_angle <= 3:
                    print('准备好了，上台阶')
                    time.sleep(1)
                    action_append("UpBridge")
                    action_append("Stand")
                    action_append("Forwalk00")
                    time.sleep(1)
                    action_append("UpBridge")
                    action_append("Stand")
                    action_append("Forwalk00")
                    time.sleep(1)
                    action_append("UpBridge")
                    action_append("Stand")
                    time.sleep(1)
                    print('到顶了，进入调整部分')
                    step_stair_flag = 1
                    step_color = 1
                    continue
        
        # 在最上面的调整，以及下楼梯部分
        if  step_stair_flag == 1:
            
            '''if Chest_top_center_x >= 170:
                action_append("Back1Run")
                print("太前了")
                continue'''
            
            if math.fabs(Chest_top_angle) < 3 :
                print("角度可了1")
                step_stair_flag = 2
            if Chest_top_angle > 0:
                print("左转")
                action_append("turn000L")
            if Chest_top_angle < 0:
                print("右转")
                action_append("turn000R")

        if step_stair_flag == 2:
            
            '''if Chest_top_center_x >= 170:
                action_append("Back1Run")
                print("太前了")
                continue'''

            if math.fabs(Chest_top_angle) > 5 :
                step_stair_flag = 1
            else:
                if math.fabs(Chest_top_center_x - 240) < 20:
                    print("左右可了")
                    action_append("Back1Run")
                    time.sleep(0.2)
                    action_append("DownBridge")
                    time.sleep(0.2)
                    action_append("DownBridge")
                    print('进入下坡部分')
                    step_stair_flag = 3
                    step_color = 2
                    continue
                elif Chest_top_center_x > 240:
                    print("往右一点点")
                    action_append("Stand")
                    action_append("Right02move")
                else:
                    print("往左一点点")
                    action_append("Stand")
                    action_append("Left02move")         #左右调整
        
        #坡道部分
        if step_stair_flag == 3:
            if math.fabs(Chest_top_angle) < 3 :
                print("角度可了3")
                step_stair_flag = 4
            if Chest_top_angle > 0:
                print("左转")
                action_append("turn001L")
            if Chest_top_angle < 0:
                print("右转")
                action_append("turn001R")         

        if step_stair_flag == 4:
            if math.fabs(Chest_top_angle) > 5 :
                step_stair_flag = 3
            else:
                if math.fabs(Chest_top_center_x - 240) < 20:
                    print("左右可了")
                    action_append("XiaPou")
                    time.sleep(1.5)
                    action_append("XiaPou")
                    time.sleep(1.5)
                    action_append("XiaPou")
                    time.sleep(1.5)
                    '''action_append("forwardSlow0403")
                    time.sleep(1.5)
                    action_append("forwardSlow0403")
                    time.sleep(1.5)
                    action_append("forwardSlow0403")
                    time.sleep(1.5)
                    action_append("forwardSlow0403")
                    time.sleep(1.5)
                    action_append("forwardSlow0403")
                    time.sleep(1.5)
                    action_append("forwardSlow0403")
                    time.sleep(1.5)'''
                    break
                elif Chest_top_center_x > 240:
                    print("往右一点点")
                    action_append("Right02move")
                else:
                    print("往左一点点")
                    action_append("Left02move")         #左右调整
        

####################################################主程序##################################################
if __name__ == '__main__':
    while len(CMDcontrol.action_list) > 0 : # 等待执行完前面的动作再开始主程序
        print("等待启动")
        time.sleep(1)
    action_append("HeadTurnMM") # 头回正？准备动作？

    while True: # 一直循环这个主程序
            
            stair()

            while(1):
                print("结束")
                time.sleep(10000)