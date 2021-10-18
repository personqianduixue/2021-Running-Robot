#!/usr/bin/env python3
# coding:utf-8
import sys
sys.path.append('./mobilenet')
sys.path.append('./pytorchyolo')


from inference import *


import cv2
import math
import numpy as np
import threading
import eventlet
import time
import datetime
import detect, models

import CMDcontrol

#################################################初始化#########################################################
#camera_out = "chest"
#stream_head = "http://192.168.137.3:8082/?action=stream?dummy=param.mjpg"
cap_head = cv2.VideoCapture(2)
#stream_chest = "http://192.168.137.3:8080/?action=stream?dummy=param.mjpg"
cap_chest = cv2.VideoCapture(0)

action_DEBUG = False
#box_debug = True
debug = True
img_debug = True
debug_obstacle = False

step = 0

# 初始化头部舵机角度

chest_ret = False  # 胸部读取图像标志位
head_ret = False  # 头部读取图像标志位
ChestOrg_img = None  # 胸部原始图像更新(在获取图像时已经旋转90)
HeadOrg_img = None  # 头部原始图像更新
#ChestOrg_copy = None # 胸部原始图像的副本
#HeadOrg_copy = None  # 头部原始图像的副本


chest_r_width = 480
chest_r_height = 640
head_r_width = 640
head_r_height = 480

# 关卡判断标志[0~6]
FLAG = None

color_range = {
    #'yellow_door': [(20, 100, 60), (50, 240, 170)],
    'yellow_door': [(18, 63, 63), (50, 255, 255)],
    'black_door': [(25, 25, 10), (110, 150, 50)],
    'black_gap': [(0, 0, 0), (180, 255, 70)],

    'yellow_hole': [(25, 90, 70), (40, 255, 255)],
    'black_hole': [(10, 10, 10), (180, 190, 60)],

    'chest_red_floor': [(0, 40, 60), (20, 200, 190)],
    'chest_red_floor1': [(0, 100, 60), (20, 200, 210)],
    'chest_red_floor2': [(110, 100, 60), (180, 200, 210)],

    'green_bridge_1': [(60, 90, 40), (80, 255, 255)],#baitian
    #'green_bridge_1': [(60, 140, 90), (80, 255, 255)],#wangshang
    #'green_bridge_2': [(60, 55, 40), (80, 255, 255)],#wangshang
    'blue_bridge_1': [(68, 105, 53), (120, 255, 255)],#baitian
    'green_bridge': [(50, 100, 80), (80, 255, 255)],#baitian
    'blue_bridge': [(50, 95, 120), (120, 255, 255)],#baitian
    #'green_bridge': [(50, 75, 30), (100, 255, 210)],  # 前射强光(正常也满足)
    #'blue_bridge': [(50, 95, 90), (120, 255, 255)],  # 前射强光(正常也满足)
    #'black_dilei': [(0, 0, 0), (110, 160, 80)],#baitian
    'black_dilei': [(0, 0, 0), (130, 160, 80)],#wangshang???
    'white_dilei': [(60, 0, 70), (100, 255, 255)],
    'blue_langan': [(50, 160, 40), (120, 255, 255)]
}

color_dist = {'red': {'Lower': np.array([0, 160, 100]), 'Upper': np.array([180, 255, 250])},
              'black_dir': {'Lower': np.array([40, 20, 10]), 'Upper': np.array([120, 150, 70])},
              #   'black_line': {'Lower': np.array([50, 30, 20]), 'Upper': np.array([130, 145, 80])},
              'black_line': {'Lower': np.array([50, 30, 20]), 'Upper': np.array([130, 220, 80])},
              'blue': {'Lower': np.array([100, 80, 46]), 'Upper': np.array([124, 255, 255])},

              'ball_red': {'Lower': np.array([0, 160, 40]), 'Upper': np.array([190, 255, 255])},
              'blue_hole': {'Lower': np.array([100, 45, 40]), 'Upper': np.array([130, 255, 90])},
              }


################################################读取图像线程#################################################
def get_img():
    global ChestOrg_img, HeadOrg_img, head_ret, chest_ret

    global cap_chest, cap_head
    while True:
        if cap_chest.isOpened() or cap_head.isOpened():
            # if False:

            chest_ret, ChestOrg_img = cap_chest.read()
            head_ret, HeadOrg_img = cap_head.read()


            if head_ret:
                pass
            else:
                print("head_ret false ------------------")
                print("chest_ret true ------------------")
            if HeadOrg_img is None:
                print("HeadOrg_img error")
            if ChestOrg_img is None:
                print("ChestOrg_img error")

        else:
            time.sleep(0.01)

            print("fail to gain both pictures ")


# 读取图像线程
th1 = threading.Thread(target=get_img)
th1.setDaemon(True)  # 设置为后台线程，这里默认是False，设置为True之后则主线程不用等待子线程
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
th2.setDaemon(True)  # 设置为后台线程，这里默认是False，设置为True之后则主线程不用等待子线程
th2.start()

acted_name = ""
def action_append(act_name):
    global acted_name

    # print("please enter to continue...")
    # cv2.waitKey(0)

    if action_DEBUG == False:
        if act_name == "forwardSlow0403" and (acted_name == "Forwalk02RL" or acted_name == "Forwalk02L"):
            acted_name = "Forwalk02LR"
        elif act_name == "forwardSlow0403" and (acted_name == "Forwalk02LR" or acted_name == "Forwalk02R"):
            acted_name = "Forwalk02RL"
        elif act_name != "forwardSlow0403" and (acted_name == "Forwalk02LR" or acted_name == "Forwalk02R"):
            CMDcontrol.action_list.append("Forwalk02RS")
            acted_name = act_name

        elif act_name != "forwardSlow0403" and (acted_name == "Forwalk02RL" or acted_name == "Forwalk02L"):
            CMDcontrol.action_list.append("Forwalk02LS")
            acted_name = act_name

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



# 得到最大轮廓和对应的最大面积
def getAreaMaxContour(contours):  # 返回轮廓 和 轮廓面积
    contour_area_temp = 0
    contour_area_max = 0
    area_max_contour = None
    # area_max_contour = np.array([[[0, 0]], [[0, 1]], [[1, 1]], [[1, 0]]])
    for c in contours:  # 历遍所有轮廓
        contour_area_temp = math.fabs(cv2.contourArea(c))  # 计算轮廓面积
        if contour_area_temp > contour_area_max:
            contour_area_max = contour_area_temp
            if contour_area_temp > 25:  # 只有在面积大于25时，最大面积的轮廓才是有效的，以过滤干扰
                area_max_contour = c
    return area_max_contour, contour_area_max  # 返回最大的轮廓

def getAreaMaxContour1(contours):  # 返回轮廓 和 轮廓面积
    contour_area_temp = 0
    contour_area_max = 0
    area_max_contour = None
    for c in contours:  # 历遍所有轮廓
        contour_area_temp = math.fabs(cv2.contourArea(c))  # 计算轮廓面积
        if contour_area_temp > contour_area_max:
            contour_area_max = contour_area_temp
            if contour_area_temp > 25:  # 只有在面积大于25时，最大面积的轮廓才是有效的，以过滤干扰
                area_max_contour = c
    return area_max_contour, contour_area_max  # 返回最大的轮廓


########得到最大轮廓############
def getAreaMaxContour2(contours, area=1):
    contour_area_max = 0
    area_max_contour = None
    for c in contours:
        contour_area_temp = math.fabs(cv2.contourArea(c))
        if contour_area_temp > contour_area_max:
            contour_area_max = contour_area_temp
            if contour_area_temp > area:  # 面积大于1
                area_max_contour = c
    return area_max_contour


# 将所有面积大于1的轮廓点拼接到一起
def getSumContour(contours, area=1):
    contours_sum = None
    # print(len(contours))
    for c in contours:  # 初始化contours
        area_temp = math.fabs(cv2.contourArea(c))
        if (area_temp > area):
            contours_sum = c
            break
    for c in contours:
        area_temp = math.fabs(cv2.contourArea(c))
        if (area_temp > area):
            contours_sum = np.concatenate((contours_sum, c), axis=0)  # 将所有面积大于1的轮廓点拼接到一起
    return contours_sum


######### 得到所有轮廓的面积##########
def getAreaSumContour(contours):
    contour_area_sum = 0
    for c in contours:  # 历遍所有轮廓
        contour_area_sum += math.fabs(cv2.contourArea(c))  # 计算轮廓面积
    return contour_area_sum  # 返回最大的面积


