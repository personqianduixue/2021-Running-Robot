#!/usr/bin/env python3
# coding:utf-8

from itertools import filterfalse
import cv2
import math
import numpy as np
import threading
import time
import datetime
import CMDcontrol 

action_DEBUG = False

stream_head = "http://192.168.137.5:8082/?action=stream?dummy=param.mjpg"
stream_chest = "http://192.168.137.5:8080/?action=stream?dummy=param.mjpg"
cap_chest = cv2.VideoCapture(stream_chest)
cap_head = cv2.VideoCapture(stream_head)  #扑捉到的视频流

'''cap_head = cv2.VideoCapture(2)
cap_chest = cv2.VideoCapture(0)  #扑捉到的视频流'''

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

###################################################关卡：过门#################################################
def getAreaMaxContour_door0(contours):
    i = 0 # 一个特别不聪明的办法的标志位
    r_w = 640
    r_h = 480
    area_max_contour = None
    contour_area_max = 0
    top_all_right = contours[0][0][0]
    top_all_left = contours[0][0][0]
    bottom_all_right = contours[0][0][0]
    bottom_all_left = contours[0][0][0]
    
    # 把每个轮廓最外面四个点找出来，得到宽和高，然后从面积判是不是最大 
    for con in contours:  # 历遍所有轮廓
        top_right = con[0][0]
        top_left = con[0][0]
        bottom_right = con[0][0]
        bottom_left = con[0][0]
        contour_area_temp = 0
        
        for c in con:
            if c[0][0] + c[0][1] < top_left[0] + top_left[1]:
                top_left = c[0]
            if (r_w - c[0][0]) + c[0][1] < (r_w - top_right[0]) + top_right[1]:
                top_right = c[0]
            if c[0][0] + (r_h - c[0][1]) < bottom_left[0] + (r_h - bottom_left[1]):
                bottom_left = c[0]
            if c[0][0] + c[0][1] > bottom_right[0] + bottom_right[1]:
                bottom_right = c[0]

        if bottom_right[0] - bottom_left[0] >= top_right[0] - top_left[0]:
            width = bottom_right[0] - bottom_left[0]
        else:
            width = top_right[0] - top_left[0]

        if bottom_left[1] - top_left[1] >= bottom_right[1] - top_right[1]:
            height = bottom_left[1] - top_left[1]
        else:
            height = bottom_right[1] - top_right[1]

        contour_area_temp = height * width
        #print(math.fabs(contour_area_temp))

        if contour_area_temp > 9000:  #只有在面积大于25时，轮廓才是有效的，以过滤干扰
            if i == 0:
                top_all_left = top_left
                top_all_right = top_right
                bottom_all_left = bottom_left
                bottom_all_right = bottom_right
                i = 1
            if contour_area_temp > contour_area_max:
                contour_area_max = contour_area_temp
                area_max_contour = con
            if top_left[0] + top_left[1] < top_all_left[0] + top_all_left[1]:
                top_all_left = top_left
            if (r_w - top_right[0]) + top_right[1] < (r_w - top_all_right[0]) + top_all_right[1]:
                top_all_right = top_right
            if bottom_left[0] + (r_h - bottom_left[1]) < bottom_all_left[0] + (r_h - bottom_all_left[1]):
                bottom_all_left = bottom_left
            if bottom_right[0] + bottom_right[1] > bottom_all_right[0] + bottom_all_right[1]:
                bottom_all_right = bottom_right
    
    box_rect_max = [top_all_left,top_all_right,bottom_all_right,bottom_all_left]

    return contour_area_max, area_max_contour, box_rect_max  # 返回最大的轮廓 

