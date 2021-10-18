#!/usr/bin/env python3
# coding:utf-8

import cv2
import math
import numpy as np
import threading
import time
import datetime

import CMDcontrol

robot_IP = "192.168.110.42"
camera_out = "chest"
stream_pic = False
action_DEBUG = False
#################################################初始化#########################################################

cap_chest = cv2.VideoCapture(0)
cap_head = cv2.VideoCapture(2)
'''stream_head = "http://192.168.137.3:8082/?action=stream?dummy=param.mjpg"
cap_head = cv2.VideoCapture(stream_head)
stream_chest = "http://192.168.137.3:8080/?action=stream?dummy=param.mjpg"
cap_chest = cv2.VideoCapture(stream_chest)'''
print(1)
box_debug = True
debug = False
img_debug = True

state = 1  # 用数字用来标志第几关
step = 0
state_sel = 'hole'  # 名称来标志第几关
reset = 0
skip = 0

chest_ret = False  # 读取图像标志位--\
ret = False  # 读取图像标志位  |
ChestOrg_img = None  # 原始图像更新    |
HeadOrg_img = None  # 原始图像更新    |这四个都是读取摄像头时的返回参数
ChestOrg_copy = None
HeadOrg_copy = None

chest_r_width = 480
chest_r_height = 640
head_r_width = 640
head_r_height = 480


################################################读取图像线程#################################################
def get_img():
    global ChestOrg_img, HeadOrg_img, chest_ret, ret
    global cap_chest, cap_head
    while True:
        if cap_chest.isOpened():

            chest_ret, ChestOrg_img = cap_chest.read()
            ret, HeadOrg_img = cap_head.read()
            if (chest_ret == False) or (ret == False):
                print("ret faile ------------------")
            if HeadOrg_img is None:
                print("HeadOrg_img error")
            if ChestOrg_img is None:
                print("ChestOrg_img error")

        else:
            time.sleep(0.01)
            ret = True
            print("58L pic  error ")


# 读取图像线程
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
            # print(act_name,"动作未执行 执行 Stand")
            # acted_name = "Forwalk02RS"#原来不是注释
        elif act_name != "forwardSlow0403" and (acted_name == "Forwalk02RL" or acted_name == "Forwalk02L"):
            CMDcontrol.action_list.append("Forwalk02LS")  # 原来是注释
            acted_name = act_name  # 原来是注释
            # print(act_name,"动作未执行 执行 Stand")
            # acted_name = "Forwalk02LS"
        elif act_name == "forwardSlow0403":
            acted_name = "Forwalk02R"
        else:
            acted_name = act_name

        CMDcontrol.actionComplete = False
        if len(CMDcontrol.action_list) > 0:
            print("队列超过一个动作")
            CMDcontrol.action_list.append(acted_name)
        else:
            CMDcontrol.action_list.append(acted_name)
        CMDcontrol.action_wait()

    else:
        print("-----------------------执行动作名：", act_name)
        time.sleep(2)


color_range = {
    'yellow_door': [(20, 100, 60), (50, 240, 170)],
    'black_door': [(25, 25, 10), (110, 150, 50)],
    'black_gap': [(0, 0, 0), (180, 255, 70)],

    'yellow_hole': [(25, 90, 70), (40, 255, 255)],
    'black_hole': [(10, 10, 10), (180, 190, 60)],

    'chest_red_floor': [(0, 40, 60), (20, 200, 190)],
    'chest_red_floor1': [(0, 100, 60), (20, 200, 210)],
    'chest_red_floor2': [(110, 100, 60), (180, 200, 210)],


    #'green_bridge_1': [(60, 90, 40), (80, 255, 255)],
    'green_bridge_1': [(60, 140, 90), (80, 255, 255)],
    'green_bridge_2': [(60, 55, 40), (80, 255, 255)],
    'blue_bridge_1': [(50, 120, 70), (120, 255, 255)],
    'green_bridge': [(50, 100, 80), (80, 255, 255)],#正常
    'blue_bridge': [(50, 95, 120), (120, 255, 255)],#正常
    #'green_bridge': [(50, 75, 30), (100, 255, 210)],  # 前射强光(正常也满足)
    #'blue_bridge': [(50, 95, 90), (120, 255, 255)],  # 前射强光(正常也满足)
    'black_dilei': [(0, 0, 0), (110, 160, 80)],
    'white_dilei': [(60, 0, 70), (100, 255, 255)],
    'blue_langan': [(50, 160, 40), (120, 255, 255)]
}


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


debug_action = True

