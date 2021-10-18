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

cap_head = cv2.VideoCapture(2)
cap_chest = cv2.VideoCapture(0)  #扑捉到的视频流

chest_ret = False     # 读取胸部图像标志位
head_ret = False      # 读取头部图像标志位  
ChestOrg_img = None   # 胸部图像当前帧      
HeadOrg_img = None    # 头部图像当前帧 

chest_r_width = 480
chest_r_height = 640
head_r_width = 640
head_r_height = 480 #窗口大小

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

###################################################颜色字典###################################################
color_range = {
               'yellow_door': [(20, 140, 60), (40, 240, 150)],
               'yellow_door_beifen': [(0, 140, 60), (40, 240, 150)],
               'black_door': [(0, 0, 0), (80, 255, 5)],
               'black_gap': [(0, 0, 0), (180, 255, 70)],
               'yellow_door_light': [(30, 200, 30), (40, 255, 150)],
               'yellow_hole': [(20, 120, 95), (30, 250, 190)],
               'black_hole': [(5, 80, 20), (40, 255, 100)],
               'chest_red_floor': [(0, 40, 60), (20,200, 190)],
               'chest_red_floor1': [(0, 100, 60), (20,200, 210)],
               'chest_red_floor2': [(110, 100, 60), (180,200, 210)],
                'green_bridge': [(50, 75, 70), (80, 240, 255)],
                'white_hole':[(0,0,221),(180,30,255)],
                'blue_bridge':[(100,80,46),(124,255,255)],
                'blue_stair':[(100,80,46),(124,255,255)],
                'green_stair':[(50, 75, 70),(80, 240, 210)],
                'red_stair':[(0, 160, 100),(180, 255, 250)]
               }

color_dist = {'red': {'Lower': np.array([0, 160, 100]), 'Upper': np.array([180, 255, 250])},
              'black_dir': {'Lower': np.array([0, 0, 10]), 'Upper': np.array([170, 170, 45])},
              'black_line': {'Lower': np.array([0, 0, 20]), 'Upper': np.array([100, 160, 80])},
              'blue': {'Lower': np.array([100, 80, 46]), 'Upper': np.array([124, 255, 255])},   # 过门，门的颜色
              'ball_red': {'Lower': np.array([160, 100, 70]), 'Upper': np.array([190, 215, 145])},
              'blue_hole': {'Lower': np.array([100, 130, 80]), 'Upper': np.array([130, 255, 150])},
              }

###################################################找最大轮廓###################################################
def getAreaMaxContour_great_stair(contours):
    box_rect_max = []
    contour_area_temp = 0
    contour_area_max = 0
    r_w = 480
    r_h = 640
    area_max_contour = None
    
    for con in contours:  # 历遍所有轮廓
        top_right = con[0][0]
        top_left = con[0][0]
        bottom_right = con[0][0]
        bottom_left = con[0][0]
        for c in con:
            if c[0][0] + 1.5 * c[0][1] < top_left[0] + 1.5 * top_left[1]:
                top_left = c[0]
            if (r_w - c[0][0]) + 1.5 * c[0][1] < (r_w - top_right[0]) + 1.5 * top_right[1]:
                top_right = c[0]
            if c[0][0] + 1.5 * (r_h - c[0][1]) < bottom_left[0] + 1.5 * (r_h - bottom_left[1]):
                bottom_left = c[0]
            if c[0][0] + 1.5 * c[0][1] > bottom_right[0] + 1.5 * bottom_right[1]:
                bottom_right = c[0]
        if bottom_right[0] - bottom_left[0] >= top_right[0] - top_left[0]:
            width = bottom_right[0] - bottom_left[0]
        else:
            width = top_right[0] - top_left[0]
        if bottom_left[1] - top_left[1] >= bottom_right[1] - top_right[1]:
            height = bottom_left[1] - top_left[1]
        else:
            height = bottom_right[1] - top_right[1]
        bottom_center_y = (bottom_right[1] + bottom_left[1]) / 2
        if bottom_center_y > 210 and bottom_center_y < 640 :
            contour_area_temp = height * width
            if contour_area_temp > contour_area_max:
                contour_area_max = contour_area_temp
                if contour_area_temp > 25:  #只有在面积大于45时，最大面积的轮廓才是有效的，以过滤干扰
                    area_max_contour = con
                    box_rect_max = [top_left,top_right,bottom_right,bottom_left]
    
    #print(contour_area_max)
    #print((box_rect_max[4][1] + box_rect_max[3][1]) / 4)
    return area_max_contour, contour_area_max, box_rect_max  # 返回最大的轮廓

