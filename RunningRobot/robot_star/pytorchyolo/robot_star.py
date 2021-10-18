#!/usr/bin/env python3
# coding:utf-8
import sys
sys.path.append('./mobilenet')


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
camera_out = "chest"
#stream_head = "http://192.168.3.29:8082/?action=stream?dummy=param.mjpg"
cap_head = cv2.VideoCapture(2)
#stream_chest = "http://192.168.3.29:8080/?action=stream?dummy=param.mjpg"
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
    'yellow_door': [(20, 100, 60), (50, 240, 170)],
    'black_door': [(25, 25, 10), (110, 150, 50)],
    'black_gap': [(0, 0, 0), (180, 255, 70)],

    'yellow_hole': [(25, 90, 70), (40, 255, 255)],
    'black_hole': [(10, 10, 10), (180, 190, 60)],

    'chest_red_floor': [(0, 40, 60), (20, 200, 190)],
    'chest_red_floor1': [(0, 100, 60), (20, 200, 210)],
    'chest_red_floor2': [(110, 100, 60), (180, 200, 210)],

    'blue': {'Lower': np.array([100, 80, 46]), 'Upper': np.array([124, 255, 255])},

    'green_bridge_1': [(35, 43, 46), (80, 255, 255)],
    'blue_bridge_1': [(78, 43, 46), (124, 255, 255)],
    'green_bridge':[(45, 75, 40), (90, 255, 210)]
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
            if percent_cut > 5:  # 检测到横杆
                print(percent, "%")
                print("有障碍 等待 contours len：", len(contours))
                time.sleep(0.1)
            else:
                print(percent)

                
                action_append("fastForward04")

                step = 1

        elif step == 1:  # 寻找下一关卡


            action_append("Stand")

            step = 0

            break



#################################################0：过桥##########################################
count_forward = 0
the_distance_Y = 0 
def move_robot(the_distance_left, the_distance_right, the_distance_y, theta):
    global is_bridge_done, count_forward,the_distance_Y
    if math.fabs(math.fabs(theta) - 90) <= 5:
        print("角度很准，直接走吧...", theta)
        if the_distance_left <= 15:
            print("看来不用往左边移动了...", the_distance_left)
        else:
            print("需要左移...", the_distance_left)
            action_append("Left02move")
            time.sleep(0.5)
            return

        if the_distance_right <= 15:
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
        action_append("forwardSlow0403")
        count_forward+=1
        if count_forward > 2+the_distance_Y/5:
            action_append("forwardSlow0403")
            action_append("Stand")
            is_bridge_done = 1
        #action_append("Forwalk01")
        #action_append("Stand")
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
    global step, ChestOrg_img, is_bridge_done, the_distance_Y

    r_w = chest_r_width
    r_h = chest_r_height
    none_contours_action = ''  # 在没有轮廓的时候要执行的动作
    robot_bridge_center = False  # 机器人是否位于桥的中心

    step = 0

    # 可加入先调好位置
    time.sleep(1)

    Chest_contours_last = None  # 记录上一个轮廓，用于step3
    the_bridge_color = ''

    while True:
        if is_bridge_done:
            break
        print(step)
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

        Chest_frame_green = cv2.inRange(Chest_frame_hsv, color_range['green_bridge'][0],
                                        color_range['green_bridge'][1])  # 对原图像和掩模(颜色的字典)进行位运算
        Chest_opened_green = cv2.morphologyEx(Chest_frame_green, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))  # 开运算 去噪点
        Chest_closed_green = cv2.morphologyEx(Chest_opened_green, cv2.MORPH_CLOSE,
                                              np.ones((3, 3), np.uint8))  # 闭运算 封闭连接

        (Chest_contours_green, hierarchy_green) = cv2.findContours(Chest_closed_green, cv2.RETR_LIST,
                                                                      cv2.CHAIN_APPROX_NONE)  # 找出轮廓cv2.CHAIN_APPROX_NONE
        # print("Chest_contours len:",len(Chest_contours))
        Chest_areaMaxContour_green, Chest_area_max_green = getAreaMaxContour(Chest_contours_green)  # 找出最大轮廓
        Chest_percent_green = round(Chest_area_max_green * 100 / (r_w * r_h), 2)

        '''
        Chest_frame_blue = cv2.inRange(Chest_frame_hsv, color_range['blue_bridge'][0],color_range['blue_bridge'][1])  # 对原图像和掩模(颜色的字典)进行位运算
        Chest_opened_blue = cv2.morphologyEx(Chest_frame_blue, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))  # 开运算 去噪点
        Chest_closed_blue = cv2.morphologyEx(Chest_opened_blue, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))  # 闭运算 封闭连接

        (Chest_contours_blue, hierarchy_blue) = cv2.findContours(Chest_closed_blue, cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)  # 找出轮廓cv2.CHAIN_APPROX_NONE
        Chest_areaMaxContour_blue, Chest_area_max_blue = getAreaMaxContour1(Chest_contours_blue)  # 找出最大轮廓
        Chest_percent_blue = round(Chest_area_max_blue * 100 / (r_w * r_h), 2)
        '''

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
            '''
            vx = d1*k1
            vy = (d2- - (381+200)/2)*k2
            w  = k3*(theta-90)
            '''

            if Chest_center_x > 255:
                the_distance_right = -d1  # + d2//100
                the_distance_left = 0
            else:
                the_distance_left = d1  # + d2//100
                the_distance_right = 0

            the_distance_y = d2 // 40
            if count_forward==0:
                the_distance_Y=the_distance_y
                
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

            move_robot(the_distance_left, the_distance_right, the_distance_y, theta)
        else:
            continue

    pass