is_bridge_done = 0
count_forward = 0
the_distance_Y = 0


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
        '''if FLAG==3 or FLAG==8 or FLAG==13:
            color_range_lower = color_range['green_bridge_1'][0]
            color_range_upper = color_range['green_bridge_1'][1]
        if FLAG==2 or FLAG==7 or FLAG==12:
            color_range_lower = color_range['blue_bridge_1'][0]
            color_range_upper = color_range['blue_bridge_1'][1]
        Chest_frame_green = cv2.inRange(Chest_frame_hsv, color_range_lower,
                                        color_range_upper)  # 对原图像和掩模(颜色的字典)进行位运算'''
        if is_enter:
            Chest_frame_green = cv2.inRange(Chest_frame_hsv, color_range['green_bridge_2'][0],
                                        color_range['green_bridge_2'][1])  # 对原图像和掩模(颜色的字典)进行位运算
        else:
            Chest_frame_green = cv2.inRange(Chest_frame_hsv, color_range['green_bridge_1'][0],
                                        color_range['green_bridge_1'][1])  # 对原图像和掩模(颜色的字典)进行位运算

        '''Chest_frame_green = cv2.inRange(Chest_frame_hsv, color_range['blue_bridge_1'][0],
                                        color_range['blue_bridge_1'][1])'''  # 对原图像和掩模(颜色的字典)进行位运算
        cv2.imshow('4', Chest_frame_green)
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
                    if Chest_bottom_left[1] < 550 or Chest_bottom_right[1] < 550:
                        step = 1
                        continue
                    else:
                        action_append("Back0Run")
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
                    action_append('Left02move')
                    time.sleep(0.5)
                    action_append('Left02move')
                    time.sleep(0.5)
                    action_append('Left02move')
                    time.sleep(0.5)
                    action_append('Left02move')
                    time.sleep(0.5)
                    action_append('Left02move')
                    step = 5
                else:
                    break
        else:
            continue

def get_all_args():
    global count_forward, state_sel, org_img, step, reset, skip, debug, chest_ret, ChestOrg_img, the_forward_num, is_bridge_done, the_distance_Y

    r_w = chest_r_width
    r_h = chest_r_height


    ChestOrg_copy = ChestOrg_img.copy()
    ChestOrg_copy = np.rot90(ChestOrg_img)
    ChestOrg_copy = ChestOrg_copy.copy()
    # cv2.imshow('1',ChestOrg_copy)
    ChestOrg_copy = ChestOrg_copy[150:585, 0:480]
    # cv2.imshow('2',ChestOrg_copy)
    border = cv2.copyMakeBorder(ChestOrg_copy, 12, 12, 16, 16, borderType=cv2.BORDER_CONSTANT,
                                value=(255, 255, 255))  # 扩展白边，防止边界无法识别
    Chest_img_copy = cv2.resize(border, (r_w, r_h), interpolation=cv2.INTER_CUBIC)  # 将图片缩放
    cv2.imshow('3', Chest_img_copy)
    # cv2.waitKey(0)
    Chest_frame_gauss = cv2.GaussianBlur(Chest_img_copy, (3, 3), 0)  # 高斯模糊
    Chest_frame_hsv = cv2.cvtColor(Chest_frame_gauss, cv2.COLOR_BGR2HSV)  # 将图片转换到HSV空间
    '''if FLAG==1 or FLAG==6 or FLAG==11:
        color_range_lower = color_range['green_bridge'][0]
        color_range_upper = color_range['green_bridge'][1]
    if FLAG==0 or FLAG==5 or FLAG==10:
        color_range_lower = color_range['blue_bridge'][0]
        color_range_upper = color_range['blue_bridge'][1]
    Chest_frame_green = cv2.inRange(Chest_frame_hsv, color_range_lower,
                                    color_range_upper)  # 对原图像和掩模(颜色的字典)进行位运算'''

    '''Chest_frame_green = cv2.inRange(Chest_frame_hsv, color_range['green_bridge'][0],
                                    color_range['green_bridge'][1])  # 对原图像和掩模(颜色的字典)进行位运算'''

    Chest_frame_green = cv2.inRange(Chest_frame_hsv, color_range['blue_bridge'][0],
                                    color_range['blue_bridge'][1])  # 对原图像和掩模(颜色的字典)进行位运算
    cv2.imshow('4', Chest_frame_green)
    Chest_opened_green = cv2.morphologyEx(Chest_frame_green, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))  # 开运算 去噪点
    Chest_closed_green = cv2.morphologyEx(Chest_opened_green, cv2.MORPH_CLOSE,
                                          np.ones((3, 3), np.uint8))  # 闭运算 封闭连接

    (Chest_contours_green, hierarchy_green) = cv2.findContours(Chest_closed_green, cv2.RETR_LIST,
                                                               cv2.CHAIN_APPROX_NONE)  # 找出轮廓cv2.CHAIN_APPROX_NONE
    # print("Chest_contours len:",len(Chest_contours))
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


    return Chest_top_left,Chest_top_right,Chest_bottom_left,Chest_bottom_right,angle_top,angle_bottom




if __name__ == '__main__':
    # action_append('Stand')
    pass_hole()
    print('已经通过')
    cap_chest.release()
    cap_head.release()

    cv2.destroyAllWindows()