#################################################过开始的横杆##########################################
def pass_start_bar():
    global ChestOrg_img,  step, img_debug

    step = 0


    while True:
        if ChestOrg_img is None:
            continue
        if step == 0:  # 判断门是否抬起
            t1 = cv2.getTickCount()  # 时间计算
            org_img_copy = ChestOrg_img.copy()
            org_img_copy = np.rot90(org_img_copy)
            handling = org_img_copy.copy()

            handling_cut = handling[:,:320,:]

            #border = cv2.copyMakeBorder(handling_cut, 12, 12, 16, 16, borderType=cv2.BORDER_CONSTANT,
            #                            value=(255, 255, 255))  # 扩展白边，防止边界无法识别
            #handling_cut= cv2.resize(border, (chest_r_width, chest_r_height), interpolation=cv2.INTER_CUBIC)  # 将图片缩放
            frame_gauss = cv2.GaussianBlur(handling_cut, (21, 21), 0)  # 高斯模糊
            frame_hsv = cv2.cvtColor(frame_gauss, cv2.COLOR_BGR2HSV)  # 将图片转换到HSV空间

            frame_door_yellow = cv2.inRange(frame_hsv, color_range['yellow_door'][0],
                                            color_range['yellow_door'][1])  # 对原图像和掩模(颜色的字典)进行位运算
            #frame_door_black = cv2.inRange(frame_hsv, color_range['black_door'][0],
            #                              color_range['black_door'][1])  # 对原图像和掩模(颜色的字典)进行位运算

            frame_door = frame_door_yellow
            open_pic = cv2.morphologyEx(frame_door, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))  # 开运算 去噪点
            closed_pic = cv2.morphologyEx(open_pic, cv2.MORPH_CLOSE, np.ones((50, 50), np.uint8))  # 闭运算 封闭连接
            # print(closed_pic)

            ( contours,_) = cv2.findContours(closed_pic, cv2.RETR_EXTERNAL,
                                                            cv2.CHAIN_APPROX_NONE)  # 找出轮廓
            areaMaxContour, area_max = getAreaMaxContour(contours)  # 找出最大轮廓
            percent = round(100 * area_max / (chest_r_width * chest_r_height), 2)  # 最大轮廓的百分比
            percent_cut = round(100 * area_max / (320 * chest_r_height), 2)
            if areaMaxContour is not None:
                rect = cv2.minAreaRect(areaMaxContour)  # 矩形框选
                box = np.int0(cv2.boxPoints(rect))  # 点的坐标
                if debug:
                    cv2.drawContours(handling_cut, [box], 0, (153, 200, 0), 2)  # 将最小外接矩形画在图上
                    cv2.drawContours(handling, [box], 0, (153, 200, 0), 2)
            if debug:
                cv2.putText(handling_cut, 'area: ' + str(percent_cut) + '%', (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                            (0, 0, 255), 2)
                cv2.putText(handling, 'area: ' + str(percent) + '%', (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                            (0, 0, 255), 2)
                t2 = cv2.getTickCount()
                time_r = (t2 - t1) / cv2.getTickFrequency()
                fps = 1.0 / time_r
                cv2.putText(handling, "fps:" + str(int(fps)), (30, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)
                cv2.imshow('handling', handling)  # 显示图像
                cv2.imshow('handling_cut', handling_cut)

                cv2.imshow('frame_door_yellow', frame_door_yellow)  # 显示图像
                #cv2.imshow('frame_door_black', frame_door_black)  # 显示图像
                cv2.imshow('closed_pic', closed_pic)  # 显示图像

                k = cv2.waitKey(10)
                if k == 27:
                    cv2.destroyWindow('closed_pic')
                    cv2.destroyWindow('handling')
                    cv2.destroyWindow('handling_cut')
                    break
                elif k == ord('s'):
                    print("save picture")
                    cv2.imwrite("picture.jpg", org_img_copy)  # 保存图片

            # 根据比例得到是否前进的信息
            if percent_cut > 6:  # 检测到横杆
                print(percent, "%")
                print("有障碍 等待 contours len：", len(contours))
                time.sleep(0.1)
            else:
                print(percent)

                
                action_append("fastForward03")

                step = 1

        elif step == 1:  # 寻找下一关卡


            action_append("Stand")

            step = 0

            break



#################################################0：过桥##########################################
count_forward = 0
the_distance_Y = 0 
def move_robot(the_distance_left, the_distance_right, the_distance_y, theta, Area):
    global is_bridge_done, count_forward,the_distance_Y
    if is_bridge_done:
        return
    if math.fabs(math.fabs(theta) - 90) <= 2:
        print("角度很准，直接走吧...", theta)
        if the_distance_left <= 10:
            print("看来不用往左边移动了...", the_distance_left)
        else:
            print("需要左移...", the_distance_left)
            action_append("Left02move")
            time.sleep(0.5)
            return

        if the_distance_right <= 10:
            print("看来不用往右边移动了...", the_distance_right)
        else:
            print("需要右移...", the_distance_right)
            action_append("Right02move")
            time.sleep(0.5)
            return

        print("调整好了，直行吧...")
        
        action_append("forwardSlow0403")
        action_append("forwardSlow0403")
        action_append("forwardSlow0403")
        count_forward+=1
        if Area < 30000 and count_forward > 1:
            action_append("forwardSlow0403")
            action_append("forwardSlow0403")
            action_append("Stand")
            is_bridge_done = 1
            return
        pass_bridge()
        
    else:
        if theta > 0:
            print("需要右转...", theta)
            action_append("turn001R")
        else:
            print("需要左转...", theta)
            action_append("turn001L")

is_bridge_done = 0
def pass_bridge():
    global step, ChestOrg_img, is_bridge_done, the_distance_Y, count_forward, FLAG

    r_w = chest_r_width
    r_h = chest_r_height
    time.sleep(1)

    while True:
        if is_bridge_done:
            break
        
        if ChestOrg_img is None:
            continue
        ChestOrg_copy = ChestOrg_img.copy()
        ChestOrg_copy = np.rot90(ChestOrg_img)
        ChestOrg_copy = ChestOrg_copy.copy()
        ChestOrg_copy = ChestOrg_copy[230:585, 0:480]
        border = cv2.copyMakeBorder(ChestOrg_copy, 12, 12, 16, 16, borderType=cv2.BORDER_CONSTANT,
                                    value=(255, 255, 255))  # 扩展白边，防止边界无法识别
        Chest_img_copy = cv2.resize(border, (r_w, r_h), interpolation=cv2.INTER_CUBIC)  # 将图片缩放

        Chest_frame_gauss = cv2.GaussianBlur(Chest_img_copy, (3, 3), 0)  # 高斯模糊
        Chest_frame_hsv = cv2.cvtColor(Chest_frame_gauss, cv2.COLOR_BGR2HSV)  # 将图片转换到HSV空间

        if FLAG==1 or FLAG==6 or FLAG==11:
            color_range_lower = color_range['green_bridge'][0]
            color_range_upper = color_range['green_bridge'][1]
        if FLAG==0 or FLAG==5 or FLAG==10:
            color_range_lower = color_range['blue_bridge'][0]
            color_range_upper = color_range['blue_bridge'][1]
            
        Chest_frame_green = cv2.inRange(Chest_frame_hsv, color_range_lower,
                                        color_range_upper)  # 对原图像和掩模(颜色的字典)进行位运算
        
        Chest_opened_green = cv2.morphologyEx(Chest_frame_green, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))  # 开运算 去噪点
        Chest_closed_green = cv2.morphologyEx(Chest_opened_green, cv2.MORPH_CLOSE,
                                              np.ones((3, 3), np.uint8))  # 闭运算 封闭连接

        (Chest_contours_green, hierarchy_green) = cv2.findContours(Chest_closed_green, cv2.RETR_LIST,
                                                                      cv2.CHAIN_APPROX_NONE)  # 找出轮廓cv2.CHAIN_APPROX_NONE
        # print("Chest_contours len:",len(Chest_contours))
        Chest_areaMaxContour_green, Chest_area_max_green = getAreaMaxContour(Chest_contours_green)  # 找出最大轮廓
        Chest_percent_green = round(Chest_area_max_green * 100 / (r_w * r_h), 2)



        Chest_areaMaxContour = Chest_areaMaxContour_green
        Chest_contours = Chest_contours_green
        Chest_percent = Chest_percent_green
        if Chest_areaMaxContour is not None:
            Chest_rect = cv2.minAreaRect(Chest_areaMaxContour)
            # center, w_h, Head_angle = rect  # 中心点 宽高 旋转角度
            Chest_box = np.int0(cv2.boxPoints(Chest_rect))  # 点的坐标

            # 初始化四个顶点坐标
            Chest_top_left = Chest_areaMaxContour[0][0]
            Chest_top_right = Chest_areaMaxContour[0][0]
            Chest_bottom_left = Chest_areaMaxContour[0][0]
            Chest_bottom_right = Chest_areaMaxContour[0][0]
            for c in Chest_areaMaxContour:  # 遍历找到四个顶点
                if c[0][0] + 1.5 * c[0][1] < Chest_top_left[0] + 1.5 * Chest_top_left[1]:
                    Chest_top_left = c[0]
                if (r_w - c[0][0]) + 1.5 * c[0][1] < (r_w - Chest_top_right[0]) + 1.5 * Chest_top_right[1]:
                    Chest_top_right = c[0]
                if c[0][0] + 1.5 * (r_h - c[0][1]) < Chest_bottom_left[0] + 1.5 * (r_h - Chest_bottom_left[1]):
                    Chest_bottom_left = c[0]
                if c[0][0] + 1.5 * c[0][1] > Chest_bottom_right[0] + 1.5 * Chest_bottom_right[1]:
                    Chest_bottom_right = c[0]
            angle_top = - math.atan(
                (Chest_top_right[1] - Chest_top_left[1]) / (Chest_top_right[0] - Chest_top_left[0])) * 180.0 / math.pi
            angle_bottom = - math.atan((Chest_bottom_right[1] - Chest_bottom_left[1]) / (
                        Chest_bottom_right[0] - Chest_bottom_left[0])) * 180.0 / math.pi
            Chest_top_center_x = int((Chest_top_right[0] + Chest_top_left[0]) / 2)
            Chest_top_center_y = int((Chest_top_right[1] + Chest_top_left[1]) / 2)
            Chest_bottom_center_x = int((Chest_bottom_right[0] + Chest_bottom_left[0]) / 2)
            Chest_bottom_center_y = int((Chest_bottom_right[1] + Chest_bottom_left[1]) / 2)
            Chest_center_x = int((Chest_top_center_x + Chest_bottom_center_x) / 2)
            Chest_center_y = int((Chest_top_center_y + Chest_bottom_center_y) / 2)

            d1 = 255 - Chest_center_x
            d2 = 640 - Chest_bottom_center_y
            if math.fabs(Chest_top_right[1] - Chest_top_left[1]) < 2:
                theta = 90
            else:
                theta = math.atan((Chest_top_right[0] - Chest_top_left[0]) / (
                            Chest_top_right[1] - Chest_top_left[1])) * 180.0 / math.pi


            if Chest_center_x > 255:
                the_distance_right = -d1  # + d2//100
                the_distance_left = 0
            else:
                the_distance_left = d1  # + d2//100
                the_distance_right = 0

            the_distance_y = d2 // 40
            if count_forward==0:
                the_distance_Y=the_distance_y
                
            Area = cv2.contourArea(Chest_areaMaxContour)
            print('Area:',Area)
            if Area < 30000 and count_forward > 1:
                action_append("forwardSlow0403")
                action_append("forwardSlow0403")
                action_append("Stand")
                is_bridge_done = 1
                break
                
            if img_debug:
                cv2.drawContours(Chest_img_copy, [Chest_box], 0, (0, 0, 255), 2)  # 将大矩形画在图上
                cv2.circle(Chest_img_copy, (Chest_top_right[0], Chest_top_right[1]), 5, [0, 255, 255], 2)
                cv2.circle(Chest_img_copy, (Chest_top_left[0], Chest_top_left[1]), 5, [0, 255, 255], 2)
                cv2.circle(Chest_img_copy, (Chest_bottom_right[0], Chest_bottom_right[1]), 5, [0, 255, 255], 2)
                cv2.circle(Chest_img_copy, (Chest_bottom_left[0], Chest_bottom_left[1]), 5, [0, 255, 255], 2)
                cv2.circle(Chest_img_copy, (Chest_top_center_x, Chest_top_center_y), 5, [0, 255, 255], 2)
                cv2.circle(Chest_img_copy, (Chest_bottom_center_x, Chest_bottom_center_y), 5, [0, 255, 255], 2)
                cv2.circle(Chest_img_copy, (Chest_center_x, Chest_center_y), 7, [255, 255, 255], 2)
                cv2.line(Chest_img_copy, (Chest_top_center_x, Chest_top_center_y),
                         (Chest_bottom_center_x, Chest_bottom_center_y), [0, 255, 255], 2)

                cv2.drawContours(Chest_img_copy, Chest_contours, -1, (255, 0, 255), 1)
                cv2.putText(Chest_img_copy, "right:" + str(int(the_distance_right)), (30, 170),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 2)
                cv2.putText(Chest_img_copy, "left:" + str(int(the_distance_left)), (30, 220), cv2.FONT_HERSHEY_SIMPLEX,
                            0.65, (0, 0, 0), 2)
                cv2.putText(Chest_img_copy, "theta:" + str(int(theta)), (30, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.65,
                            (0, 0, 0), 2)
                cv2.putText(Chest_img_copy, "y:" + str(int(the_distance_y)), (30, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.65,
                            (0, 0, 0), 2)
                cv2.imshow('Chest', Chest_img_copy)
                k = cv2.waitKey(1)
                if k == ord('w') & 0xff:
                    break

            move_robot(the_distance_left, the_distance_right, the_distance_y, theta, Area)
        else:
            continue



#################################################1：过雷区##########################################
the_forwalk_total = 0
Last_baffle_dis_Y = 200
def get_angle1():
    global  ChestOrg_img, HeadOrg_img, the_forwalk_total, Last_baffle_dis_Y
    if ChestOrg_img is None:
        baffle_angle,baffle_dis_Y = 0,Last_baffle_dis_Y
    else:
        Corg_img = ChestOrg_img.copy()
        Corg_img = np.rot90(Corg_img)
        OrgFrame = Corg_img.copy()

        
        max_index=int(0.8984*Last_baffle_dis_Y+7.378)
        OrgFrame[0:max_index, :] = 255   

        center = []

        hsv = cv2.cvtColor(OrgFrame, cv2.COLOR_BGR2HSV)
        hsv = cv2.GaussianBlur(hsv, (3, 3), 0)
        Imask = cv2.inRange(hsv, color_range['blue_langan'][0], color_range['blue_langan'][1])
        Imask = cv2.erode(Imask, None, iterations=2)
        Imask = cv2.dilate(Imask, np.ones((3, 3), np.uint8), iterations=2)
        cv2.imshow('Angle1_Imask',Imask)
        cnts, hieracy = cv2.findContours(Imask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)  # 找出所有轮廓

        if cnts is not None:
            cnt_large = getAreaMaxContour2(cnts, area=500)
        else:
            print("1135L cnt_large is None")
        
        blue_bottom_Y = 0
        if cnt_large is not None:
            rect = cv2.minAreaRect(cnt_large)
            box = np.int0(cv2.boxPoints(rect))
            Ax = box[0, 0]
            Ay = box[0, 1]
            Bx = box[1, 0]
            By = box[1, 1]
            Cx = box[2, 0]
            Cy = box[2, 1]
            Dx = box[3, 0]
            Dy = box[3, 1]
            pt1_x, pt1_y = box[0, 0], box[0, 1]
            pt3_x, pt3_y = box[2, 0], box[2, 1]
            center_x = int((pt1_x + pt3_x) / 2)
            center_y = int((pt1_y + pt3_y) / 2)
            center.append([center_x, center_y])
            cv2.drawContours(OrgFrame, [box], -1, [0, 0, 255, 255], 3)
            cv2.circle(OrgFrame, (center_x, center_y), 10, (0, 0, 255), -1)  # 画出中心点
            if math.sqrt(math.pow(box[3, 1] - box[0, 1], 2) + math.pow(box[3, 0] - box[0, 0], 2)) > math.sqrt(
                    math.pow(box[3, 1] - box[2, 1], 2) + math.pow(box[3, 0] - box[2, 0], 2)):
                baffle_angle = - math.atan((box[3, 1] - box[0, 1]) / (box[3, 0] - box[0, 0])) * 180.0 / math.pi
            else:
                baffle_angle = - math.atan(
                    (box[3, 1] - box[2, 1]) / (box[3, 0] - box[2, 0])) * 180.0 / math.pi  # 负号是因为坐标原点的问题
            if center_y > blue_bottom_Y:
                baffle_dis_Y = center_y
            cv2.putText(OrgFrame, "baffle_angle:" + str(int(baffle_angle)), (230, 400),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 2)  # (0, 0, 255)BGR
            cv2.putText(OrgFrame, "blue_bottom_Y:" + str(int(baffle_dis_Y)) , (230, 440),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 2)  # (0, 0, 255)BGR
            cv2.imshow('Angle1', OrgFrame)
            #cv2.waitKey(1)    
                
        else:
            print('cnt_large is  None')
            baffle_angle,baffle_dis_Y = 0, Last_baffle_dis_Y
            
    return baffle_angle,baffle_dis_Y


def pass_landmine():
    global ChestOrg_img, HeadOrg_img, the_forwalk_total, Last_baffle_dis_Y
    the_right_left = False

    print("/-/-/-/-/-/-/-/-/-进入obstacle")
    is_enter = 0
    is_center = 0
    is_end = 0
    while True:
        #if the_forwalk_total > 4:
         #   is_enter = 1

        #if the_forwalk_total >=12 and the_forwalk_total <=14:
        #    is_center = 1

        #if Last_baffle_dis_Y >=350 and the_forwalk_total > 10:
        #    is_end = 1
   
        if ChestOrg_img is None:
            continue
        
        
        Corg_img0 = ChestOrg_img.copy()
        Corg_img0 = np.rot90(Corg_img0)

        Corg_img = Corg_img0.copy()
        '''if is_enter:
            Corg_img[0:290, :] = 255
            Corg_img[550:640, :] = 255
        else:
            Corg_img[0:290, :] = 255
            Corg_img[500:640, :] = 255
        if is_center:
            Corg_img[450:640, :] = 255
        if is_end :
            Corg_img[0:640, :] = 255'''
        hsv = cv2.cvtColor(Corg_img, cv2.COLOR_BGR2HSV)
        hsv = cv2.GaussianBlur(hsv, (3, 3), 0)

        Imask = cv2.inRange(hsv, color_range['black_dilei'][0], color_range['black_dilei'][1])
        #cv2.imshow('Imask', Imask)
        Imask = cv2.morphologyEx(Imask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))  # 开运算 去噪点
        Imask = cv2.morphologyEx(Imask, cv2.MORPH_CLOSE,
                                 np.ones((3, 3), np.uint8))  # 闭运算 封闭连接
        #cv2.imshow('black', Imask)
        contours, hierarchy = cv2.findContours(Imask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)  # 找出所有轮廓
        # print("contours lens:",len(contours))
        cv2.drawContours(Corg_img, contours, -1, (255, 0, 255), 2)

        # 这只是个初始化，往后看就明白了
        left_point = [480, 0]
        right_point = [0, 0]

        if len(contours) != 0:
            Big_battle = [0, 0]

            for c in contours:
                rect = cv2.minAreaRect(c)
                box = cv2.boxPoints(rect)  # 我们需要矩形的4个顶点坐标box, 通过函数 cv2.cv.BoxPoints() 获得
                box = np.intp(box)  # 最小外接矩形的四个顶点
                box_Ax, box_Ay = box[0, 0], box[0, 1]
                box_Bx, box_By = box[1, 0], box[1, 1]
                box_Cx, box_Cy = box[2, 0], box[2, 1]
                box_Dx, box_Dy = box[3, 0], box[3, 1]
                box_centerX = int((box_Ax + box_Bx + box_Cx + box_Dx) / 4)
                box_centerY = int((box_Ay + box_By + box_Cy + box_Dy) / 4)
                box_center = [box_centerX, box_centerY]
                # cv2.circle(Corg_img, (box_centerX,box_centerY), 7, (0, 255, 0), -1) #距离比较点 绿圆点标记
                # cv2.drawContours(Corg_img, [box], -1, (255,0,0), 3)

                if box_centerY < 250 or box_centerY > 610:
                    continue

                # 找出最左点与最右点
                if box_centerX < left_point[0]:
                    left_point = box_center
                if box_centerX > right_point[0]:
                    right_point = box_center

                if box_centerX <= 80 or box_centerX >= 400:  # 排除左右边沿点 box_centerX ,box_centerX 240
                    continue

                if math.pow(box_centerX - 240, 2) + math.pow(box_centerY - 640, 2) < math.pow(Big_battle[0] - 240,
                                                                                              2) + math.pow(
                        Big_battle[1] - 640, 2):
                    Big_battle = box_center  # 找出最近的障碍物

            baffle_angle, baffle_dis_Y = get_angle1()
            Last_baffle_dis_Y = baffle_dis_Y
            print('baffle_angle, baffle_dis_Y:',baffle_angle,' ### ', baffle_dis_Y)

            cv2.circle(Corg_img, (left_point[0], left_point[1]), 7, (0, 255, 0), -1)  # 圆点标记
            cv2.circle(Corg_img, (right_point[0], right_point[1]), 7, (0, 255, 255), -1)  # 圆点标记
            cv2.circle(Corg_img, (Big_battle[0], Big_battle[1]), 7, (255, 255, 0), -1)  # 圆点标记
            cv2.putText(Corg_img, "Left_point:" + str(int(left_point[0])) + "," + str(int(left_point[1])), (230, 400),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 2)  # (0, 0, 255)BGR
            cv2.putText(Corg_img, "Right_point:" + str(int(right_point[0])) + "," + str(int(right_point[1])),
                        (230, 440), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 2)  # (0, 0, 255)BGR
            cv2.putText(Corg_img, "Big_battle:" + str(int(Big_battle[0])) + "," + str(int(Big_battle[1])), (230, 480),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 2)  # (0, 0, 255)BGR

            cv2.line(Corg_img, (Big_battle[0], Big_battle[1]), (240, 640), (0, 255, 255), thickness=2)
            # 500线
            cv2.line(Corg_img, (0, 500), (480, 500), (255, 255, 255), thickness=2)

            cv2.imshow('Corg_img', Corg_img)
            
            if 1:

                
                if baffle_angle < -1 and the_forwalk_total%1 == 0:
                    action_append("turn001R")
                elif baffle_angle > 1 and the_forwalk_total%1 == 0:
                    action_append("turn001L")
                    
                elif baffle_dis_Y > 340 and the_forwalk_total > 6:
                    print('dilei finish!!!')
                    break
                
                elif Big_battle[1] <= 320:
                    print("608L 前进靠近 forwardSlow0403 ", Big_battle[1])
                    action_append("forwardSlow0403")
                    # action_append("forwardSlow0403")
                    the_forwalk_total += 1
                elif Big_battle[1] <= 380:
                    print("565L 前进靠近 Forwalk01 ", Big_battle[1])
                    action_append("Forwalk01")
                    the_forwalk_total += 1
                elif Big_battle[1] < 400:
                    print("571L 慢慢前进靠近 Forwalk01  ", Big_battle[1])
                    action_append("Forwalk01")
                    the_forwalk_total += 1
                # elif Big_battle[1] < 430 and (Big_battle[0] <= (100 + (640 - Big_battle[1]) * 0.15) or Big_battle[0] >= (
                #         380 - (640 - Big_battle[1]) * 0.15)):
                #     print("568L 前进靠近 Forwalk00  ", Big_battle[1])
                #     action_append("Forwalk00")

                # 60---150---225---*240*---270---350---400
                elif 60 <= Big_battle[0] and Big_battle[0] < 150:
                    print("右平移一点点")
                    action_append('Right02move')
                    time.sleep(1)
                elif 150 <= Big_battle[0] and Big_battle[0] < 225:
                    print('向右平移一步')
                    action_append('Right02move')
                    time.sleep(1)
                elif 225 <= Big_battle[0] and Big_battle[0] < 240:
                    print('向右平移一大步')
                    action_append('Right02move')
                    time.sleep(1)
                elif 240 <= Big_battle[0] and Big_battle[0] < 255:
                    print('向左平移一大步')
                    action_append('Left02move')
                    time.sleep(1)
                elif 255 <= Big_battle[0] and Big_battle[0] < 270:  # 顺便去检测之前机器人已经往左边走了几个了，负数代表往右走
                    print('向左平移一步')
                    action_append('Left02move')
                    time.sleep(1)
                elif 270 <= Big_battle[0] and Big_battle[0] < 350:
                    print('向左平移一步')
                    action_append('Left02move')
                    time.sleep(1)
                elif 350 <= Big_battle[0] and Big_battle[0] < 400:  # 能离机器人这么远，机器人还没出事说明此障碍物不是在很边界的地方
                    print('向左平移一点点')
                    action_append('Left02move')
                    time.sleep(1)

        else:
            if debug_action:
                '''if is_end:
                    action_append("forwardSlow0403")
                    break'''
                print("287L 无障碍，可前进")
                action_append("forwardSlow0403")
                the_forwalk_total += 1
                Big_battle = [0, 0]


        cv2.circle(Corg_img, (left_point[0], left_point[1]), 7, (0, 255, 0), -1)  # 圆点标记
        cv2.circle(Corg_img, (right_point[0], right_point[1]), 7, (0, 255, 255), -1)  # 圆点标记
        cv2.circle(Corg_img, (Big_battle[0], Big_battle[1]), 7, (255, 255, 0), -1)  # 圆点标记
        cv2.putText(Corg_img, "Left_point:" + str(int(left_point[0])) + "," + str(int(left_point[1])), (230, 400),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 2)  # (0, 0, 255)BGR
        cv2.putText(Corg_img, "Right_point:" + str(int(right_point[0])) + "," + str(int(right_point[1])), (230, 440),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 2)  # (0, 0, 255)BGR
        cv2.putText(Corg_img, "Big_battle:" + str(int(Big_battle[0])) + "," + str(int(Big_battle[1])), (230, 480),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 2)  # (0, 0, 255)BGR

        cv2.line(Corg_img, (Big_battle[0], Big_battle[1]), (240, 640), (0, 255, 255), thickness=2)
        # 500线
        cv2.line(Corg_img, (0, 500), (480, 500), (255, 255, 255), thickness=2)

        cv2.imshow('Corg_img', Corg_img)
        cv2.waitKey(1)
        



#################################################2：过障碍##########################################
def get_all_area(contours,contour_area_threshold = 0):
    contour_area_sum = 0
    for c in contours:
        contour_area_now = math.fabs(cv2.contourArea(c))
        if contour_area_now > contour_area_threshold:
            contour_area_sum += contour_area_now
    return contour_area_sum

def pass_obstacle():
    global step, ChestOrg_img, HeadOrg_img
    step = 0
    baffle_dis_Y_flag = False
    baffle_angle = 0

    print('进入baffle')
    while True:
        xiayige = False
        if ChestOrg_img is None:
            continue
        if HeadOrg_img is None:
            continue
        Corg_img = ChestOrg_img.copy()
        Corg_img = np.rot90(Corg_img)
        OrgFrame = Corg_img.copy()
        Corg_img2 = HeadOrg_img.copy()
        OrgFrame2 = Corg_img2.copy()
        cv2.imshow('cheat',OrgFrame)
        cv2.imshow('head', OrgFrame2)
        OrgFrame[0:260, :, :] = 255
        # OrgFrame[590:640, :, :] = 255
        center = []

        hsv = cv2.cvtColor(OrgFrame, cv2.COLOR_BGR2HSV)
        hsv = cv2.GaussianBlur(hsv, (3, 3), 0)
        Imask = cv2.inRange(hsv, color_range['blue_langan'][0], color_range['blue_langan'][1])
        Imask = cv2.erode(Imask, None, iterations=2)
        Imask = cv2.dilate(Imask, np.ones((3, 3), np.uint8), iterations=2)
        cnts, hieracy = cv2.findContours(Imask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)  # 找出所有轮廓

        hsv2 = cv2.cvtColor(OrgFrame2, cv2.COLOR_BGR2HSV)
        hsv2 = cv2.GaussianBlur(hsv2, (3, 3), 0)
        Imask2 = cv2.inRange(hsv2, color_range['blue_langan'][0], color_range['blue_langan'][1])
        Imask2 = cv2.erode(Imask2, None, iterations=2)
        Imask2 = cv2.dilate(Imask2, np.ones((3, 3), np.uint8), iterations=2)
        cnt2, hieracy2 = cv2.findContours(Imask2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)  # 找出所有轮廓
        if cnts is not None:
            blue_area = get_all_area(cnt2, 500)
        else:
            print("1135L cnt_large is None")
            continue

        if cnts is not None:
            cnt_large = getAreaMaxContour2(cnts, area=1000)
        else:
            print("1135L cnt_large is None")
            continue

        blue_bottom_Y = 0

        if cnt_large is not None:
            rect = cv2.minAreaRect(cnt_large)
            box = np.int0(cv2.boxPoints(rect))
            Ax = box[0, 0]
            Ay = box[0, 1]
            Bx = box[1, 0]
            By = box[1, 1]
            Cx = box[2, 0]
            Cy = box[2, 1]
            Dx = box[3, 0]
            Dy = box[3, 1]
            pt1_x, pt1_y = box[0, 0], box[0, 1]
            pt3_x, pt3_y = box[2, 0], box[2, 1]
            center_x = int((pt1_x + pt3_x) / 2)
            center_y = int((pt1_y + pt3_y) / 2)
            center.append([center_x, center_y])
            cv2.drawContours(OrgFrame, [box], -1, [0, 0, 255, 255], 3)
            cv2.circle(OrgFrame, (center_x, center_y), 10, (0, 0, 255), -1)  # 画出中心点
            if math.sqrt(math.pow(box[3, 1] - box[0, 1], 2) + math.pow(box[3, 0] - box[0, 0], 2)) > math.sqrt(
                    math.pow(box[3, 1] - box[2, 1], 2) + math.pow(box[3, 0] - box[2, 0], 2)):
                baffle_angle = - math.atan((box[3, 1] - box[0, 1]) / (box[3, 0] - box[0, 0])) * 180.0 / math.pi
            else:
                baffle_angle = - math.atan(
                    (box[3, 1] - box[2, 1]) / (box[3, 0] - box[2, 0])) * 180.0 / math.pi  # 负号是因为坐标原点的问题
            if center_y > blue_bottom_Y:
                blue_bottom_Y = center_y
        else:
            print('cnt_large is  None')
            continue
        baffle_dis_Y = blue_bottom_Y
        if baffle_dis_Y > 240:
            baffle_dis_Y_flag = True
        # print('baffle_angle:',baffle_angle)
        # print('blue_bottom_Y',blue_bottom_Y)
        cv2.putText(OrgFrame, "baffle_angle:" + str(int(baffle_angle)), (230, 400),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 2)  # (0, 0, 255)BGR
        cv2.putText(OrgFrame, "blue_bottom_Y:" + str(int(blue_bottom_Y)) , (230, 440),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 2)  # (0, 0, 255)BGR
        cv2.imshow('OrgFrame1', OrgFrame)
        cv2.waitKey(1)

        if True:
            print('step:', step)
            if step == 0:
                if baffle_dis_Y <= 250:
                    print('大步前进')
                    action_append('Forwalk02')
                else:
                    step = 1
            elif step == 1:
                if baffle_angle > 4:
                    if baffle_angle > 8:
                        print("1471L 大左转一下  turn001L  baffle_angle:", baffle_angle)
                        action_append("turn001L")
                    else:
                        print("1474L 左转 turn000L  baffle_angle:", baffle_angle)
                        action_append("turn001L")
                elif baffle_angle < -4:
                    if baffle_angle < -8:
                        print("1478L 大右转一下  turn001R  baffle_angle:", baffle_angle)
                        action_append("turn001R")
                    else:
                        print("1481L 右转 turn000R  baffle_angle:", baffle_angle)
                        action_append("turn001R")
                else:
                    step = 2
            elif step == 2:
                if baffle_dis_Y < 390:
                    print("318L 大一步前进 forwardSlow0403")
                    action_append("forwardSlow0403")
                elif 390 < baffle_dis_Y < 460:
                    print("320L 向前挪动 Forwalk00")
                    action_append("Forwalk00")
                elif 460 < baffle_dis_Y:
                    step = 4
#             elif step == 3:
#                 if blue_area < 8000:
#                     action_append('Left02move')
#                     time.sleep(1)
#                 elif blue_area > 10000:
#                     action_append('Right02move')
#                     time.sleep(1)
#                 else:
#                     step =4
            elif step == 4:
                if baffle_angle > 2:
                    if baffle_angle > 5:
                        print("316L 大左转一下  turn001L ", baffle_angle)
                        action_append("turn001L")
                    else:
                        print("318L 左转 turn001L")
                        action_append("turn001L")
                elif baffle_angle < -2:
                    if baffle_angle < -5:
                        print("321L 大右转一下  turn001R ", baffle_angle)
                        action_append("turn001R")
                    else:
                        print("323L 右转 turn001R ", baffle_angle)
                        action_append("turn001R")
                elif baffle_dis_Y_flag:
                    step = 5

            elif step == 5:
                print("342L 前挪一点点")
                print("326L 翻栏杆 翻栏杆 RollRail")
                action_append("Stand")
                action_append("RollRail")
                xiayige = True

            if xiayige == True:
                break

#################################################3：过门##########################################
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

    for con in contours:  # 历遍所有轮廓
        contour_area_temp = math.fabs(cv2.contourArea(con))  # 计算轮廓面积
        # print(math.fabs(cv2.contourArea(con)))
        if contour_area_temp > 1000:
            if contour_area_temp >= contour_area_max:
                contour_area_max = contour_area_temp
                area_max_contour = con
    
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
            #HeadOrg_img_blue = cv2.inRang
            e(HeadOrg_img_hsv, np.array([95, 80, 46]),np.array([124, 255, 255]))  # 对原图像进行掩模运算（这个时候蓝的部分是白的，其他部分是黑的）
            HeadOrg_img_blue = cv2.inRange(HeadOrg_img_hsv, np.array([90, 75, 50]),np.array([124, 255, 255]))
            HeadOrg_img_opened = cv2.morphologyEx(HeadOrg_img_blue, cv2.MORPH_OPEN, np.ones((8, 8), np.uint8))  # 开运算 去噪点
            HeadOrg_img_closed = cv2.morphologyEx(HeadOrg_img_opened, cv2.MORPH_CLOSE, np.ones((8, 8), np.uint8))  # 闭运算 封闭连接

            # 找轮廓及4个顶点
            (contours, hierarchy) = cv2.findContours(HeadOrg_img_closed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            if Head_top_center_y_last > 10:
                max_area, max_contour, max_box= getAreaMaxContour_door1(contours)
            if Head_top_center_y_last <= 10:
                max_area, max_contour, max_box= getAreaMaxContour_door0(contours)

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
            #cv2.imwrite('door_'+str(j)+'.jpg', HeadOrg_img_forshow0)
            #cv2.imwrite('door_close_'+str(j)+'.jpg', HeadOrg_img_forshow1)
            j = j + 1

        # 后一步用胸部摄像头    
        if step_door_flag == 2:

            if ChestOrg_img is None:
                continue

            ChestOrg_img = ChestOrg_img.copy()
            ChestOrg_img_90 = np.rot90(ChestOrg_img)
            ChestOrg_img_door = ChestOrg_img_90[160:,:,:]
            ChestOrg_img_draw = ChestOrg_img_door.copy()

            ChestOrg_img_gauss = cv2.GaussianBlur(ChestOrg_img_door, (5, 5), 0)  # 高斯模糊
            ChestOrg_img_hsv = cv2.cvtColor(ChestOrg_img_gauss, cv2.COLOR_BGR2HSV)  # 将图片转换到HSV空间
            ChestOrg_img_blue = cv2.inRange(ChestOrg_img_hsv, np.array([100, 80, 46]),np.array([124, 255, 255]))  # 对原图像进行掩模运算（这个时候蓝的部分是白的，其他部分是黑的）
            ChestOrg_img_opened = cv2.morphologyEx(ChestOrg_img_blue, cv2.MORPH_OPEN, np.ones((15, 15), np.uint8))  # 开运算 去噪点
            ChestOrg_img_closed = cv2.morphologyEx(ChestOrg_img_opened, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))  # 闭运算 封闭连接
            
            (contours, hierarchy) = cv2.findContours(ChestOrg_img_closed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            max_area, max_contour, max_box= getAreaMaxContour_door1(contours)

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
            i = i + 1

        #转身前调整   
        if step_door_flag == 0:

            if Head_bottom_center_y < 470:
                
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
                        action_append("Right02move")
                        time.sleep(1)
                    else:
                        print(str(j - 1) + "往左一点点01")
                        action_append("Left02move")
                        time.sleep(1)
                    
                if Head_top_center_y <= 10:
                    if math.fabs(Head_top_angle) >= 5:
                        action_append("Back2Run")
                        print(str(j - 1) + "too02_angle")
                        continue
                    if math.fabs(Head_bottom_center_x - 320) > 20:
                        action_append("Back2Run")
                        print(str(j - 1) + "too02_x")
                        continue
                    else:
                        '''print(str(j - 1) + "转身")
                        action_append("turn010R")
                        action_append("turn010R")
                        action_append("HeadTurn185")'''
                        step_door_flag = 2
                        time.sleep(0.2)
                        #action_append("Back2Run")
                        cv2.destroyAllWindows()
                        continue

        #转身后及其调整                                    
        '''if step_door_flag == 1:
        
            if math.fabs(Head_top_angle) <=5:
                print("角度可了10")
            elif  Head_top_angle > 0:
                print("右转一点点10")
                action_append("turn001R")
                continue
            else:
                print("左转一点点10")
                action_append("turn001L")
                continue

            if math.fabs(Head_top_center_x - 320) < 20:
                print("前后可了10")
                step_door_flag = 2
                continue
            elif Head_top_center_x < 320:
                print("往后一点点10")
                action_append("Back0Run")
            else:
                print("往前一点点10")
                action_append("Forwalk00")'''        

        # 开胸部摄像头判断前后位置    
        '''if step_door_flag == 2:

            if Chest_left_center_x <370 :

                print(str(i - 1) + "左移" + str(Chest_left_center_x))
                action_append("Left3move")
                time.sleep(1)

                if step_turn_times < 3 :
                    step_turn_times = step_turn_times + 1
                else:
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
        
            
#################################################4：过坑##########################################
'''def bridge_choose(r_w, r_h):
    global ChestOrg_img
    if ChestOrg_img is None:
        continue
    Corg_img = ChestOrg_img.copy()

    Corg_img = Corg_img.copy()
    org_img_copy = cv2.resize(Corg_img, (r_w, r_h), interpolation=cv2.INTER_CUBIC)  # 将图片缩放
    frame_gauss = cv2.GaussianBlur(org_img_copy, (3, 3), 0)  # 高斯模糊
    frame_hsv = cv2.cvtColor(frame_gauss, cv2.COLOR_BGR2HSV)  # 将图片转换到HSV空间


    frame_floor_red = cv2.inRange(frame_hsv, color_dist['red']['Lower'],
                                  color_dist['red']['Upper'])  # 对原图像和红色掩膜位运算

    frame_floor_green = cv2.inRange(frame_hsv, color_range['green_bridge_1'][0],
                                    color_range['green_bridge_1'][1])  # 对原图像和绿色掩膜位运算
    frame_floor_blue = cv2.inRange(frame_hsv, color_range['blue_bridge_1'][0],
                                   color_range['blue_bridge_1'][1])  # 对原图像和蓝色掩膜位运算



    cnts_red, _ = cv2.findContours(frame_floor_red, cv2.RETR_EXTERNAL,
                                                    cv2.CHAIN_APPROX_TC89_L1)  # 找出所有轮廓
    cnts_green, _ = cv2.findContours(frame_floor_green, cv2.RETR_EXTERNAL,
                                                        cv2.CHAIN_APPROX_TC89_L1)  # 找出所有轮廓
    cnts_blue, _ = cv2.findContours(frame_floor_blue, cv2.RETR_EXTERNAL,
                                                      cv2.CHAIN_APPROX_TC89_L1)  # 找出所有轮廓



    areaMaxContour_green, area_max_green = getAreaMaxContour(cnts_green)  # 找出绿色最大轮廓
    percent_green = round(area_max_green * 100 / (r_w * r_h), 2)  # 绿色最大轮廓百分比
    areaMaxContour_blue, area_max_blue = getAreaMaxContour(cnts_blue)  # 找出蓝色最大轮廓
    percent_blue = round(area_max_blue * 100 / (r_w * r_h), 2)  # 蓝色最大轮廓百分比


    print('p_green', percent_green, 'p_blue', percent_blue)

    if percent_blue > 1 and percent_blue>percent_green:
        print('blue bridge')
        return 1
    else:
        print('green bridge')
        return 0
'''

def pass_hole():
    global step,  ChestOrg_img
    r_w = chest_r_width
    r_h = chest_r_height
    step = 0
    is_enter = 0
    # time.sleep(1)
    while True:
        if ChestOrg_img is None:
            continue
        ChestOrg_copy = ChestOrg_img.copy()
        ChestOrg_copy = np.rot90(ChestOrg_img)
        index_bottom = 555
        if  is_enter :
            ChestOrg_copy = ChestOrg_copy[150:index_bottom, 150:480]
        else:
            ChestOrg_copy = ChestOrg_copy[150:680, 0:480]
        border = cv2.copyMakeBorder(ChestOrg_copy, 12, 12, 16, 16, borderType=cv2.BORDER_CONSTANT,
                                    value=(255, 255, 255))  # 扩展白边，防止边界无法识别
        Chest_img_copy = cv2.resize(border, (r_w, r_h), interpolation=cv2.INTER_CUBIC)  # 将图片缩放
        #cv2.imshow('3', Chest_img_copy)
        Chest_frame_gauss = cv2.GaussianBlur(Chest_img_copy, (3, 3), 0)  # 高斯模糊
        Chest_frame_hsv = cv2.cvtColor(Chest_frame_gauss, cv2.COLOR_BGR2HSV)  # 将图片转换到HSV空间
        if FLAG==3 or FLAG==8 or FLAG==13:
            color_range_lower = color_range['green_bridge_1'][0]
            color_range_upper = color_range['green_bridge_1'][1]
        if FLAG==2 or FLAG==7 or FLAG==12:
            color_range_lower = color_range['blue_bridge_1'][0]
            color_range_upper = color_range['blue_bridge_1'][1]
        Chest_frame_green = cv2.inRange(Chest_frame_hsv, color_range_lower,
                                        color_range_upper)  # 对原图像和掩模(颜色的字典)进行位运算
        '''if is_enter:
            Chest_frame_green = cv2.inRange(Chest_frame_hsv, color_range['green_bridge_2'][0],
                                        color_range['green_bridge_2'][1])  # 对原图像和掩模(颜色的字典)进行位运算
        else:
            Chest_frame_green = cv2.inRange(Chest_frame_hsv, color_range['green_bridge_1'][0],
                                        color_range['green_bridge_1'][1]) ''' # 对原图像和掩模(颜色的字典)进行位运算

        '''Chest_frame_green = cv2.inRange(Chest_frame_hsv, color_range['blue_bridge_1'][0],
                                        color_range['blue_bridge_1'][1])'''  # 对原图像和掩模(颜色的字典)进行位运算
        
#         cv2.imshow('4', Chest_frame_green)
        Chest_opened_green = cv2.morphologyEx(Chest_frame_green, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))  # 开运算 去噪点
        Chest_closed_green = cv2.morphologyEx(Chest_opened_green, cv2.MORPH_CLOSE,
                                              np.ones((3, 3), np.uint8))  # 闭运算 封闭连接

        (Chest_contours_green, hierarchy_green) = cv2.findContours(Chest_closed_green, cv2.RETR_LIST,
                                                                   cv2.CHAIN_APPROX_NONE)  # 找出轮廓cv2.CHAIN_APPROX_NONE
        Chest_areaMaxContour_green, Chest_area_max_green = getAreaMaxContour1(Chest_contours_green)  # 找出最大轮廓
        Chest_percent_green = round(Chest_area_max_green * 100 / (r_w * r_h), 2)

        Chest_areaMaxContour = Chest_areaMaxContour_green
        Chest_contours = Chest_contours_green
        Chest_percent = Chest_percent_green
        if Chest_areaMaxContour is not None:
            Chest_rect = cv2.minAreaRect(Chest_areaMaxContour)
            # center, w_h, Head_angle = rect  # 中心点 宽高 旋转角度
            Chest_box = np.int0(cv2.boxPoints(Chest_rect))  # 点的坐标

            # 初始化四个顶点坐标
            Chest_top_left = Chest_areaMaxContour[0][0]
            Chest_top_right = Chest_areaMaxContour[0][0]
            Chest_bottom_left = Chest_areaMaxContour[0][0]
            Chest_bottom_right = Chest_areaMaxContour[0][0]
            for c in Chest_areaMaxContour:  # 遍历找到四个顶点
                if c[0][0] + 1.5 * c[0][1] < Chest_top_left[0] + 1.5 * Chest_top_left[1]:
                    Chest_top_left = c[0]
                if (r_w - c[0][0]) + 1.5 * c[0][1] < (r_w - Chest_top_right[0]) + 1.5 * Chest_top_right[1]:
                    Chest_top_right = c[0]
                if c[0][0] + 1.5 * (r_h - c[0][1]) < Chest_bottom_left[0] + 1.5 * (r_h - Chest_bottom_left[1]):
                    Chest_bottom_left = c[0]
                if c[0][0] + 1.5 * c[0][1] > Chest_bottom_right[0] + 1.5 * Chest_bottom_right[1]:
                    Chest_bottom_right = c[0]
            angle_top = - math.atan(
                (Chest_top_right[1] - Chest_top_left[1]) / (Chest_top_right[0] - Chest_top_left[0])) * 180.0 / math.pi
            angle_bottom = - math.atan((Chest_bottom_right[1] - Chest_bottom_left[1]) / (
                    Chest_bottom_right[0] - Chest_bottom_left[0])) * 180.0 / math.pi
            Chest_top_center_x = int((Chest_top_right[0] + Chest_top_left[0]) / 2)
            Chest_top_center_y = int((Chest_top_right[1] + Chest_top_left[1]) / 2)
            Chest_bottom_center_x = int((Chest_bottom_right[0] + Chest_bottom_left[0]) / 2)
            Chest_bottom_center_y = int((Chest_bottom_right[1] + Chest_bottom_left[1]) / 2)
            Chest_center_x = int((Chest_top_center_x + Chest_bottom_center_x) / 2)
            Chest_center_y = int((Chest_top_center_y + Chest_bottom_center_y) / 2)
            if math.fabs(Chest_top_right[1] - Chest_top_left[1]) < 2:
                angle_top = 90
            else:
                angle_top = math.atan((Chest_top_right[0] - Chest_top_left[0]) / (
                            Chest_top_right[1] - Chest_top_left[1])) * 180.0 / math.pi
            if math.fabs(Chest_bottom_right[1] - Chest_bottom_left[1]) < 2:
                angle_bottom = 90
            else:
                angle_bottom = math.atan((Chest_bottom_right[0] - Chest_bottom_left[0]) / (
                            Chest_bottom_right[1] - Chest_bottom_left[1])) * 180.0 / math.pi
            if img_debug:
                cv2.drawContours(Chest_img_copy, [Chest_box], 0, (0, 0, 255), 2)  # 将大矩形画在图上
                cv2.circle(Chest_img_copy, (Chest_top_right[0], Chest_top_right[1]), 5, [0, 255, 255], 2)
                cv2.circle(Chest_img_copy, (Chest_top_left[0], Chest_top_left[1]), 5, [0, 255, 255], 2)
                cv2.circle(Chest_img_copy, (Chest_bottom_right[0], Chest_bottom_right[1]), 5, [0, 255, 255], 2)
                cv2.circle(Chest_img_copy, (Chest_bottom_left[0], Chest_bottom_left[1]), 5, [0, 255, 255], 2)
                cv2.circle(Chest_img_copy, (Chest_top_center_x, Chest_top_center_y), 5, [0, 255, 255], 2)
                cv2.circle(Chest_img_copy, (Chest_bottom_center_x, Chest_bottom_center_y), 5, [0, 255, 255], 2)
                cv2.circle(Chest_img_copy, (Chest_center_x, Chest_center_y), 7, [255, 255, 255], 2)
                cv2.line(Chest_img_copy, (Chest_top_center_x, Chest_top_center_y),
                         (Chest_bottom_center_x, Chest_bottom_center_y), [0, 255, 255], 2)

                cv2.drawContours(Chest_img_copy, Chest_contours, -1, (255, 0, 255), 1)
                cv2.putText(Chest_img_copy,
                            "bottom_right:" + str(int(Chest_bottom_right[0])) + ',' + str(int(Chest_bottom_right[1])),
                            (30, 200),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 2)
                cv2.putText(Chest_img_copy,
                            "bottom_left:" + str(int(Chest_bottom_left[0])) + ',' + str(int(Chest_bottom_left[1])),
                            (30, 220),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 2)
                cv2.putText(Chest_img_copy,
                            "top_right:" + str(int(Chest_top_right[0])) + ',' + str(int(Chest_top_right[1])),
                            (30, 240),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 2)

                cv2.putText(Chest_img_copy, "angle_top:" + str(int(angle_top)), (30, 260), cv2.FONT_HERSHEY_SIMPLEX,
                            0.65,
                            (0, 0, 0), 2)
                cv2.putText(Chest_img_copy, "angle_bottom:" + str(int(angle_bottom)), (30, 280),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.65,
                            (0, 0, 0), 2)
                cv2.imshow('Chest', Chest_img_copy)
                k = cv2.waitKey(1)
                if k == ord('w') & 0xff:
                    break

            if 1:
                print('step:', step)
                #后退，识别底线
                if step == 0:
                    step = 1
                    '''if Chest_bottom_left[1] < 550 or Chest_bottom_right[1] < 550:
                        step = 1
                        continue
                    else:
                        action_append("Back0Run")'''
                #根据底线角度调整方向
                elif step == 1:
                    if 0 < angle_bottom < 87:
                        action_append('turn001R')
                        print('angle_bottom:', angle_bottom)
                    elif -87 < angle_bottom < 0:
                        action_append('turn001L')
                        print('angle_bottom:', angle_bottom)
                    else:
                        step = 2
                        is_enter = True
                        
                        '''if Chest_bottom_left[1] > 615 or Chest_bottom_right[1] > 615:
                            step = 2
                            is_enter = True
                            continue
                        action_append("forwardSlow0403")
                        action_append("forwardSlow0403")
                        #action_append("Stand")'''
                #右移
                elif step == 2:
                    if 0 < angle_top < 87:
                        action_append('turn001R')
                        print('angle_top:', angle_top)
                    elif -87 < angle_top < 0:
                        action_append('turn001L')
                        print('angle_top:', angle_top)
                    else:
                        if Chest_bottom_right[0]  < 450:
                            step = 3
                            
                            continue
                        action_append("Right02move")
                        time.sleep(1)
                        action_append("Right02move")

                #前进
                elif step == 3:
                    if Chest_top_right[1] > 460:
                            step = 4
                            continue
                    elif 0 < angle_top < 88:
                        action_append('turn001R')
                        print('angle_top:', angle_top)
                    elif -88 < angle_top < 0:
                        action_append('turn001L')
                        print('angle_top:', angle_top)
                    else:
                        if Chest_top_right[1] > 460:
                            step = 4
                            continue
                        elif Chest_bottom_right[0] < 310:
                            action_append('Left02move')
                        elif Chest_bottom_right[0] > 385:
                            action_append('Right02move')
                        else:
                            
                            action_append('forwardSlow0403')
                            #time.sleep(2)
                            action_append('forwardSlow0403')
                            #time.sleep(2)
                            action_append('Stand')
                            #action_append('forwardSlow0403')
                #左移
                elif step == 4:
                    '''if 0 < angle_top < 87:
                        action_append('turn001R')
                    elif -87 < angle_top < 0:
                        action_append('turn001L')
                    else:
                        if Chest_bottom_right[0] < 310:
                            action_append('Left02move')
                        elif Chest_bottom_right[0] > 385:
                            action_append('Right02move')
                        else:'''
                    action_append('Left02move')
                    time.sleep(0.5)
                    action_append('Left02move')
                    time.sleep(0.5)
                    action_append('Left02move')
                    time.sleep(0.5)
                    action_append('Left02move')
                    time.sleep(0.5)
                    action_append('Left02move')
                    time.sleep(0.5)
                    action_append('turn001L')
                    time.sleep(0.5)
                    action_append('Left02move')
                    time.sleep(0.5)
                    action_append('Left02move')
                    time.sleep(0.5)
                    action_append('Left02move')
                    time.sleep(0.5)
                    action_append('Left02move')
                    time.sleep(0.5)
                    action_append('Left02move')
                    time.sleep(0.5)
                    action_append('turn001L')
                    time.sleep(0.5)
                    action_append('Left02move')
                    time.sleep(0.5)
                    
                    step = 5
                else:
                    break
        else:
            continue

        
#################################################5：过楼梯##########################################
def getAreaMaxContour_stair(contours):
    r_w = 480
    r_h = 480
    contour_area_temp = 0
    contour_area_max = 0
    area_max_contour = None

    for con in contours:  # 历遍所有轮廓
        contour_area_temp = math.fabs(cv2.contourArea(con))  # 计算轮廓面积
        # print(math.fabs(cv2.contourArea(con)))
        if contour_area_temp > 25:
            if contour_area_temp >= contour_area_max:
                contour_area_max = contour_area_temp
                area_max_contour = con

    top_right = area_max_contour[0][0]
    top_left = area_max_contour[0][0]
    bottom_right = area_max_contour[0][0]
    bottom_left = area_max_contour[0][0]

    for c in area_max_contour:
        if c[0][0] + 1.5 * c[0][1] < top_left[0] + 1.5 * top_left[1]:
            top_left = c[0]
        if (r_w - c[0][0]) + 1.5 * c[0][1] < (r_w - top_right[0]) + 1.5 * top_right[1]:
            top_right = c[0]
        if c[0][0] + 0.5 * (r_h - c[0][1]) < bottom_left[0] + 0.5 * (r_h - bottom_left[1]):
            bottom_left = c[0]
        if c[0][0] + 0.5 * c[0][1] > bottom_right[0] + 0.5 * bottom_right[1]:
            bottom_right = c[0]

    box_rect_max = [top_left, top_right, bottom_right, bottom_left]

    return contour_area_max, area_max_contour, box_rect_max  # 返回最大的轮廓廓

def pass_staircase():
    
    global state,state_sel,ChestOrg_img
    step_color = 0 # 0：识别蓝色；1：识别绿色；2：识别红色
    step_stair_flag = 0 # 进入第几阶段
    j = 0

    while True:

        if ChestOrg_img is None:
            continue
        ChestOrg = ChestOrg_img.copy()
        ChestOrg = np.rot90(ChestOrg)
        ChestOrg_90 = ChestOrg[160:,:,:]
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
        
        if contours == None:
            action_append("turn005L")
            continue
        
        max_area, max_contour, max_box= getAreaMaxContour_stair(contours)

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
        cv2.putText(ChestOrg_draw, "Chest_top_center_x:" + str(int(Chest_top_center_x)), (30, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255, 255, 255), 2)    
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
                    action_append("Forwalk02")
                    time.sleep(1)
                    action_append("UpBridge")
                    action_append("Stand")
                    action_append("Forwalk02")
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
                    break
                elif Chest_top_center_x > 240:
                    print("往右一点点")
                    action_append("Right02move")
                else:
                    print("往左一点点")
                    action_append("Left02move")         #左右调整


#################################################6：踢球##########################################
hole_x = 0
hole_y = 0
ball_x = 0
ball_y = 0


def act_move():
    global step, angle, chest
    global hole_Angle, ball_hole
    global golf_angle_ball, golf_angle, ball_angle, Chest_golf_angle
    global hole_x, hole_y, ball_x, ball_y
    global golf_angle_flag, golf_dis_flag  # golf_dis_flag未使用
    global golf_angle_start, golf_dis_start
    global golf_ok
    global hole_flag, Chest_ball_flag, angle_flag
    global ball_dis_start, hole_angle_start
    global head_state, angle_dis_count
    ball_hole_angle_ok = False

    if True:
        if step == 0:  # 发现球,前进到球跟前

            if Chest_ball_flag == True:
                if ball_y <= 300:  # 340
                    print("step0 ball_y <= 300, forwardSlow0403  ", ball_y)
                    # action_append("forwardSlow0403")
                    # action_append("forwardSlow0403")
                    action_append("forwardSlow0403")
                elif 300 < ball_y < 340:

                    if ball_x > 340:
                        action_append("Right02move")
                        print('ball_x>340 Right02move', ball_x)
                    elif ball_x < 160:  # 240 - 100

                        print("ball_x <160 Left02move ", ball_x)
                        action_append("Left02move")
                    else:
                        print(" 160<ball_x<340 Forwalk01 ", ball_x)
                        action_append("Forwalk01")

                else:  # ball_y>340

                    if ball_x < 160:  # 240 - 100
                        print("ball_x < 160 Left02move ", ball_x)
                        action_append("Left02move")
                    elif ball_x > 340:  # 240 + 100
                        print("ball_x > 340 Right02move ", ball_x)
                        action_append("Right02move")

                    else:
                        print("from step 0 go to step 1")
                        cv2.imwrite('0->1.jpg', chest)
                        step = 1
            else:
                print(" 未发现白球  左右旋转头部摄像头 寻找白球")
                print(" step0 Forwalk01")
                action_append("Forwalk01")


        elif step == 1:  # ball_y>340, 160<ball_x<340
            if ball_y <= 340:
                print("step1 ball_y< 340 Forwalk01", ball_y)
                action_append("Forwalk01")
            elif ball_y > 420:
                print("step1 ball_y> 420 Back2Run", ball_y)
                action_append("Back2Run")
            elif 340 <= ball_y <= 420:

                if angle_flag == True:
                    if angle < 75 and angle > 0:
                        print("洞在球右边")
                        print('from step 1 go to step 2')
                        cv2.imwrite('1->2.jpg', chest)
                        step = 2
                        # print("172L 头恢复0 向右平移")
                        # head_state = 0
                    elif angle > -80 and angle < 0:
                        print("洞在球左边")
                        print('from step 1 go to step 3')
                        cv2.imwrite('1->3.jpg', chest)
                        step = 3
                        # print("172L 头恢复0 向左平移")
                        # head_state = 0
                    elif angle > 75 or angle < -80:  # 头前看 看到球洞
                        print("洞基本处于球正前方")
                        print('from step 1 go to step 4')
                        cv2.imwrite('1->4.jpg', chest)
                        step = 4
                else:
                    print("step1找不到angle Forwalk00")
                    action_append('Forwalk00')
                    # 目前假设球洞在前方，head能看到

                    # if head_state == 0:
                    #     print("头右转(-60)寻找球")
                    #     head_state = -60
                    # elif head_state == -60:
                    #     print("头由右转变为左转(+60)寻找球")
                    #     head_state = 60
                    # elif head_state == 60:
                    #     print("头部 恢复0 向前迈进")

        elif step == 2:  # 0<angle<75 洞在球右边 340< ball_y <= 420 160< ball_x < 360
            if ball_y < 370:
                action_append("Forwalk01")
                print('step2, ball_y<370 Forwalk01', ball_y)
            elif ball_y > 460:
                action_append("Back2Run")
                print('step2, ball_y>460 Back1Run', ball_y)
            elif 370 <= ball_y <= 460:
                # 粗调水平位置
                if ball_x < 150:
                    action_append('Left02move')
                    print('step2, 370<= ball_y <= 460 ball_x<150 Left02move', ball_x)
                elif ball_x > 300:
                    action_append('Right02move')
                    print('step2, 370<= ball_y <= 460 ball_x>300 Right02move', ball_x)
                elif 150 < ball_x < 300:

                    if angle_flag == True:
                        # 调整球坑之间角度
                        if 0 < angle < 60:
                            action_append('turn001R')
                            print('step2 0<angle<60 turn001R', angle)
                        elif 60 < angle < 75:
                            action_append('turn001R')
                            print('step2 angle>60 turn001R', angle)
                        elif angle > 75 or angle < -80:
                            # 进一步调整 球水平位置
                            if ball_x < 170:
                                action_append('Left02move')
                                print('step2 angle>75 or angle<-80 ball_x<170 Left02move', ball_x)
                            elif ball_x > 280:
                                action_append('Right02move')
                                print('step2 angle>75 or angle<-80 ball_x>280 Right02move', ball_x)
                            else:
                                print('from step 2 go to step 5')
                                cv2.imwrite('2->5.jpg', chest)
                                step = 5

                        elif -80 < angle < -60:
                            action_append('turn001L')
                            print('step2 -80<angle<-60 turn001L', angle)

                        else:
                            print('from step 2 go to step 3')
                            cv2.imwrite('2->3.jpg', chest)
                            step = 3

                    else:
                        print('step2找不到angle')
                        action_append('Stand')
                        # action_append('Forwalk00')


        elif step == 3:  # -80<angle<0 洞在球左边 340< ball_y <= 420 160< ball_x < 360
            if ball_y < 370:
                action_append("Forwalk01")
                print('step3 ball_y<370 Forwalk01', ball_y)
            elif ball_y > 460:
                action_append("Back1Run")
                print('step3 ball_y>460 Back1Run', ball_y)

            elif 370 <= ball_y <= 460:
                # 粗调水平位置
                if ball_x < 150:
                    action_append('Left02move')
                    print('step3 370<= ball_y <= 460 ball_x<180 Left02move', ball_x)

                elif ball_x > 300:
                    action_append('Right02move')
                    print('step3 370<= ball_y <= 460 ball_x>300 Right02move', ball_x)

                elif 150 < ball_x < 300:
                    # 调整球和坑之间角度
                    if angle_flag == True:

                        if -60 < angle < 0:
                            action_append('turn001L')
                            print('step3 180<ball_x<300 -60<angle<0 turn001L', angle)

                        elif -80 < angle < -60:
                            action_append('turn001L')
                            print('step3 180<ball_x<300 -80<angle<-60 turn001L', angle)

                        elif angle > 75 or angle < -80:
                            # 进一步调整球水平位置
                            if ball_x < 170:
                                action_append('Left02move')
                                print('step3 angle>75 or angle<-80 ball_x<170 Left02move', ball_x)
                            elif ball_x > 280:
                                action_append('Right02move')
                                print('step3 angle>75 or angle<-80 ball_x>280 Left02move', ball_x)
                            else:
                                print('from step 3 go to step 5')
                                cv2.imwrite('3->5.jpg', chest)
                                step = 5

                        elif 60 < angle < 75:
                            action_append('turn001R')
                            print('step3 60<angle<75 turn001R', angle)

                        else:
                            print('from step 3 go to step 2')
                            cv2.imwrite('3->2.jpg', chest)
                            step = 2

                    else:
                        print('step3找不到angle')
                        action_append('Stand')
                        # action_append('Forwalk00')



        elif step == 4:  # angle>75 or angle<-80 洞在球前方 340< ball_y <= 420 160< ball_x < 360
            if ball_y < 370:
                action_append("Forwalk01")
                print('step4 ball_y<370 Forwalk01', ball_y)

            elif ball_y > 460:
                action_append("Back1Run")
                print('step4 ball_y>460 Back1Run', ball_y)

            elif 370 <= ball_y <= 460:
                # 粗调水平位置
                if ball_x < 170:
                    action_append('Left02move')
                    print('step4 370<= ball_y <= 460 ball_x<170 Left02move', ball_x)

                elif ball_x > 280:
                    action_append('Right02move')
                    print('step4 370<= ball_y <= 460 ball_x>280 Right02move', ball_x)

                elif 170 < ball_x < 280:

                    if angle_flag == True:

                        if 0 < angle < 75:
                            print('from step 4 go to step 2', angle)
                            cv2.imwrite('4->2.jpg', chest)
                            step = 2
                        elif -80 < angle < 0:
                            print('from step 4 go to step 3', angle)
                            cv2.imwrite('4->3.jpg', chest)
                            step = 3
                        elif angle > 75 or angle < -80:
                            step = 5
                            print('from step 4 go to step 5', angle)
                            cv2.imshow('4->5.jpg', chest)
                    else:
                        print('step4找不到hole')
                        action_append('Stand')
                        # action_append('Forwalk00')


        elif step == 5:  # angle>75 or angle<-80 洞在球前方 370< ball_y <= 450 200< ball_x < 280
            if ball_y < 410:
                action_append('Forwalk00')
                print('step5 ball_y<410 Forwalk00', ball_y)
            elif ball_y > 480:
                action_append('Back2Run')
                print('step5 ball_y>480 Back1Run', ball_y)
            elif 410 < ball_y < 480:
                if ball_x > 240:
                    action_append('Right02move')
                    print('step5 410<ball_y<470 ball_x>240 Right1move', ball_x)
                elif ball_x < 180:
                    action_append('Left02move')
                    print('step5 410<ball_y<470 ball_x<180 Left1move', ball_x)
                elif 180 < ball_x < 240:

                    if angle_flag == True:

                        if angle > 75 or angle < -88:
                            step = 6
                            print('from step5 go to step6', angle)
                            cv2.imwrite('5->6.jpg', chest)
                        elif 60 < angle < 75:
                            action_append('turn001R')
                            print('step5 200<ball_x<240 65<angle<75 turn001R', angle)
                        elif 0 < angle < 60:
                            action_append('turn001R')
                            print('step5 200<ball_x<240 0<angle<65 turn001R', angle)
                        elif -88 < angle < -70:
                            action_append('turn001L')
                            print('step5 200<ball_x<240 -88<angle<-70 turn001L', angle)
                        elif -70 < angle < 0:
                            action_append('turn001L')
                            print('step5 200<ball_x<240 -70<angle<0 turn001L', angle)
                    else:
                        print('step5找不到angle')
                        action_append('Stand')

        elif step == 6:  # angle>78 or angle<-86.5 洞在球前方 410< ball_y <= 460 200< ball_x < 240
            if ball_y < 430:
                action_append('Forwalk00')
                print('step6 ball_y<430 Forwalk00', ball_y)
            elif ball_y > 480:
                action_append('Back2Run')
                print('step6 ball_y>480 Back1Run', ball_y)
            elif 430 < ball_y < 480:
                if ball_x > 220:
                    action_append('Right1move')
                    print('step6 420<ball_y<480 ball_x>220 Right1move', ball_x)
                elif ball_x < 200:
                    action_append('Left1move')
                    print('step6 420<ball_y<480 ball_x<200 Left1move', ball_x)
                elif 200 < ball_x < 220:

                    if angle_flag == True:

                        if angle > 78 and angle < 87 :
                            step = 7
                            print('from step6 go to step7', angle)
                            cv2.imwrite('6->7.jpg', chest)
                        elif 60 < angle < 78:
                            action_append('turn001R')
                            print('step6 200<ball_x<220 60<angle<78 turn001R', angle)
                        elif 0 < angle < 60:
                            action_append('turn001R')
                            print('step6 200<ball_x<220 0<angle<60 turn001R', angle)
                        elif angle < -75 or angle>87 :
                            action_append('turn001L')
                            print('step6 200<ball_x<220 angle < -75 or angle>86 turn001L', angle)
                        elif -75 < angle < 0:
                            action_append('turn001L')
                            print('step6 200<ball_x<220 -75<angle<0 turn001L', angle)
                    else:
                        print('step6找不到angle')
                        action_append('Stand')

        elif step == 7:  # angle>85 or angle<-85 洞在球前方 420< ball_y <= 460 210< ball_x < 230
            print('位置已找好')
            action_append('LfootShot')
            step = 8
            #cv2.waitKey(0)


def kick_ball():
    global step, chest
    global hole_Angle, ball_angle, angle
    global golf_angle_ball, golf_angle , Chest_golf_angle
    global hole_x, hole_y, ball_x, ball_y
    global hole_flag ,Chest_ball_flag, angle_flag
    global ChestOrg_img
    global picnum,debug_pic


    step = 0
    model = models.load_model('./config/yolov3-tiny-custom.cfg',
                          'best.weights')
    i = 50


    while True:
        if 0<=step <= 7: #踢球的六步

            hole = None
            ball = None

            ChestOrg = ChestOrg_img.copy()
            ChestOrg = np.rot90(ChestOrg)

            chest = ChestOrg.copy()

            img_h, img_w = chest.shape[:2]

            # 把上中心点和下中心点200改为640/2  fftest
            bottom_center = (int(img_w/2), int(img_h))  #图像底中点
            top_center = (int(img_w/2), int(0))     #图像顶中点
            # bottom_center = (int(640/2), int(img_h))  #图像底中点
            # top_center = (int(640/2), int(0))     #图像顶中点

            chest_RGB = cv2.cvtColor(chest, cv2.COLOR_BGR2RGB)
            
            chest_RGB[580:640,:,0] = 139
            chest_RGB[580:640,:,1] = 77
            chest_RGB[580:640,:,2] = 88
            

            boxes = detect.detect_image(model, chest_RGB, conf_thres=0.1)

            for box in boxes:
                x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])
                cv2.rectangle(chest, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)
                cv2.putText(chest, str(box[5]) + '_' + str(box[4]), (int(x1), int(y1 - 10)), cv2.FONT_HERSHEY_COMPLEX, 1,
                            (0, 255, 0), 3)

            for box in boxes:
                if box[5]==1:
                    hole = box

            if hole is not None:

                hole_flag = True
                hole_x = int((hole[0]+hole[2])/2)
                hole_y = int((hole[1]+hole[3])/2)
                cv2.putText(chest, '('+str(hole_x) + ',' + str(hole_y)+')', (int(hole_x-20), hole_y), cv2.FONT_HERSHEY_COMPLEX, 1,
                            (0, 255, 0), 1)

                if (hole_x - bottom_center[0]) == 0:
                    hole_Angle = 90
                else:
                # hole_Angle  (y1-y0)/(x1-x0)
                    hole_Angle = - math.atan(
                        (hole_y - bottom_center[1]) / (hole_x - bottom_center[0])) * 180.0 / math.pi
            else:
                hole_flag = False
                print("没有找到洞")
                i = i+1
                #cv2.imwrite('./not_found_pic/not_found_'+str(i)+'.jpg', chest)


            for box in boxes:
                if box[5]==0:
                    ball = box

            if ball is not None:

                Chest_ball_flag = True

                ball_x = int((ball[0]+ball[2])/2)
                ball_y = int((ball[1]+ball[3])/2)

                cv2.putText(chest, '(' + str(ball_x) + ',' + str(ball_y) + ')', (int(ball_x - 20), ball_y),
                            cv2.FONT_HERSHEY_COMPLEX, 1,(0, 255, 0), 1)

                if (ball_x- top_center[0])==0:
                    ball_angle = 90
                else:
                    ball_angle = - math.atan((ball_y - top_center[1]) / (
                                ball_x - top_center[0])) * 180.0 / math.pi

            else:
                Chest_ball_flag = False
                i = i+1
                #cv2.imwrite('./not_found_pic/not_found_'+str(i)+'.jpg', chest)

            if len(boxes) == 2:
                angle_flag = True

                if hole_x != ball_x:
                    angle = - math.atan(
                        (hole_y - ball_y) / (hole_x - ball_x)) * 180.0 / math.pi
                else:
                    angle = 90
                cv2.putText(chest, str(angle), (int(240), 30),
                            cv2.FONT_HERSHEY_COMPLEX, 1,(0, 255, 0), 3)
            if debug:

                cv2.imshow('chest', chest)
                cv2.waitKey(1)

            act_move()
        else:
            print('踢球完成')
            for i in range(3):
                action_append('turn005L')


            action_append('fastForward03')

            break


#################################################过最后的横杆##########################################
def pass_end_bar():
    global ChestOrg_img, step, img_debug

    step = 0

    while True:
        if step == 0:  # 判断门是否抬起
            t1 = cv2.getTickCount()  # 时间计算
            org_img_copy = ChestOrg_img.copy()
            org_img_copy = np.rot90(org_img_copy)
            handling = org_img_copy.copy()

            handling_cut = handling[:,100:380, :]

            # border = cv2.copyMakeBorder(handling_cut, 12, 12, 16, 16, borderType=cv2.BORDER_CONSTANT,
            #                            value=(255, 255, 255))  # 扩展白边，防止边界无法识别
            # handling_cut= cv2.resize(border, (chest_r_width, chest_r_height), interpolation=cv2.INTER_CUBIC)  # 将图片缩放
            frame_gauss = cv2.GaussianBlur(handling_cut, (21, 21), 0)  # 高斯模糊
            frame_hsv = cv2.cvtColor(frame_gauss, cv2.COLOR_BGR2HSV)  # 将图片转换到HSV空间

            frame_door_yellow = cv2.inRange(frame_hsv, color_range['yellow_door'][0],
                                            color_range['yellow_door'][1])  # 对原图像和掩模(颜色的字典)进行位运算
            #frame_door_black = cv2.inRange(frame_hsv, color_range['black_door'][0],
            #                               color_range['black_door'][1])  # 对原图像和掩模(颜色的字典)进行位运算

            frame_door =frame_door_yellow
            open_pic = cv2.morphologyEx(frame_door, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))  # 开运算 去噪点
            closed_pic = cv2.morphologyEx(open_pic, cv2.MORPH_CLOSE, np.ones((50, 50), np.uint8))  # 闭运算 封闭连接
            # print(closed_pic)

            (contours, hierarchy) = cv2.findContours(closed_pic, cv2.RETR_EXTERNAL,
                                                            cv2.CHAIN_APPROX_NONE)  # 找出轮廓
            areaMaxContour, area_max = getAreaMaxContour(contours)  # 找出最大轮廓
            percent = round(100 * area_max / (chest_r_width * chest_r_height), 2)  # 最大轮廓的百分比
            percent_cut = round(100 * area_max / (320 * chest_r_height), 2)
            if areaMaxContour is not None:
                rect = cv2.minAreaRect(areaMaxContour)  # 矩形框选
                box = np.int0(cv2.boxPoints(rect))  # 点的坐标
                if img_debug:
                    cv2.drawContours(handling_cut, [box], 0, (153, 200, 0), 2)  # 将最小外接矩形画在图上
                    cv2.drawContours(handling, [box], 0, (153, 200, 0), 2)
            if debug:
                cv2.putText(handling_cut, 'area: ' + str(percent_cut) + '%', (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                            (0, 0, 255), 2)
                cv2.putText(handling, 'area: ' + str(percent) + '%', (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                            (0, 0, 255), 2)
                t2 = cv2.getTickCount()
                time_r = (t2 - t1) / cv2.getTickFrequency()
                fps = 1.0 / time_r
                cv2.putText(handling, "fps:" + str(int(fps)), (30, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)
                cv2.imshow('handling', handling)  # 显示图像
                cv2.imshow('handling_cut', handling_cut)

                cv2.imshow('frame_door_yellow', frame_door_yellow)  # 显示图像
                #cv2.imshow('frame_door_black', frame_door_black)  # 显示图像
                cv2.imshow('closed_pic', closed_pic)  # 显示图像

                k = cv2.waitKey(10)
                if k == 27:
                    cv2.destroyWindow('closed_pic')
                    cv2.destroyWindow('handling')
                    cv2.destroyWindow('handling_cut')
                    break
                elif k == ord('s'):
                    print("save picture")
                    cv2.imwrite("picture.jpg", org_img_copy)  # 保存图片

            # 根据比例得到是否前进的信息
            if percent_cut > 8:  # 检测到横杆
                print(percent, "%")
                print("有障碍 等待 contours len：", len(contours))
                time.sleep(0.1)
            else:
                print(percent)

                print("231L 执行7步")

                
                action_append("fastForward07")

                step = 1

        elif step == 1:  # 寻找下一关卡

            action_append("Stand")

            step = 0

            break
    pass





if __name__ == '__main__':
    #while len(CMDcontrol.action_list) > 0:
    #    print("等待启动")
    #    time.sleep(1)
    action_append("HeadTurnMM")
    hole_flag = False
    bridge_flag = False
    '''
    while True:
        if ChestOrg_img is not None and chest_ret:

            img = ChestOrg_img.copy()
            img = np.rot90(img)
            img = img[160:,:,:]
            cv2.imshow('img', img)
            cv2.waitKey(0)

            break
        else:
            print('image is empty :', chest_ret)
            time.sleep(0.01)
    '''
    
    detector = Detector('small', num_classes=15)
    
    while True:
        if ChestOrg_img is not None and chest_ret:

            pass_start_bar()

            break
        else:
            print('image is empty :', chest_ret)
            time.sleep(0.01)
    
    
    while True:
        if ChestOrg_img is not None and chest_ret:
            
            chest = ChestOrg_img.copy()
            chest = np.rot90(chest)
            chest = chest[160:,:,:]
            

            FLAG = detector.detect('best.pkl', chest)
            print(FLAG)
            #cv2.imshow('chest', chest)
            #cv2.waitKey(0)
            if FLAG==0 or FLAG==1 or FLAG==5 or FLAG==6 or FLAG==10 or FLAG==11:
                pass_bridge()
                bridge_hole = True
                break
            elif FLAG== 2 or FLAG==3 or FLAG==7 or FLAG==8 or FLAG==12 or FLAG==13:
                pass_hole()
                hole_flag = True
                break
            else:
                pass_staircase()
                break
            
            pass_hole()
        else:
            print('image is empty :', chest_ret)
            time.sleep(0.01)
    
    
    while True:
        if ChestOrg_img is not None and chest_ret:

            pass_landmine()

            break
        else:
            print('image is empty :', chest_ret)
            time.sleep(0.01)
    
    
    while True:
        if ChestOrg_img is not None and chest_ret:

            pass_obstacle()

            break
        else:
            print('image is empty :', chest_ret)
            time.sleep(0.01)
    
    while True:
        if ChestOrg_img is not None and chest_ret:
            
            action_append("Back2Run")
            action_append("Back2Run")
            time.sleep(0.5)
            action_append("turn010L")
            pass_door()

            break
        else:
            print('image is empty :', chest_ret)
            time.sleep(0.01)
    
    while True:
        if ChestOrg_img is not None and chest_ret:
            
            chest = ChestOrg_img.copy()
            chest = np.rot90(chest)
            chest = chest[160:, :,:]
            

            FLAG = detector.detect('best.pkl', chest)
            #FLAG = 6
            print(FLAG)
            if FLAG==0 or FLAG==1 or FLAG==5 or FLAG==6 or FLAG==10 or FLAG==11:
                if bridge_flag:
                    pass_hole()
                    break
                else:
                    pass_bridge()
                    break
            elif FLAG== 2 or FLAG==3 or FLAG==7 or FLAG==8 or FLAG==12 or FLAG==13:
                if hole_flag:
                    pass_bridge()
                    break
                else:
                    pass_hole()
                    break
            else:
                pass_staircase()
                break
            
#             pass_bridge()
           # break
        else:
            print('image is empty :', chest_ret)
            time.sleep(0.01)
    

    while True:
        if ChestOrg_img is not None and chest_ret:
            if FLAG==4 or FLAG==9 or FLAG==14:
                pass
            else:
                action_append('fastForward04')
            kick_ball()

            break
        else:
            print('image is empty :', chest_ret)
            time.sleep(0.01)

    

    while True:
        if ChestOrg_img is not None and chest_ret:
            
            chest = ChestOrg_img.copy()
            chest = np.rot90(chest)
            chest = chest[160:,:,:]
            

            FLAG = detector.detect('best.pkl', chest)
            print(FLAG)
            if FLAG==0 or FLAG==1 or FLAG==5 or FLAG==6 or FLAG==10 or FLAG==11:
                pass_bridge()
                break
            elif FLAG== 2 or FLAG==3 or FLAG==7 or FLAG==8 or FLAG==12 or FLAG==13:
                pass_hole()
                break
            else:
                pass_staircase()
                break
            
            pass_staircase()
            break
        else:
            print('image is empty :', chest_ret)
            time.sleep(0.01)
    
    pass_staircase()
    action_append('fastForward05')
    
    while True:
        if ChestOrg_img is not None and chest_ret:

            pass_end_bar()

            break
        else:
            print('image is empty :', chest_ret)
            time.sleep(0.01)
            cv2.destroyAllWindows()

    while (1):
        print("结束")
        time.sleep(10000)