#################################################1：过雷区##########################################
def pass_landmine():
    global HeadOrg_img, step, ChestOrg_img, debug_obstacle
    global blue_rail
    the_right_left = False

    blue_rail = False

    print("/-/-/-/-/-/-/-/-/-进入obstacle")
    step = 0  # 用数字表示在这一关中执行任务的第几步
    actioned_dir = {'Right02move': 0}
    the_forwalk_num = 0  # 用于记录是否已经通过障碍物
    the_forwalk_total = 0  # 用于检测往前一共走了几步
    while True:
        if ChestOrg_img is None:
            continue
        Corg_img = ChestOrg_img.copy()
        Corg_img = np.rot90(Corg_img)

        Corg_img = Corg_img.copy()
        cv2.imshow('Corg_img0', Corg_img)
        Corg_img[0:290, :, :] = 255
        Corg_img[550:640, :, :] = 255
        cv2.imshow('write Corg_img', Corg_img)
        hsv = cv2.cvtColor(Corg_img, cv2.COLOR_BGR2HSV)
        hsv = cv2.GaussianBlur(hsv, (3, 3), 0)

        Imask = cv2.inRange(hsv, color_dist['black_dir']['Lower'], color_dist['black_dir']['Upper'])
        Imask = cv2.erode(Imask, None, iterations=3)  # 可以尝试去掉
        Imask = cv2.dilate(Imask, np.ones((3, 3), np.uint8), iterations=2)
        cv2.imshow('black', Imask)
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

            # cv2.imshow('handling', handling)
            cv2.imshow('Corg_img', Corg_img)
            cv2.waitKey(1)
            if 1:
                if Big_battle[1] <= 320:
                    print("608L 前进靠近 forwardSlow0403 ", Big_battle[1])
                    action_append("forwardSlow0403")
                    # action_append("forwardSlow0403")
                elif Big_battle[1] <= 380:
                    print("565L 前进靠近 Forwalk01 ", Big_battle[1])
                    action_append("Forwalk01")
                elif Big_battle[1] < 400:
                    print("571L 慢慢前进靠近 Forwalk01  ", Big_battle[1])
                    action_append("Forwalk01")
                # elif Big_battle[1] < 430 and (Big_battle[0] <= (100 + (640 - Big_battle[1]) * 0.15) or Big_battle[0] >= (
                #         380 - (640 - Big_battle[1]) * 0.15)):
                #     print("568L 前进靠近 Forwalk00  ", Big_battle[1])
                #     action_append("Forwalk00")

                # 60---150---225---*240*---270---350---400
                elif 60 <= Big_battle[0] and Big_battle[0] < 150:
                    print("右平移一点点")
                    action_append('Right02move')
                elif 150 <= Big_battle[0] and Big_battle[0] < 225:
                    print('向右平移一步')
                    action_append('Right02move')
                elif 225 <= Big_battle[0] and Big_battle[0] < 240:
                    print('向右平移一大步')
                    action_append('Right02move')
                elif 240 <= Big_battle[0] and Big_battle[0] < 255:
                    print('向左平移一大步')
                    action_append('Left02move')
                elif 255 <= Big_battle[0] and Big_battle[0] < 270:  # 顺便去检测之前机器人已经往左边走了几个了，负数代表往右走
                    print('向左平移一步')
                    action_append('Left02move')
                elif 270 <= Big_battle[0] and Big_battle[0] < 350:
                    print('向左平移一步')
                    action_append('Left02move')
                elif 350 <= Big_battle[0] and Big_battle[0] < 400:  # 能离机器人这么远，机器人还没出事说明此障碍物不是在很边界的地方
                    print('向左平移一点点')
                    action_append('Left02move')

        else:
            if debug_obstacle:
                print("287L 无障碍，可前进")
                action_append("forwardSlow0403")
                the_forwalk_total += 1
                Big_battle = [0, 0]

            # if Big_battle[1] <= 350:
            #     print("608L 前进靠近 forwardSlow0403 ",Big_battle[1])
            #     for i in range(int(450 - Big_battle[1]) // 60):
            #         action_append('forwardSlow0403')
            #         the_forwalk_num += 1
            #         the_forwalk_total += 1
            #     if the_forwalk_num != 5 and actioned_dir['Right02move'] != 0:
            #         the_forwalk_num += 1
            #     elif the_forwalk_num == 5 and actioned_dir['Right02move'] != 0:
            #         the_forwalk_num = 0
            #         the_right_left = True           #表示已经通过上一个障碍物，左移和右移不会触碰到上一个障碍物
            #     elif actioned_dir['Right02move'] == 0:
            #         the_forwalk_num = 0
            #
            #     if the_right_left:
            #         if actioned_dir['Right02move'] != 0:
            #             if actioned_dir['Right02move'] < 0:
            #                 for i in range(abs(actioned_dir['Right02move'])):
            #                     action_append('Right02move')
            #             elif actioned_dir['Right02move'] > 0:
            #                 for i in range(actioned_dir['Right02move']):
            #                     action_append('Left02move')
            #
            #             actioned_dir['Right02move'] = 0
            #         else:
            #             pass
            #
            #         the_right_left = False
            #
            # elif Big_battle[1] <= 400:
            #     print("565L 前进靠近 forwardSlow0403 ",Big_battle[1])
            #     action_append("forwardSlow0403")
            #     the_forwalk_total += 1
            #     if the_forwalk_num != 5 and actioned_dir['Right02move'] != 0 :
            #         the_forwalk_num += 1
            #     elif the_forwalk_num == 5 and actioned_dir['Right02move'] != 0 :
            #         the_forwalk_num = 0
            #         the_right_left = True
            #     elif actioned_dir['Right02move'] == 0 :
            #         the_forwalk_num = 0
            #
            #     if the_right_left:
            #         if actioned_dir['Right02move'] != 0:
            #             if actioned_dir['Right02move'] < 0:
            #                 for i in range(abs(actioned_dir['Right02move'])):
            #                     action_append('Right02move')
            #             elif actioned_dir['Right02move'] > 0:
            #                 for i in range(actioned_dir['Right02move']):
            #                     action_append('Left02move')
            #
            #             actioned_dir['Right02move'] = 0
            #         else:
            #             pass
            #
            #         the_right_left = False
            # elif Big_battle[1] < 450  and (Big_battle[0] <= (100+(640-Big_battle[1])*0.15) or Big_battle[0] >= (380-(640-Big_battle[1])*0.15)) :#此步也很关键
            #     print("568L 慢慢靠近 forwardSlow0403  ",Big_battle[1])
            #     action_append("forwardSlow0403")
            #     the_forwalk_total += 1
            # elif Big_battle == right_point and (Big_battle != left_point):
            #     print('左平移两步 321L')
            #     action_append('Left02move')
            #     actioned_dir['Right02move'] -= 1
            # elif Big_battle == left_point and (Big_battle != right_point):
            #     print('右平移两步 324L')
            #     action_append('Right02move')
            #     actioned_dir['Right02move'] += 1
            # elif 60 <= Big_battle[0] and Big_battle[0] < 150:
            #     print("右平移一点点")
            #     action_append('Right02move')
            #     actioned_dir['Right02move'] += 1
            # elif 150 <= Big_battle[0] and Big_battle[0] < 225:
            #     print('向右平移一步')
            #     action_append('Right02move')
            #     actioned_dir['Right02move'] += 1
            #
            # elif 225 <= Big_battle[0] and Big_battle[0] < 240:
            #     print('向右平移一大步')
            #     action_append('Right02move')
            #     actioned_dir['Right02move'] += 1
            #
            # elif 240 <= Big_battle[0] and Big_battle[0] < 255:
            #     print('向右平移一大步')
            #     action_append('Left02move')
            #     actioned_dir['Right02move'] -= 1
            #
            # elif 255 <= Big_battle[0] and Big_battle[0] < 270:  #顺便去检测之前机器人已经往左边走了几个了，负数代表往右走
            #     print('向左平移一步')
            #     action_append('Left02move')
            #     actioned_dir['Right02move'] -= 1
            #
            # elif 270 <= Big_battle[0] and Big_battle[0] < 350:
            #     action_append('Left02move')
            #     actioned_dir['Right02move'] -= 1
            #
            # elif 350 <= Big_battle[0] and Big_battle[0] < 400:  #能离机器人这么远，机器人还没出事说明此障碍物不是在很边界的地方
            #     action_append('Left02move')
            #     actioned_dir['Right02move'] -= 1

        # else:
        #     print("287L 无障碍，可前进")
        #     action_append("forwardSlow0403")
        #     the_forwalk_total += 1
        #     Big_battle = [0,0]

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

        # cv2.imshow('handling', handling)
        cv2.imshow('Corg_img', Corg_img)
        cv2.waitKey(1)
        print('the_forwalk_total:',the_forwalk_total)
        if the_forwalk_total >= 25:
            action_append("Stand")
            print('okkkkkkkkkk')
            break
        else:
            pass