def getAreaMaxContour_door1(contours):
    r_w = 640
    r_h = 480
    contour_area_temp = 0
    contour_area_max = 0
    area_max_contour = None
    box_rect_max = None

    for con in contours:  # 历遍所有轮廓
        contour_area_temp = math.fabs(cv2.contourArea(con))  # 计算轮廓面积
        # print(math.fabs(cv2.contourArea(con)))
        if contour_area_temp > 1000:
            if contour_area_temp >= contour_area_max:
                contour_area_max = contour_area_temp
                area_max_contour = con

    if  area_max_contour.all() == None:
        return contour_area_max, area_max_contour, box_rect_max
    
    top_right = area_max_contour[0][0] 
    top_left = area_max_contour[0][0] 
    bottom_right = area_max_contour[0][0] 
    bottom_left = area_max_contour[0][0]

    for c in area_max_contour:
        if c[0][0] + c[0][1] < top_left[0] + top_left[1]:
            top_left = c[0]
        if (r_w - c[0][0]) + c[0][1] < (r_w - top_right[0]) + top_right[1]:
            top_right = c[0]
        if c[0][0] + (r_h - c[0][1]) < bottom_left[0] + (r_h - bottom_left[1]):
            bottom_left = c[0]
        if c[0][0] + c[0][1] > bottom_right[0] + bottom_right[1]:
            bottom_right = c[0]
    
    box_rect_max = [top_left,top_right,bottom_right,bottom_left]

    return contour_area_max, area_max_contour, box_rect_max   # 返回最大的轮廓