###################################################关卡：楼梯#################################################
def up_stair():
    '''
    上楼梯函数
    '''
    global state,state_sel,org_img,step,img_debug,chest_ret,ChestOrg_img

    step_total_stair = 0
    state_sel = 'up_stair'
    state = 7
    step = 0
    robot_stair_center = False
    the_real_distance  = 0

    while state_sel == 'up_stair':
        if ChestOrg_img is None:
            continue
        ChestOrg_copy = np.rot90(ChestOrg_img)

        border = cv2.copyMakeBorder(ChestOrg_copy, 12, 12, 16, 16, borderType=cv2.BORDER_CONSTANT,value=(255, 255, 255))  # 扩展白边，防止边界无法识别
        Chest_img_copy = cv2.resize(border, (chest_r_width, chest_r_height), interpolation=cv2.INTER_CUBIC)  # 将图片缩放
        Chest_frame_gauss = cv2.GaussianBlur(Chest_img_copy,(3,3),0)

        Chest_frame_hsv = cv2.cvtColor(Chest_frame_gauss,cv2.COLOR_BGR2HSV)
        #图像处理 蓝色，绿色，红色
        if step_total_stair == 0:
            Chest_frame_blue = cv2.inRange(Chest_frame_hsv,color_range['blue_stair'][0],color_range['blue_stair'][1])
            Chest_opened = cv2.morphologyEx(Chest_frame_blue, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))  # 开运算 去噪点
        elif step_total_stair == 1:
            Chest_frame_green = cv2.inRange(Chest_frame_hsv,color_range['green_stair'][0],color_range['green_stair'][1])
            Chest_opened = cv2.morphologyEx(Chest_frame_green, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))  # 开运算 去噪点
        
        Chest_closed = cv2.morphologyEx(Chest_opened, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))  # 闭运算 封闭连接
        
        (_, contours, hierarchy) = cv2.findContours(Chest_closed, cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)  # 找出轮廓cv2.CHAIN_APPROX_NONE
       
        if contours is not None:    
            area_max_contour,contour_area_max,box_rect_max = getAreaMaxContour_great_stair(contours)
            if len(box_rect_max) == 0:
                continue
            top_left = box_rect_max[0]
            top_right = box_rect_max[1]
            bottom_right = box_rect_max[2]
            bottom_left = box_rect_max[3]

            top_angle = -int(math.atan((bottom_right[1] - bottom_left[1]) / (bottom_right[0] - bottom_left[0])) * 180 / math.pi)
            bottom_angle = -int(math.atan((bottom_right[1] - bottom_left[1]) / (bottom_right[0] - bottom_left[0])) * 180 / math.pi)
            top_center_y = int((top_left[1] + top_right[1]) / 2)
            bottom_center_x = int((bottom_left[0] + bottom_right[0]) / 2)
            bottom_center_y = int((bottom_left[1] + bottom_right[1]) / 2)

            cv2.circle(ChestOrg_copy, (top_right[0], top_right[1]), 5, [0, 255, 255], 2)
            cv2.circle(ChestOrg_copy, (top_left[0], top_left[1]), 5, [0, 255, 255], 2)
            cv2.circle(ChestOrg_copy, (bottom_right[0], bottom_right[1]), 5, [0, 255, 255], 2)
            cv2.circle(ChestOrg_copy, (bottom_left[0], bottom_left[1]), 5, [0, 255, 255], 2)

            cv2.putText(ChestOrg_copy,'bottom_center_y'+str(bottom_center_y),(30,200),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,0),4)
            cv2.putText(ChestOrg_copy,'top_angle'+str(top_angle),(30,230),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,0),4)
            cv2.putText(ChestOrg_copy,'top_center_y'+str(top_center_y),(30,260),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,0),4)
            cv2.imshow('chest',ChestOrg_copy)
            
            k = cv2.waitKey(1)
            if k == ord('q') & 0xff:
                cv2.destroyAllWindows()
                break
        else:
            continue

        if step_total_stair == 0:
            the_real_distance =  ((240 - bottom_left[0]) * math.tan((0-bottom_angle) * math.pi / 180) + (640 - bottom_left[1])) * math.cos((0 - bottom_angle) * math.pi / 180)
            if bottom_center_y < 450:#远得很，往前走就完了
                
                for i in range(int(the_real_distance) // 80):
                    action_append('forwardSlow0403')
                    print('253L')                   
                
            elif bottom_center_y >= 450 and bottom_center_y < 560:#有点近了，调整左右
                
                if bottom_center_x <= 190:
                    for i in range(2):
                        action_append("Left1move")
                elif bottom_center_x >= 290:
                    for i in range(2):
                        action_append("Right1move")
                for i in range((500 - bottom_center_y) // 70):
                    print("快接近一级楼梯了前进")
                    action_append('forwardSlow0403') 

            elif bottom_center_y >= 560:#近在咫尺，调角度，调好角度就冲鸭

                if top_angle > 2:
                    if top_angle >= 6:
                        for i in range((top_angle - 2) // 3):
                            action_append('turn001L')
                            print('259L')
                    else:
                        action_append('turn001L')
                        print('263L')

                elif top_angle < -2:
                    if top_angle <= -6:
                        for i in range(abs(top_angle + 6) // 3):
                            action_append('turn001R')
                            print('266L')
                    else:
                        action_append('turn001R')
                        print('272L')

                if top_angle >= -2 and top_angle <= 2:
                    print("314L")
                    action_append("Stand")
                    action_append("UpBridge")
                    action_append("Stand")
                    action_append("UpBridge")
                    action_append("Stand")
                    step_total_stair = 2
                    action_append("Stand")
                    action_append("Back0Run")
                    action_append("UpBridge")
                    break

def down_stair():
    '''
    下楼梯函数
    '''
    global state,state_sel,org_img,step,img_debug,chest_ret,ChestOrg_img

    step_total_stair = 0
    state_sel = 'down_stair'
    state = 0
    action_have_done = 0 #0代表着还在红色楼梯上，还没开始下楼梯

    while state_sel == 'down_stair':
        if ChestOrg_img is None:
            continue
        ChestOrg_copy = ChestOrg_img.copy()
        ChestOrg_copy = np.rot90(ChestOrg_copy)
        ChestOrg_copy = ChestOrg_copy.copy()

        border = cv2.copyMakeBorder(ChestOrg_copy, 12, 12, 16, 16, borderType=cv2.BORDER_CONSTANT,value=(255, 255, 255))  # 扩展白边，防止边界无法识别
        Chest_img_copy = cv2.resize(border, (chest_r_width, chest_r_height), interpolation=cv2.INTER_CUBIC)  # 将图片缩放
        Chest_frame_gauss = cv2.GaussianBlur(Chest_img_copy,(3,3),0)

        Chest_frame_hsv = cv2.cvtColor(Chest_frame_gauss,cv2.COLOR_BGR2HSV)
        #下阶梯图像处理 红色，绿色，蓝色
        Chest_frame_blue = cv2.inRange(Chest_frame_hsv,color_range['blue_stair'][0],color_range['blue_stair'][1])
        Chest_opened = cv2.morphologyEx(Chest_frame_blue, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))  # 开运算 去噪点
        
        Chest_closed = cv2.morphologyEx(Chest_opened, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))  # 闭运算 封闭连接
        
        (_, Chest_contours, hierarchy) = cv2.findContours(Chest_closed, cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)  # 找出轮廓cv2.CHAIN_APPROX_NONE
        # print("Chest_contours len:",len(Chest_contours))
        area_max_contour, contour_area_max, box_rect_max = getAreaMaxContour_down_stair(Chest_contours)  # 找出最大轮廓
        Chest_percent = round(contour_area_max * 100 / (chest_r_width* chest_r_height), 2)
       
        if area_max_contour is not None:#当有轮廓的时候
            
            top_left = box_rect_max[0]
            top_right = box_rect_max[1]
            bottom_right = box_rect_max[2]
            bottom_left = box_rect_max[3]
           
            top_angle = -int(math.atan((bottom_right[1] - bottom_left[1]) / (bottom_right[0] - bottom_left[0])) * 180 / math.pi)
            angle_bottom = -int(math.atan((bottom_right[1] - bottom_left[1]) / (bottom_right[0] - bottom_left[0])) * 180 / math.pi)
            Chest_top_center_y = int((top_left[1] + top_right[1]) / 2)
            Chest_bottom_center_y = int((bottom_left[1] + bottom_right[1]) / 2)
            
            if action_have_done == 0:
                
                if Chest_bottom_center_y < 400:
                    if top_angle > 2:
                        action_append("turn001L")
                    elif top_angle < -2:
                        action_append("turn001R")      
                    elif top_angle <= 2 and top_angle >= -2:
                        action_append("Forwalk001")
                elif Chest_bottom_center_y >= 400 :#意味着还在红色台阶上
                    action_append("DownBridge")
                    action_append("Forwalk00")
                    action_have_done += 1

            elif action_have_done == 1:
                if Chest_bottom_center_y < 520:
                    for i in range(int((Chest_bottom_center_y - 520) // 10)):
                        action_append("Forwalk001")
                
                else:
                    action_append("DownBridge")
                    action_append("Stand")
                    for i in range(3):
                        action_append("pre_xiapo")
                    action_append("Stand")
                    for i in range(2):
                        action_append("forwardSlow0403")
                    action_append("Stand")
                    break

def up_and_down_stair():
    up_stair()
    down_stair()                    

####################################################主程序##################################################
if __name__ == '__main__':
    while len(CMDcontrol.action_list) > 0 : # 等待执行完前面的动作再开始主程序
        print("等待启动")
        time.sleep(1)
    action_append("HeadTurnMM") # 头回正？准备动作？

    while True: # 一直循环这个主程序
        
            up_stair()

            while(1):
                print("结束")
                time.sleep(10000)