#################################################2：过障碍##########################################
def pass_obstacle():
    global step, ChestOrg_img
    # global state, step, state_sel



    step = 0
    baffle_dis_Y_flag = False
    baffle_angle = 0
    notok = True
    see = False
    finish = False
    angle = 45
    dis = 0
    dis_flag = False
    angle_flag = False

    print('进入baffle')
    while True:
        # if cap_chest.isOpened():
        #     chest_ret, ChestOrg_img = cap_chest.read()
        xiayige = False
        if ChestOrg_img is None:
            continue
        # print('hahah')
        Corg_img = ChestOrg_img.copy()
        Corg_img = np.rot90(Corg_img)
        OrgFrame = Corg_img.copy()
        cv2.imshow('O',OrgFrame)
        # handling = Corg_img.copy()
        # frame = Corg_img.copy()
        OrgFrame[0:260, :, :] = 255
        # OrgFrame[590:640, :, :] = 255
        center = []

        hsv = cv2.cvtColor(OrgFrame, cv2.COLOR_BGR2HSV)
        hsv = cv2.GaussianBlur(hsv, (3, 3), 0)
        Imask = cv2.inRange(hsv, color_dist['blue']['Lower'], color_dist['blue']['Upper'])
        Imask = cv2.erode(Imask, None, iterations=2)
        Imask = cv2.dilate(Imask, np.ones((3, 3), np.uint8), iterations=2)
        # cv2.imshow('BLcolor', Imask)
        cnts, hieracy = cv2.findContours(Imask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)  # 找出所有轮廓

        # print("cnts len:",len(cnts))
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
                    step = 3
            elif step == 3:
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
                    step = 4

            elif step == 4:
                print("342L 前挪一点点")
                print("326L 翻栏杆 翻栏杆 RollRail")
                action_append("Stand")
                action_append("RollRail")
                print("step step step 444 ")
                '''
                for i in range(2):
                    action_append("Back0Run")
                action_append("turn004L")
                for i in range(2):
                    action_append("turn001L")

                action_append("Left02move")
                action_append("Left02move")
                '''
                xiayige = True

            if xiayige == True:
                break


#################################################3：过门##########################################
def getAreaMaxContour_door0(contours):
    i = 0  
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

        if contour_area_temp > 1000:  # 只有在面积大于25时，轮廓才是有效的，以过滤干扰
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

    box_rect_max = [top_all_left, top_all_right, bottom_all_right, bottom_all_left]

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

    box_rect_max = [top_left, top_right, bottom_right, bottom_left]

    return contour_area_max, area_max_contour, box_rect_max  # 返回最大的轮廓