def pass_door():
    global HeadOrg_img,ChestOrg_img
    step_door_flag = 0 # 进入第几阶段（0：正面朝门；1：转身；2：过门）
    j = 0 # 头部拍照标志
    i = 0 # 胸部拍照标志
    step_turn_times = 0 # 过门的调整标志位
    Head_top_center_y_last = 480
    door_Debug = False
    
    while True:

        # 前两步用头部摄像头
        if step_door_flag == 0 or step_door_flag == 1:
            
            if HeadOrg_img is None:
                continue
        
            # 图像处理
            HeadOrg_img = HeadOrg_img.copy()
            HeadOrg_img_draw = HeadOrg_img.copy()
            HeadOrg_img_gauss = cv2.GaussianBlur(HeadOrg_img, (3, 3), 0)  # 高斯模糊
            HeadOrg_img_hsv = cv2.cvtColor(HeadOrg_img_gauss, cv2.COLOR_BGR2HSV)  # 将图片转换到HSV空间
            #HeadOrg_img_blue = cv2.inRange(HeadOrg_img_hsv, np.array([90, 80, 46]),np.array([124, 255, 255])) #yuanseyue
            HeadOrg_img_blue = cv2.inRange(HeadOrg_img_hsv, np.array([75, 40, 46]),np.array([130, 255, 255]))  # 对原图像进行掩模运算（这个时候蓝的部分是白的，其他部分是黑的）
            HeadOrg_img_opened = cv2.morphologyEx(HeadOrg_img_blue, cv2.MORPH_OPEN, np.ones((8, 8), np.uint8))  # 开运算 去噪点
            HeadOrg_img_closed = cv2.morphologyEx(HeadOrg_img_opened, cv2.MORPH_CLOSE, np.ones((8, 8), np.uint8))  # 闭运算 封闭连接

            # 找轮廓及4个顶点
            (contours, hierarchy) = cv2.findContours(HeadOrg_img_closed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            if Head_top_center_y_last > 10:
                max_area, max_contour, max_box= getAreaMaxContour_door1(contours)
                if  max_contour.all() == 0:
                    print("未识别到轮廓")
                    door_Debug = True
            if Head_top_center_y_last <= 10:
                if contours == None :
                    print("未识别到轮廓")
                    door_Debug = True
                max_area, max_contour, max_box= getAreaMaxContour_door0(contours)

            if door_Debug == False:

                Head_top_center_x = int((max_box[1][0] + max_box[0][0]) / 2)
                Head_top_center_y = int((max_box[1][1] + max_box[0][1]) / 2)
                Head_bottom_center_x = int((max_box[2][0] + max_box[3][0]) / 2)
                Head_bottom_center_y = int((max_box[2][1] + max_box[3][1]) / 2)
                Head_top_bottom = math.fabs(Head_top_center_x - Head_bottom_center_x)
                Head_bottom_angle = - math.atan((max_box[2][1] - max_box[3][1]) / (max_box[2][0] - max_box[3][0])) * 180.0 / math.pi
                Head_top_angle = - math.atan((max_box[1][1] - max_box[0][1]) / (max_box[1][0] - max_box[0][0])) * 180.0 / math.pi
                Head_top_long = max_box[1][0] - max_box[0][0]
                Head_bottom_long = max_box[2][0] - max_box[3][0]

                if Head_top_center_y <= 10 and Head_top_center_y_last > 10:
                    Head_top_center_y_last = Head_top_center_y
                    print("Head_top_center_y:" + str(Head_top_center_y))
                    continue
                if Head_top_center_y > 10 and Head_top_center_y_last <= 10 :
                    Head_top_center_y_last = Head_top_center_y
                    print("Head_top_center_y:" + str(Head_top_center_y))
                    continue
                Head_top_center_y_last = Head_top_center_y
                    
                #画轮廓
                cv2.drawContours(HeadOrg_img_draw, np.array([max_box]), 0, (0, 255, 255), 2)  
                cv2.circle(HeadOrg_img_draw, (max_box[1][0], max_box[1][1]), 3, [0, 255, 255], 2)
                cv2.circle(HeadOrg_img_draw, (max_box[0][0], max_box[0][1]), 3, [0, 255, 255], 2)
                cv2.circle(HeadOrg_img_draw, (max_box[2][0], max_box[2][1]), 3, [0, 255, 255], 2)
                cv2.circle(HeadOrg_img_draw, (max_box[3][0], max_box[3][1]), 3, [0, 255, 255], 2) 
                cv2.circle(HeadOrg_img_draw, (Head_top_center_x, Head_top_center_y), 3, [0, 0, 255], 2)
                cv2.circle(HeadOrg_img_draw, (Head_bottom_center_x, Head_bottom_center_y), 3, [0, 0, 255], 2)

                cv2.putText(HeadOrg_img_draw, "top_bottom:" + str(int(Head_top_bottom)), (30, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 255), 2)  
                cv2.putText(HeadOrg_img_draw, "bottom_angle:" + str(int(Head_bottom_angle)), (30, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 255), 2) 
                cv2.putText(HeadOrg_img_draw, "top_angle:" + str(int(Head_top_angle)), (30, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 255), 2) 
                cv2.putText(HeadOrg_img_draw, "top_center_y:" + str(int(Head_top_center_y)), (30, 230), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 255), 2)
                cv2.putText(HeadOrg_img_draw, "top_center_x:" + str(int(Head_top_center_x)), (30, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 255), 2)
                cv2.putText(HeadOrg_img_draw, "bottom_center_y:" + str(int(Head_bottom_center_y)), (30, 290), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 255), 2)
                cv2.putText(HeadOrg_img_draw, "bottom_center_x:" + str(int(Head_bottom_center_x)), (30, 320), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 255), 2)
                cv2.putText(HeadOrg_img_draw, "max_area:" + str(int(max_area)), (30, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 255), 2)
                cv2.putText(HeadOrg_img_draw, "top_long:" + str(int(Head_top_long)), (30, 380), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 255), 2)
                cv2.putText(HeadOrg_img_draw, "bottome_long:" + str(int(Head_bottom_long)), (30, 410), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 255), 2)
                    
                cv2.imshow('blue_image', HeadOrg_img_blue)
                cv2.imshow('closed_image', HeadOrg_img_closed)
                cv2.imshow('current_image', HeadOrg_img_draw)
                HeadOrg_img_forshow0 = np.vstack((HeadOrg_img, HeadOrg_img_draw))
                HeadOrg_img_forshow1 = np.vstack((HeadOrg_img_blue, HeadOrg_img_closed))
                cv2.waitKey(5)
            
                #cv2.imwrite('door_'+str(j)+'.jpg', HeadOrg_img)
                cv2.imwrite('door_'+str(j)+'.jpg', HeadOrg_img_forshow0)
                cv2.imwrite('door_close_'+str(j)+'.jpg', HeadOrg_img_forshow1)
                j = j + 1

        # 后一步用胸部摄像头    
        '''if step_door_flag == 2:

            if ChestOrg_img is None:
                continue

            ChestOrg_img = ChestOrg_img.copy()
            ChestOrg_img_90 = np.rot90(ChestOrg_img)
            ChestOrg_img_door = ChestOrg_img_90[160:,:,:]
            ChestOrg_img_draw = ChestOrg_img_door.copy()

            ChestOrg_img_gauss = cv2.GaussianBlur(ChestOrg_img_door, (5, 5), 0)  # 高斯模糊
            ChestOrg_img_hsv = cv2.cvtColor(ChestOrg_img_gauss, cv2.COLOR_BGR2HSV)  # 将图片转换到HSV空间
            ChestOrg_img_blue = cv2.inRange(ChestOrg_img_hsv, np.array([90, 80, 46]),np.array([124, 255, 255]))  # 对原图像进行掩模运算（这个时候蓝的部分是白的，其他部分是黑的）
            ChestOrg_img_opened = cv2.morphologyEx(ChestOrg_img_blue, cv2.MORPH_OPEN, np.ones((15, 15), np.uint8))  # 开运算 去噪点
            ChestOrg_img_closed = cv2.morphologyEx(ChestOrg_img_opened, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))  # 闭运算 封闭连接
            
            (contours, hierarchy) = cv2.findContours(ChestOrg_img_closed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            max_area, max_contour, max_box= getAreaMaxContour_door1(contours)
            if  max_area == 0:
                print("未识别到轮廓")
                door_Debug = True

            if door_Debug == False:

                Chest_left_center_x = int((max_box[0][0] + max_box[3][0]) / 2)
                Chest_right_center_x = int((max_box[1][0] + max_box[2][0]) / 2)

                cv2.drawContours(ChestOrg_img_draw, np.array([max_box]), 0, (0, 255, 255), 2)  
                cv2.circle(ChestOrg_img_draw, (max_box[1][0], max_box[1][1]), 3, [0, 255, 255], 2)
                cv2.circle(ChestOrg_img_draw, (max_box[0][0], max_box[0][1]), 3, [0, 255, 255], 2)
                cv2.circle(ChestOrg_img_draw, (max_box[2][0], max_box[2][1]), 3, [0, 255, 255], 2)
                cv2.circle(ChestOrg_img_draw, (max_box[3][0], max_box[3][1]), 3, [0, 255, 255], 2) 

                cv2.putText(ChestOrg_img_draw, "Chest_left_center_x:" + str(int(Chest_left_center_x)), (30, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 255), 2)  
                cv2.putText(ChestOrg_img_draw, "Chest_right_center_x:" + str(int(Chest_right_center_x)), (30, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 255), 2) 

                cv2.imshow('Chest_img', ChestOrg_img_draw)
                cv2.imwrite('door_'+'Chest_'+str(i)+'.jpg', ChestOrg_img_draw)
                i = i + 1'''

        #转身前调整   
        if step_door_flag == 0:

            if Head_bottom_center_y < 470:

                '''if door_Debug == True:
                    print("找不到轮廓00")
                    action_append("turn003L")'''

                if max_box[0][0] < 30 :
                    action_append("turn004L")
                    print(str(j - 1) + "tooL00")
                    continue
                if max_box[1][0] > 450 :
                    action_append("turn004R")
                    print(str(j - 1) + "tooR00")
                    continue
                
                if math.fabs(Head_bottom_angle) <= 5:
                    print(str(j - 1) + "角度可了00")
                    action_append("Forwalk02")
                elif  max_box[3][1] > max_box[2][1]:
                    print(str(j - 1) + "左转一点点00")
                    action_append("turn001L")
                else:
                    print(str(j - 1) + "右转一点点00")
                    action_append("turn001R")
                    
            if Head_bottom_center_y >= 470:
                
                if door_Debug == True:
                    action_append("Back2Run")
                    print("找不到轮廓01")
                
                if Head_top_center_y < 70 and Head_top_long < 160:
                    print(str(j - 1) + "too01")
                    action_append("Back2Run")
                    continue
                
                if Head_top_center_y > 10:
                    
                    if math.fabs(Head_top_angle) <= 5:
                        print(str(j - 1) + "角度可了01")
                    elif  max_box[0][1] < max_box[1][1]:
                        print(str(j - 1) + "左转一点点01")
                        action_append("turn001L")
                        continue
                    else:
                        print(str(j - 1) + "右转一点点01")
                        action_append("turn001R")
                        continue
                        
                    if math.fabs(Head_bottom_center_x - 320) < 15:
                        print(str(j - 1) + "左右可了01")
                        action_append("Forwalk01")
                    elif Head_bottom_center_x > 350:
                        print(str(j - 1) + "往右一点点01")
                        action_append("Right3move")
                        time.sleep(1)
                    else:
                        print(str(j - 1) + "往左一点点01")
                        action_append("Left3move")
                        time.sleep(1)
                    
                if Head_top_center_y <= 10:
                    if math.fabs(Head_top_angle) >= 5:
                        action_append("Back2Run")
                        print(str(j - 1) + "too02_angle")
                        continue
                    if math.fabs(Head_top_center_x - 320) > 20:
                        action_append("Back2Run")
                        print(str(j - 1) + "too02_x")
                        continue
                    else:
                        '''print(str(j - 1) + "转身")
                        action_append("turn010R")
                        action_append("turn010R")
                        action_append("HeadTurn185")
                        action_append("Back2Run")'''
                        step_door_flag = 2
                        time.sleep(0.2)
                        cv2.destroyAllWindows()
                        continue

        #转身后及其调整                                    
        '''if step_door_flag == 1:
        
            if math.fabs(Head_top_angle) <=5:
                print(str(j - 1) + "角度可了10")
            elif  Head_top_angle > 0:
                print(str(j - 1) + "右转一点点10")
                action_append("turn001R")
                continue
            else:
                print(str(j - 1) + "左转一点点10")
                action_append("turn001L")
                continue

            if math.fabs(Head_top_center_x - 350) < 20:
                print(str(j - 1) + "前后可了10")
                action_append("Back2Run")
                step_door_flag = 2
                continue
            elif Head_top_center_x < 350:
                print(str(j - 1) + "往后一点点10")
                action_append("Back0Run")
            else:
                print(str(j - 1) + "往前一点点10")
                action_append("Forwalk00")'''       

        # 开胸部摄像头判断前后位置
        # 侧走版本    
        '''if step_door_flag == 2:

            if door_Debug == True:
                if i >= 2 :
                    print("找不到轮廓2")
                    print("盲走结束")
                    action_append("turn010L")
                    action_append("turn010L")
                    action_append("HeadTurnMM")
                    cv2.destroyAllWindows()
                    break

            if Chest_left_center_x <370 :

                print(str(i - 1) +'_' + str(step_turn_times) + "左移" + str(Chest_left_center_x))
                action_append("Left3move")
                time.sleep(1)

                if step_turn_times <= 2 :
                    step_turn_times = step_turn_times + 1
                
                else:
                    print("过门调整")
                    action_append("Back2Run")
                    action_append("turn001L")
                    action_append("turn001L")
                    action_append("turn001L")
                    step_turn_times = 0
                    
                continue

            else:
                print("盲走结束")
                action_append("turn010L")
                action_append("turn010L")
                action_append("HeadTurnMM")
                cv2.destroyAllWindows()
                break'''

        #直走版本
        if step_door_flag ==2:
            print("盲走")
            '''action_append("fastForward01")
            time.sleep(0.5)
            action_append("fastForward01")
            time.sleep(0.5)
            action_append("fastForward01")
            time.sleep(0.5)'''
            action_append("forwardSlow0403")
            action_append("forwardSlow0403")
            action_append("forwardSlow0403")
            action_append("forwardSlow0403")
            action_append("forwardSlow0403")
            action_append("forwardSlow0403")
            action_append("forwardSlow0403")
            action_append("forwardSlow0403")
            action_append("forwardSlow0403")
            action_append("forwardSlow0403")
            action_append("Stand")
            break
          
####################################################主程序##################################################
if __name__ == '__main__':
    while len(CMDcontrol.action_list) > 0 : 
        print("等待启动")
    action_append("HeadTurnMM") 

    while True: 
            
            #action_append("RollRail")
            action_append("Back1Run")
            action_append("Back1Run")
            action_append("Back1Run")
            action_append("Back1Run")
            time.sleep(0.5)
            action_append("turn010L")

            pass_door()

            while(1):
                print("结束")
                time.sleep(10000)