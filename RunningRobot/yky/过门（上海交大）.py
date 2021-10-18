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

################################################读取图像线程#################################################
# 接收视频流，转化为一帧帧图像；未成功接收报错
def get_img():
    global cap_chest,cap_head
    global ChestOrg_img,HeadOrg_img,chest_ret,head_ret
    while True:
        if cap_chest.isOpened() and cap_head.isOpend():      #摄像头初始化成功？
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

###################################################关卡：过门#################################################
def getAreaMaxContour_door(contours):
    box_rect_max = []
    contour_area_temp = 0
    contour_area_max = 0
    r_w = 480
    r_h = 640
    area_max_contour = None
    
    # 把每个轮廓最外面四个点找出来，得到宽和高，然后从面积判是不是最大 
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

        contour_area_temp = height * width

        if contour_area_temp > contour_area_max:
            contour_area_max = contour_area_temp
            if contour_area_temp > 25:  #只有在面积大于25时，最大面积的轮廓才是有效的，以过滤干扰
                area_max_contour = con
                box_rect_max = [top_left,top_right,bottom_right,bottom_left]

    return area_max_contour, contour_area_max, box_rect_max  # 返回最大的轮廓

def door():
    global angle_top,angle_bottom,Head_top_center_X,Head_top_center_Y
    global Head_bottom_center_X,Head_bottom_center_Y
    global Head_center_X,Head_center_Y,Head_box,Head_angle
    global step,step_sel,ChestOrg_img,HeadOrg_img,Head_contours
    k = 0.05
    r_w = 480
    r_h = 640      # 图像大小
    bottom_center_x = 240
    bottom_center_y = 640
    step = 0
    step_sel = 'door'
    the_last_have_door = False          # 用于判断上一帧是否检测到门
    the_last_time = 0
    the_current_time = 0
    first_not_have_door = False
    the_door_x_is_ok = False
    the_door_angle_is_ok = False        # 位置和角度调整到位的flag

    while step_sel == 'door':
        if ChestOrg_img is None:
            continue
        if HeadOrg_img is None :
            continue
        ChestOrg_copy = HeadOrg_img.copy()  # 可能原来用的是胸，发现胸的效果不好……？

        # 先判断和门之间的距离
        # 一系列图像处理：Chest_closed就是最终处理好的结果
        Chest_img_copy = cv2.resize(ChestOrg_copy, (r_w, r_h), interpolation=cv2.INTER_CUBIC)  
        Chest_frame_gauss = cv2.GaussianBlur(Chest_img_copy, (3, 3), 0)  # 高斯模糊
        Chest_frame_hsv = cv2.cvtColor(Chest_frame_gauss, cv2.COLOR_BGR2HSV)  # 将图片转换到HSV空间
        Chest_frame_blue = cv2.inRange(Chest_frame_hsv, color_dist['blue']['Lower'],color_dist['blue']['Upper'])  # 对原图像进行掩模运算（这个时候蓝的部分是白的，其他部分是黑的）
        Chest_opened = cv2.morphologyEx(Chest_frame_blue, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))  # 开运算 去噪点
        Chest_closed = cv2.morphologyEx(Chest_opened, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))  # 闭运算 封闭连接
        # 找出轮廓
        (_,Chest_contours, hierarchy) = cv2.findContours(Chest_closed, cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)  # 找出轮廓cv2.CHAIN_APPROX_NONE
        # (_, Chest_contours, hierarchy) = cv2.findContours(Chest_closed, cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE) 
        angle_top = 0
        angle_bottom = 0
        
        if Chest_contours is not None:
            the_last_have_door = True   #图像中有门
            Chest_areaMaxContour, Chest_area_max,Chest_box = getAreaMaxContour_door(Chest_contours)  # 找出最大轮廓,并记录最大轮廓的值
            Chest_percent = round(Chest_area_max * 100 / (r_w * r_h), 2) # 最大轮廓在画面中所占的百分比
            if Chest_box is not None:
                the_door_not_find = False    #找到最大轮廓
                left_top = Chest_box[0][1]
                right_top = Chest_box[1][1]

                # 上轮廓和下轮廓的倾角值（没用上）
                # angle_top = - math.atan((Chest_box[1][1] - Chest_box[0][1]) / (Chest_box[1][0] - Chest_box[0][0])) * 180.0 / math.pi
                # angle_bottom = - math.atan((Chest_box[2][1] - Chest_box[3][1]) / (Chest_box[2][0] - Chest_box[3][0])) * 180.0 / math.pi
                
                # 上下轮廓中间位置的x、y值
                Chest_top_center_x = int((Chest_box[1][0] + Chest_box[0][0]) / 2)
                Chest_top_center_y = int((Chest_box[1][1] + Chest_box[0][1]) / 2)
                Chest_bottom_center_x = int((Chest_box[2][0] + Chest_box[3][0]) / 2)
                Chest_bottom_center_y = int((Chest_box[2][1] + Chest_box[3][1]) / 2)
                
                # print("chest_top_center_x",Chest_top_center_x)
                # print("chest_center_y",Chest_top_center_y)
                
                # 中线的角度
                if math.fabs(Chest_top_center_x - Chest_bottom_center_x) <= 1:  # 得到连线的角度
                    Chest_angle = 90
                else:
                    Chest_angle = - math.atan((Chest_top_center_y - Chest_bottom_center_y) / (Chest_top_center_x - Chest_bottom_center_x)) * 180.0 / math.pi
                
                cv2.drawContours(Chest_img_copy, np.array([Chest_box]), 0, (0, 0, 255), 2)  # 将大矩形画在图上

                cv2.circle(Chest_img_copy, (Chest_box[1][0], Chest_box[1][1]), 5, [0, 255, 255], 2)
                cv2.circle(Chest_img_copy, (Chest_box[0][0], Chest_box[0][1]), 5, [0, 255, 255], 2)
                cv2.circle(Chest_img_copy, (Chest_box[2][0], Chest_box[2][1]), 5, [0, 255, 255], 2)
                cv2.circle(Chest_img_copy, (Chest_box[3][0], Chest_box[3][1]), 5, [0, 255, 255], 2)
                cv2.circle(Chest_img_copy, (Chest_top_center_x, Chest_top_center_y), 5, [0, 255, 255], 2)
                cv2.circle(Chest_img_copy, (Chest_bottom_center_x, Chest_bottom_center_y), 5, [0, 255, 255], 2) 

                #cv2.circle(Chest_img_copy, (Chest_center_x, Chest_center_y), 7, [255, 255, 255], 2)
                cv2.line(Chest_img_copy, (Chest_top_center_x, Chest_top_center_y), (Chest_bottom_center_x, Chest_bottom_center_y), [0, 255, 255],2)  # 画出上下中点连线
                if math.fabs(Chest_top_center_x - Chest_bottom_center_x) <= 1:  # 得到连线的角度
                    Chest_angle = 90
                else:
                    Chest_angle = - math.atan((Chest_top_center_y - Chest_bottom_center_y) / (Chest_top_center_x - Chest_bottom_center_x)) * 180.0 / math.pi
                cv2.drawContours(Chest_img_copy, Chest_contours, -1, (255, 0, 255), 1)
                
                cv2.putText(Chest_img_copy, "top_left:" + str(int(left_top)), (30, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.65,(0, 0, 0), 2)  # (0, 0, 255)BGR
                cv2.putText(Chest_img_copy, "top_right:" + str(int(right_top)), (30, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.65,(0, 0, 0), 2)  # (0, 0, 255)BGR
                
                cv2.imshow('Chest_Camera', Chest_img_copy)  # 显示图像
                cv2.waitKey(100)

        else:
            continue

        if math.fabs(left_top-right_top) <= 8:
            print("角度不用调了...",left_top-right_top)   # 是机器人和门不平齐，所以
            if math.fabs(Chest_top_center_x - 240) < 40: 
                print("调好了，直接走吧...",Chest_top_center_x) # 门的中线位于照片的中间，那就比较合适了
                distance_y = int(k*Chest_top_center_y) # ？？？懂了但是没完全懂……
                print("distance_y", distance_y)
                for i in range(distance_y):
                    action_append("forwardSlow0403")    # 先往前，走一段（distance_y应该是距前面的物体的步数）
                action_append("forwardSlow0403")  
                action_append("forwardSlow0403")        # 不是提供的动作，是自己设定的（蹲一点往前挪吗哈哈哈）
                action_append("Stand")
                action_append("forwardSlow0403")
                action_append("forwardSlow0403")
                action_append("Stand")
                print('走完啦！')
                break
            elif Chest_top_center_x < 240:
                print("需要往右调整")
                action_append("Right02move")
            else:
                print("需要往左调整")
                action_append("Left02move")         #左右调整

        elif left_top < right_top:
            print("需要右转...",left_top-right_top)
            action_append("turn001L")
        else:
            print("需要左转...",left_top-right_top)
            action_append("turn001R")               #角度调整

####################################################主程序##################################################
if __name__ == '__main__':
    while len(CMDcontrol.action_list) > 0 : # 等待执行完前面的动作再开始主程序
        print("等待启动")
        time.sleep(1)
    action_append("HeadTurnMM") # 头回正？准备动作？

    while True: # 一直循环这个主程序
        
            door()

            while(1):
                print("结束")
                time.sleep(10000)
            
       