def pass_door():
    global HeadOrg_img,ChestOrg_img
    step_door_flag = 0 # 进入第几阶段（0：正面朝门；1：转身；2：盲走）
    door_step = 0
    j = 0 #拍照标志
    i = 0
    Chest_top_center_y = 480
    
    while True:

        if HeadOrg_img is None:
            continue
        
        # 图像处理
        HeadOrg_img = HeadOrg_img.copy()
        HeadOrg_img_draw = HeadOrg_img.copy()
        HeadOrg_img_gauss = cv2.GaussianBlur(HeadOrg_img, (3, 3), 0)  # 高斯模糊
        HeadOrg_img_hsv = cv2.cvtColor(HeadOrg_img_gauss, cv2.COLOR_BGR2HSV)  # 将图片转换到HSV空间
        HeadOrg_img_blue = cv2.inRange(HeadOrg_img_hsv, np.array([95, 80, 46]),np.array([124, 255, 255]))  # 对原图像进行掩模运算（这个时候蓝的部分是白的，其他部分是黑的）
        HeadOrg_img_opened = cv2.morphologyEx(HeadOrg_img_blue, cv2.MORPH_OPEN, np.ones((8, 8), np.uint8))  # 开运算 去噪点
        HeadOrg_img_closed = cv2.morphologyEx(HeadOrg_img_opened, cv2.MORPH_CLOSE, np.ones((8, 8), np.uint8))  # 闭运算 封闭连接

        # 找轮廓及4个顶点
        (contours, hierarchy) = cv2.findContours(HeadOrg_img_closed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if Chest_top_center_y > 10:
            max_area, max_contour, max_box= getAreaMaxContour_door1(contours)
        if Chest_top_center_y <= 10:
            max_area, max_contour, max_box= getAreaMaxContour_door0(contours)

        #计算轮廓的一些参数
        if step_door_flag == 0 or step_door_flag == 1:
            Chest_top_center_x = int((max_box[1][0] + max_box[0][0]) / 2)
            Chest_top_center_y = int((max_box[1][1] + max_box[0][1]) / 2)
            Chest_bottom_center_x = int((max_box[2][0] + max_box[3][0]) / 2)
            Chest_bottom_center_y = int((max_box[2][1] + max_box[3][1]) / 2)
            Chest_top_bottom = math.fabs(Chest_top_center_x - Chest_bottom_center_x)
            Chest_bottom_angle = - math.atan((max_box[2][1] - max_box[3][1]) / (max_box[2][0] - max_box[3][0])) * 180.0 / math.pi
            Chest_top_angle = - math.atan((max_box[1][1] - max_box[0][1]) / (max_box[1][0] - max_box[0][0])) * 180.0 / math.pi
            Chest_top_long = max_box[1][0] - max_box[0][0]
            Chest_bottom_long = max_box[2][0] - max_box[3][0]
             
            #画轮廓
            cv2.drawContours(HeadOrg_img_draw, np.array([max_box]), 0, (0, 255, 255), 2)  
            cv2.circle(HeadOrg_img_draw, (max_box[1][0], max_box[1][1]), 3, [0, 255, 255], 2)
            cv2.circle(HeadOrg_img_draw, (max_box[0][0], max_box[0][1]), 3, [0, 255, 255], 2)
            cv2.circle(HeadOrg_img_draw, (max_box[2][0], max_box[2][1]), 3, [0, 255, 255], 2)
            cv2.circle(HeadOrg_img_draw, (max_box[3][0], max_box[3][1]), 3, [0, 255, 255], 2) 
            cv2.circle(HeadOrg_img_draw, (Chest_top_center_x, Chest_top_center_y), 3, [0, 0, 255], 2)
            cv2.circle(HeadOrg_img_draw, (Chest_bottom_center_x, Chest_bottom_center_y), 3, [0, 0, 255], 2)

            cv2.putText(HeadOrg_img_draw, "top_bottom:" + str(int(Chest_top_bottom)), (30, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 255), 2)  
            cv2.putText(HeadOrg_img_draw, "bottom_angle:" + str(int(Chest_bottom_angle)), (30, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 255), 2) 
            cv2.putText(HeadOrg_img_draw, "top_angle:" + str(int(Chest_top_angle)), (30, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 255), 2) 
            cv2.putText(HeadOrg_img_draw, "top_center_y:" + str(int(Chest_top_center_y)), (30, 230), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 255), 2)
            cv2.putText(HeadOrg_img_draw, "top_center_x:" + str(int(Chest_top_center_x)), (30, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 255), 2)
            cv2.putText(HeadOrg_img_draw, "bottom_center_y:" + str(int(Chest_bottom_center_y)), (30, 290), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 255), 2)
            cv2.putText(HeadOrg_img_draw, "bottom_center_x:" + str(int(Chest_bottom_center_x)), (30, 320), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 255), 2)
            cv2.putText(HeadOrg_img_draw, "max_area:" + str(int(max_area)), (30, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 255), 2)
            cv2.putText(HeadOrg_img_draw, "top_long:" + str(int(Chest_top_long)), (30, 380), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 255), 2)
            cv2.putText(HeadOrg_img_draw, "bottome_long:" + str(int(Chest_bottom_long)), (30, 410), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 255), 2)
                
            cv2.imshow('blue_image', HeadOrg_img_blue)
            cv2.imshow('closed_image', HeadOrg_img_closed)
            cv2.imshow('current_image', HeadOrg_img_draw)
            HeadOrg_img_forshow0 = np.vstack((HeadOrg_img, HeadOrg_img_draw))
            HeadOrg_img_forshow1 = np.vstack((HeadOrg_img_blue, HeadOrg_img_closed))
            cv2.waitKey(5)
        
            cv2.imwrite('door_'+str(j)+'.jpg', HeadOrg_img)
            cv2.imwrite('door_'+str(j)+'_0.jpg', HeadOrg_img_forshow0)
            cv2.imwrite('door_'+str(j)+'_1.jpg', HeadOrg_img_forshow1)
            j = j + 1
            
        if step_door_flag == 2:
            cv2.imwrite('door_'+'Chest_'+str(i)+'.jpg', ChestOrg_img)
            i = i + 1
            
        if step_door_flag == 0:

            if Chest_bottom_center_y < 470:
                
                if max_box[0][0] < 30 :
                    action_append("turn004L")
                    print("tooL")
                    continue
                if max_box[1][0] > 450 :
                    action_append("turn004R")
                    print("tooR")
                    continue
                
                if Chest_top_bottom <= 8 and math.fabs(Chest_bottom_angle) <= 3:
                    print("角度可了00")
                    action_append("Forwalk02")
                elif  max_box[3][1] > max_box[2][1]:
                    print("左转一点点00")
                    action_append("turn001L")
                else:
                    print("右转一点点00")
                    action_append("turn001R")
                    
            if Chest_bottom_center_y >= 470:
                
                if Chest_top_long < 160:
                    print("too")
                    action_append("Back2Run")
                    continue
                
                if Chest_top_center_y > 10:
                    
                    if Chest_top_bottom <= 8 and math.fabs(Chest_bottom_angle) <= 3:
                        print("角度可了01")
                    elif  max_box[3][1] > max_box[2][1]:
                        print("左转一点点01")
                        action_append("turn001L")
                        continue
                    else:
                        print("右转一点点01")
                        action_append("turn001R")
                        continue
                        
                    if math.fabs(Chest_bottom_center_x - 340) < 20:
                        print("左右可了01")
                        action_append("Forwalk01")
                    elif Chest_bottom_center_x > 340:
                        print("往右一点点01")
                        action_append("Right02move")
                    else:
                        print("往左一点点01")
                        action_append("Left02move")
                    
                if Chest_top_center_y <= 10:
                    print("转身")
                    action_append("turn010L")
                    action_append("turn010L")
                    action_append("HeadTurn015")
                    step_door_flag = 2
                    continue
                                            
        '''if step_door_flag == 1:
        
            if math.fabs(Chest_top_angle) <=5:
                print("角度可了10")
            elif  Chest_top_angle > 0:
                print("右转一点点10")
                action_append("turn001R")
                continue
            else:
                print("左转一点点10")
                action_append("turn001L")
                continue

            if math.fabs(Chest_top_center_x - 340) < 20:
                print("前后可了10")
                step_door_flag = 2
                continue
            elif Chest_top_center_x > 340:
                print("往后一点点10")
                action_append("Back0Run")
            else:
                print("往前一点点10")
                action_append("Forwalk00")         #左右调整'''
            
        if step_door_flag == 2:
            print("进入盲走")
            if door_step <= 4 :
                action_append("Right3move")
                action_append("Right3move")
                time.sleep(0.5)
                door_step = door_step + 1
                continue
            print("盲走结束")
            action_append("turn010R")
            action_append("turn010R")
            action_append("HeadTurnMM")
            cv2.destroyAllWindows()
            break

#################################################4：过坑##########################################
def bridge_choose(r_w, r_h):
    


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


def pass_hole():
    global ChestOrg_img, FLAG, step

    r_w = chest_r_width
    r_h = chest_r_height

    hole_color = bridge_choose(r_w, r_h)
    step = 0

    while True:  # 初始化

        # 开始处理图像
        if True:  # head发现黄色区域
            t1 = cv2.getTickCount()

            ChestOrg_copy = np.rot90(ChestOrg_img)
            ChestOrg_copy = ChestOrg_copy.copy()
            # ChestOrg_img = cv2.imread('E:\\pic\\09172.PNG')
            # ChestOrg_img = cv2.resize(ChestOrg_img, (640, 480))
            # ChestOrg_copy = np.rot90(ChestOrg_img)
            # ChestOrg_copy = ChestOrg_copy.copy()
            cv2.rectangle(ChestOrg_copy, (0, 580), (480, 640), (0, 0, 0), -1)  # 底部涂白，遮盖双脚
            handling = cv2.resize(ChestOrg_copy, (480, 640), interpolation=cv2.INTER_CUBIC)  # 将图片缩放
            frame_gauss = cv2.GaussianBlur(handling, (3, 3), 0)  # 高斯模糊

            frame_hsv = cv2.cvtColor(frame_gauss, cv2.COLOR_BGR2HSV)  # 将图片转换到HSV空间

            # yellow  yellow   Yellow_
            if hole_color:
                print("blue hole")

                frame = cv2.inRange(frame_hsv, color_range['blue_bridge_1'][0],
                                    color_range['blue_bridge_1'][1])  # 对原图像和掩模(颜色的字典)进行位运算
            else:
                print("green hole")
                frame = cv2.inRange(frame_hsv, color_range['green_bridge_1'][0],
                                    color_range['green_bridge_1'][1])  # 对原图像和掩模(颜色的字典)进行位运算
            opened = cv2.morphologyEx(frame, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))  # 开运算 去噪点
            closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))  # 闭运算 封闭连接
            # (_, contours, hierarchy) = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # 找出轮廓

            frame2 = cv2.bitwise_not(closed)
            cv2.rectangle(frame2, (0, 580), (480, 640), (0, 0, 0), -1)

            cntskeng, hierarchy = cv2.findContours(frame2, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)  # 找出轮廓

            r_w = chest_r_width
            r_h = chest_r_height

            for c in cntskeng:
                area_temp = math.fabs(cv2.contourArea(c))  # contourArea求面积
                rect = cv2.minAreaRect(c)  # 最小外接矩形
                box = np.int0(cv2.boxPoints(rect))  # 最小外接矩形的四个顶点
                edge1 = math.sqrt(math.pow(box[3, 1] - box[0, 1], 2) + math.pow(box[3, 0] - box[0, 0], 2))
                edge2 = math.sqrt(math.pow(box[3, 1] - box[1, 1], 2) + math.pow(box[3, 0] - box[1, 0], 2))
                edge3 = math.sqrt(math.pow(box[3, 1] - box[2, 1], 2) + math.pow(box[3, 0] - box[2, 0], 2))
                # 用来判断哪个是对角线，并且避免出现除以零
                if (edge2 != 0) and (edge3 != 0):
                    if edge1 == max(edge1, edge2, edge3):
                        ratio = edge2 / edge3
                    elif edge2 == max(edge1, edge2, edge3):
                        ratio = edge1 / edge3
                    else:
                        ratio = edge1 / edge2
                    # else:
                    # edge1 = math.sqrt(math.pow(box[3, 1] - box[0, 1], 2) + math.pow(box[3, 0] - box[0, 0], 2))
                    # edge2 = math.sqrt(math.pow(box[3, 1] - box[2, 1], 2) + math.pow(box[3, 0] - box[2, 0], 2))
                    # if ((edge1 != 0) and (edge2 != 0)):
                    #     ratio = edge1 / edge2  #
                    if ((ratio > 0.25) and (ratio < 4) and (area_temp > 1000) and (step == 2)) or (
                            (ratio > 0.25) and (ratio < 4) and (area_temp > 1000) and (area_temp < 50000) and (
                            step <= 2)):
                        cnt_keng = c
                        break

            if cnt_keng is not None:
                #
                # for i in range(0, len(cnt_keng)):
                #     x, y, w, h = cv2.boundingRect(cnt_keng[i])
                #     print(x,y,w,h)
                #     cv2.rectangle(frame, (x, y), (x + w, y + h), (153, 153, 0), 5)

                rect_blue = cv2.minAreaRect(cnt_keng)
                box_blue = np.int0(cv2.boxPoints(rect_blue))  # 点的坐标
                Bbox_centerX = int((box_blue[3, 0] + box_blue[2, 0] + box_blue[1, 0] + box_blue[0, 0]) / 4)
                Bbox_centerY = int((box_blue[3, 1] + box_blue[2, 1] + box_blue[1, 1] + box_blue[0, 1]) / 4)
                Bbox_center = [Bbox_centerX, Bbox_centerY]
                cv2.circle(handling, (Bbox_center[0], Bbox_center[1]), 7, (0, 0, 255), -1)  # 圆点标记
                cv2.drawContours(handling, [box_blue], -1, (255, 0, 0), 3)

            idex = np.lexsort([box_blue[:, 1]])
            sorted_data = box_blue[idex, :]  # 按y坐标从小到大排列
            # print(sorted_data)

            dibian = sorted_data[2:]  # 取y轴坐标大的两个点为底边两点
            idex2 = np.lexsort([dibian[:, 0]])
            sorted_data2 = dibian[idex2, :]  # 按x坐标从小到大排列
            # print('sorted_data2', sorted_data2)
            bottom_left = sorted_data2[0]
            bottom_right = sorted_data2[1]
            # print(bottom_left)
            # print(bottom_right)

            angle_bottom = - math.atan((bottom_right[1] - bottom_left[1]) / (
                    bottom_right[0] - bottom_left[0])) * 180.0 / math.pi
            bottom_center_x = (bottom_right[0] + bottom_left[0]) / 2
            bottom_center_y = (bottom_right[1] + bottom_left[1]) / 2

            cv2.imshow('handling', handling)
            # cv2.imshow('frame_gauss', frame_gauss)
            # cv2.imshow('frame_hsv', frame_hsv)
            # cv2.imshow('frame', frame)
            cv2.imshow("frame2", frame2)
            cv2.waitKey(100)
            # cv2.destroyAllWindows()

        if True:
            if step == 0:  # 依据yellow调整左右位置  到接触黑色
                if bottom_center_y > 360:  # 黑色方框
                    print("进入step 1,当前中心坐标： ", bottom_center_x, bottom_center_y)
                    step = 1
                elif bottom_center_x < 200:
                    print("向左移动 当前中心坐标： ", bottom_center_x, bottom_center_y)
                    action_append("Left02move")
                elif bottom_center_x > 280:
                    print("向右移动 当前中心坐标： ", bottom_center_x, bottom_center_y)
                    action_append("Right02move")
                else:
                    print("继续前进,当前底部坐标： ", bottom_center_x, bottom_center_y)
                    action_append("forwardSlow0403")

            elif step == 1:  # 看黑色下顶点,调整方向和位置
                # angle
                print("进入step1,当前中心坐标： ", bottom_center_x, bottom_center_y)

                if angle_bottom < -2.0:  # 右转
                    if angle_bottom < -6.0:  # 大右转
                        print("Black_angle_bottom < -6 右转 当前底部角度为： ", angle_bottom)
                        action_append("turn001R")
                    elif angle_bottom < -6.0:  # 大右转
                        print("Black_angle_bottom < -4 右转 当前底部角度为：  ", angle_bottom)
                        action_append("turn001R")
                    else:
                        print("Black_angle_bottom < -2 右转 当前底部角度为：  ", angle_bottom)
                        action_append("turn000R")

                    # time.sleep(1)   # timefftest
                elif angle_bottom > 2.0:  # 左转
                    if angle_bottom > 6.0:  # 大左转
                        print("Black_angle_bottom > 6 大左转 当前底部角度为：  ", angle_bottom)
                        action_append("turn001L")
                    elif angle_bottom > 6.0:  # 大左转
                        print("Black_angle_bottom > 4 大左转 当前底部角度为：  ", angle_bottom)
                        action_append("turn001L")
                    else:
                        print("Black_angle_bottom > 2 左转 当前底部角度为：  ", angle_bottom)
                        action_append("turn000L")

                    # time.sleep(1)   # timefftest
                # x 225 # 240
                elif bottom_center_x > 235:  # 小右移 249.6
                    if bottom_center_x > 245:  # 大右移
                        print("bottom_center_x > 0.54 大右移 当前中心点x坐标为：  ", bottom_center_x)
                        action_append("Right02move")
                    else:
                        print("bottom_center_x > 0.54 小右移 当前中心点x坐标为：   ", bottom_center_x)
                        action_append("Right1move")
                elif bottom_center_x < 215:  # 小左移 230.4
                    if bottom_center_x < 205:  # 大左1移
                        print("bottom_center_x < 0.48 大左移 当前中心点x坐标为：   ", bottom_center_x)
                        action_append("Left02move")
                    else:
                        print("bottom_center_x < 0.48 小左移 当前中心点x坐标为：   ", bottom_center_x)
                        action_append("Left1move")
                # y
                elif bottom_center_y > 450:
                    print("进入step 2")
                    step = 2
                elif bottom_center_y <= 400:
                    print("继续往前挪动")  # <480 Forwalk01
                    action_append("forwardSlow0403")
                elif bottom_center_y <= 420:
                    print("继续往前挪动 当前中心坐标： ", bottom_center_x, bottom_center_y)  # Forwalk01
                    action_append("Forwalk01")
                else:
                    print("继续往前挪动 当前中心坐标： ", bottom_center_x, bottom_center_y)
                    action_append("Forwalk00")

            elif step == 2:  # 依据黑线调整完角度和位置后继续前进
                # if bottom_center_y < 480:  # 小步前挪
                #     print("2627L  Black_bottom_center_y < 500 小步前挪 Forwalk01,当前中心坐标： ",bottom_center_x,bottom_center_y)
                #     action_append("Forwalk01")
                print("进入step2,当前中心坐标： ", bottom_center_x, bottom_center_y)

                # if 520 <= bottom_center_y <= 570:
                #     print("进入step3")
                #     step = 3
                # elif bottom_center_y < 520:  # 小步前挪
                #     print("Black_bottom_center_y < 540 小步前挪 Forwalk00,当前中心坐标： ",bottom_center_x,bottom_center_y)
                #     action_append("Forwalk00")
                # elif bottom_center_y >= 570:
                #     print("Black_bottom_center_y > 560 后退一点点 Back0Run,当前中心坐标： ",bottom_center_x,bottom_center_y)
                #     action_append("Back1Run")

                if bottom_center_y < 480:  # 小步前挪
                    print("小步前挪")
                    action_append("Forwalk01")
                elif bottom_center_y < 520:  # 小步前挪
                    print("小步前挪")
                    action_append("Forwalk00")
                elif bottom_center_y >= 560:
                    print("后退一点")
                    action_append("Back1Run")
                elif 520 <= bottom_center_y <= 560:
                    print("进入step3")
                    step = 3

            elif step == 3:
                print("进入step2,当前中心坐标： ", bottom_center_x, bottom_center_y)

                if angle_bottom < -2.0:  # 右转
                    if angle_bottom < -6.0:  # 大右转
                        print("右转 当前底部角度为： ", angle_bottom)
                        action_append("turn001R")
                    # elif angle_bottom < -6.0:  # 大右转
                    #     print("Black_angle_bottom < -4 右转 turn001R,当前底部角度为：  ", angle_bottom)
                    #     action_append("turn001R")
                    else:
                        print("右转 当前底部角度为：  ", angle_bottom)
                        action_append("turn000R")

                    # time.sleep(1)   # timefftest
                elif angle_bottom > 2.0:  # 左转
                    if angle_bottom > 6.0:  # 大左转
                        print("大左转 当前底部角度为：  ", angle_bottom)
                        action_append("turn001L")
                    # elif angle_bottom > 6.0:  # 大左转
                    #     print("Black_angle_bottom > 4 大左转 turn001L,当前底部角度为：  ", angle_bottom)
                    #     action_append("turn001L")
                    else:
                        print("左转 当前底部角度为：  ", angle_bottom)
                        action_append("turn000L")

                    # time.sleep(1)   # timefftest
                # x 225 # 240
                elif bottom_center_x > 235:  # 小右移 249.6
                    if bottom_center_x > 245:  # 大右移
                        print("大右移 当前中心点x坐标为：  ", bottom_center_x)
                        action_append("Right02move")
                    else:
                        print("小右移 当前中心点x坐标为：   ", bottom_center_x)
                        action_append("Right1move")
                elif bottom_center_x < 215:  # 小左移 230.4
                    if bottom_center_x < 205:  # 大左1移
                        print("大左移 当前中心点x坐标为：   ", bottom_center_x)
                        action_append("Left02move")
                    else:
                        print("小左移 当前中心点x坐标为：   ", bottom_center_x)
                        action_append("Left1move")

                action_append("Stand")
                action_append("Right02move")
                action_append("Right02move")
                action_append("Right02move")
                action_append("Right02move")
                action_append("Right02move")
                action_append("Right02move")
                action_append("Right02move")
                action_append("Right02move")
                action_append("Right02move")
                # action_append("Right02move")
                action_append("Stand")
                action_append("turn001R")
                # action_append("turn001L")
                # action_append("turn001L")
                # action_append("turn001L")
                # action_append("turn001L")
                # action_append("turn001L")

                action_append("Stand")
                action_append("fastForward04")
                action_append("Stand")
                action_append("Left02move")
                action_append("Left02move")
                action_append("Left02move")
                action_append("Left02move")
                action_append("Left02move")
                action_append("Left02move")
                # action_append("Left02move")
                # action_append("Left02move")
                # action_append("Left02move")
                action_append("turn001L")
                action_append("turn001L")
                # action_append("turn001L")
                # action_append("turn001L")

                print("过关la!")
                action_append("Stand")
                # action_append("forwardSlow0403")
                # action_append("forwardSlow0403")
                # action_append("forwardSlow0403")
                # action_append("Stand")

                cv2.destroyAllWindows()
                break
        else:
            print(angle_bottom, bottom_center_x, bottom_center_y)


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
    global ChestOrg_img
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

        #上楼梯
        if  step_stair_flag == 0:
    
            if Chest_bottom_center_y < 120:
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
                
            if Chest_bottom_center_y >= 120 and Chest_bottom_center_y < 340:
                
                if max_box[0][0] > 240 :
                    action_append("Left02move")
                    continue
                if max_box[1][0] < 240 :
                    action_append("Right02move")
                    continue
                
                if Chest_bottom_center_x >= 260:
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
                    action_append("Stand")
                    action_append("UpBridge")
                    action_append("Stand")
                    time.sleep(1)
                    action_append("UpBridge")
                    action_append("Stand")
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
                action_append("turn001L")
            if Chest_top_angle < 0:
                print("右转")
                action_append("turn001R")

        if step_stair_flag == 2:
            if math.fabs(Chest_top_angle) > 5 :
                step_stair_flag = 1
            else:
                if math.fabs(Chest_top_center_x - 240) < 20:
                    print("左右可了")
                    action_append("Back2Run")
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
            elif ball_y > 440:
                action_append("Back2Run")
                print('step2, ball_y>440 Back2Run', ball_y)
            elif 370 <= ball_y <= 440:
                # 粗调水平位置
                if ball_x < 180:
                    action_append('Left02move')
                    print('step2, 370<= ball_y <= 440 ball_x<180 Left02move', ball_x)
                elif ball_x > 300:
                    action_append('Right02move')
                    print('step2, 370<= ball_y <= 440 ball_x>300 Right02move', ball_x)
                elif 180 < ball_x < 300:

                    if angle_flag == True:
                        # 调整球坑之间角度
                        if 0 < angle < 60:
                            action_append('turn003R')
                            print('step2 0<angle<60 turn003R', angle)
                        elif 60 < angle < 75:
                            action_append('turn001R')
                            print('step2 angle>60 turn001R', angle)
                        elif angle > 75 or angle < -80:
                            # 进一步调整 球水平位置
                            if ball_x < 200:
                                action_append('Left02move')
                                print('step2 angle>75 or angle<-80 ball_x<200 Left02move', ball_x)
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
            elif ball_y > 440:
                action_append("Back2Run")
                print('step3 ball_y>450 Back2Run', ball_y)

            elif 370 <= ball_y <= 440:
                # 粗调水平位置
                if ball_x < 180:
                    action_append('Left02move')
                    print('step3 370<= ball_y <= 440 ball_x<180 Left02move', ball_x)

                elif ball_x > 300:
                    action_append('Right02move')
                    print('step3 370<= ball_y <= 440 ball_x>300 Right02move', ball_x)

                elif 180 < ball_x < 300:
                    # 调整球和坑之间角度
                    if angle_flag == True:

                        if -60 < angle < 0:
                            action_append('turn003L')
                            print('step3 180<ball_x<300 -60<angle<0 turn003L', angle)

                        elif -80 < angle < -60:
                            action_append('turn001L')
                            print('step3 180<ball_x<300 -80<angle<-60 turn001L', angle)

                        elif angle > 75 or angle < -80:
                            # 进一步调整球水平位置
                            if ball_x < 200:
                                action_append('Left02move')
                                print('step3 angle>75 or angle<-80 ball_x<200 Left02move', ball_x)
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

            elif ball_y > 440:
                action_append("Back2Run")
                print('step4 ball_y>450 Back2Run', ball_y)

            elif 370 <= ball_y <= 440:
                # 粗调水平位置
                if ball_x < 200:
                    action_append('Left02move')
                    print('step4 370<= ball_y <= 440 ball_x<190 Left02move', ball_x)

                elif ball_x > 280:
                    action_append('Right02move')
                    print('step4 370<= ball_y <= 440 ball_x>280 Right02move', ball_x)

                elif 200 < ball_x < 280:

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
                print('step5 ball_y<400 Forwalk00', ball_y)
            elif ball_y > 470:
                action_append('Back2Run')
                print('step5 ball_y>470 Back2Run', ball_y)
            elif 410 < ball_y < 470:
                if ball_x > 240:
                    action_append('Right02move')
                    print('step5 410<ball_y<470 ball_x>240 Right02move', ball_x)
                elif ball_x < 200:
                    action_append('Left02move')
                    print('step5 410<ball_y<470 ball_x<200 Left02move', ball_x)
                elif 200 < ball_x < 240:

                    if angle_flag == True:

                        if angle > 75 or angle < -88:
                            step = 6
                            print('from step5 go to step6', angle)
                            cv2.imwrite('5->6.jpg', chest)
                        elif 60 < angle < 75:
                            action_append('turn001R')
                            print('step5 200<ball_x<240 65<angle<78 turn001R', angle)
                        elif 0 < angle < 60:
                            action_append('turn003R')
                            print('step5 200<ball_x<240 0<angle<65 turn003R', angle)
                        elif -88 < angle < -70:
                            action_append('turn001L')
                            print('step5 200<ball_x<240 -88<angle<-70 turn001L', angle)
                        elif -70 < angle < 0:
                            action_append('turn003L')
                            print('step5 200<ball_x<240 -70<angle<0 turn003L', angle)
                    else:
                        print('step5找不到angle')
                        action_append('Stand')

        elif step == 6:  # angle>78 or angle<-86.5 洞在球前方 410< ball_y <= 460 200< ball_x < 240
            if ball_y < 430:
                action_append('Forwalk00')
                print('step6 ball_y<430 Forwalk00', ball_y)
            elif ball_y > 470:
                action_append('Back2Run')
                print('step6 ball_y>470 Back2Run', ball_y)
            elif 430 < ball_y < 470:
                if ball_x > 220:
                    action_append('Right1move')
                    print('step6 420<ball_y<470 ball_x>220 Right1move', ball_x)
                elif ball_x < 200:
                    action_append('Left1move')
                    print('step6 420<ball_y<470 ball_x<200 Left1move', ball_x)
                elif 200 < ball_x < 220:

                    if angle_flag == True:

                        if angle > 78 and angle < 86 :
                            step = 7
                            print('from step6 go to step7', angle)
                            cv2.imwrite('6->7.jpg', chest)
                        elif 60 < angle < 78:
                            action_append('turn001R')
                            print('step6 200<ball_x<220 60<angle<78 turn001R', angle)
                        elif 0 < angle < 60:
                            action_append('turn003R')
                            print('step6 200<ball_x<220 0<angle<60 turn003R', angle)
                        elif angle < -75 or angle>86 :
                            action_append('turn001L')
                            print('step6 200<ball_x<220 angle < -75 or angle>86 turn001L', angle)
                        elif -75 < angle < 0:
                            action_append('turn003L')
                            print('step6 200<ball_x<220 -75<angle<0 turn003L', angle)
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
    model = models.load_model('../config/yolov3-tiny-custom.cfg',
                          'best1.weights')
    i = 40


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
            if percent_cut > 5:  # 检测到横杆
                print(percent, "%")
                print("有障碍 等待 contours len：", len(contours))
                time.sleep(0.1)
            else:
                print(percent)

                print("231L 执行7步")

                
                action_append("fastForward05")

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
    '''
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
                break
            elif FLAG== 2 or FLAG==3 or FLAG==7 or FLAG==8 or FLAG==12 or FLAG==13:
                pass_hole()
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
            action_append("turn004L")
            time.sleep(0.5)
            action_append("turn005L")
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
            
            pass_bridge()
            break
        else:
            print('image is empty :', chest_ret)
            time.sleep(0.01)
    '''

    while True:
        if ChestOrg_img is not None and chest_ret:
            action_append('fastForward05')
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
    
    action_append('fastForward04')
    
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



