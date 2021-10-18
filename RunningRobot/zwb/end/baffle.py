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
# stream_head = "./images/pic_chest10.png"
# cap_head = cv2.VideoCapture(stream_head)
# stream_chest = "./images/pic_chest8.png"
# cap_chest = cv2.VideoCapture(stream_chest)

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
def restart_camera():

    print('摄像头无响应，执行重启')
    res1=os.system("sudo service livestream.sh stop")
    res2=os.system("sudo service livestream.sh start")
    print(res1,res2)

def get_img():
    global ChestOrg_img, HeadOrg_img, chest_ret, ret
    global cap_chest, cap_head
    # restart_camera()
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


# 读取图像线程
th1 = threading.Thread(target=get_img)
th1.setDaemon(True)
th1.start()
#
#
# ################################################动作执行线程#################################################
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


# def action_append(act_name):
#     global acted_name
#
#     # print("please enter to continue...")
#     # cv2.waitKey(0)
#
#     if action_DEBUG == False:
#         if act_name == "forwardSlow0403" and (acted_name == "Forwalk02RL" or acted_name == "Forwalk02L"):
#             acted_name = "Forwalk02LR"
#         elif act_name == "forwardSlow0403" and (acted_name == "Forwalk02LR" or acted_name == "Forwalk02R"):
#             acted_name = "Forwalk02RL"
#         elif act_name != "forwardSlow0403" and (acted_name == "Forwalk02LR" or acted_name == "Forwalk02R"):
#             # CMDcontrol.action_list.append("Forwalk02RS")#原来是注释
#             # acted_name = act_name#原来是注释
#             print(act_name, "动作未执行 执行 Stand")  # 原来不是注释
#             acted_name = "Forwalk02RS"  # 原来不是注释
#         elif act_name != "forwardSlow0403" and (acted_name == "Forwalk02RL" or acted_name == "Forwalk02L"):
#             # CMDcontrol.action_list.append("Forwalk02LS")#原来是注释
#             # acted_name = act_name#原来是注释
#             print(act_name, "动作未执行 执行 Stand")
#             acted_name = "Forwalk02LS"
#         elif act_name == "forwardSlow0403":
#             acted_name = "Forwalk02R"
#         else:
#             acted_name = act_name
#
#         CMDcontrol.actionComplete = False
#         if len(CMDcontrol.action_list) > 0:
#             print("队列超过一个动作")
#             CMDcontrol.action_list.append(acted_name)
#         else:
#             CMDcontrol.action_list.append(acted_name)
#         CMDcontrol.action_wait()
#
#     else:
#         print("-----------------------执行动作名：", act_name)
#         time.sleep(2)
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
            CMDcontrol.action_list.append("Forwalk02LS")#原来是注释
            acted_name = act_name#原来是注释
            # print(act_name,"动作未执行 执行 Stand")
            # acted_name = "Forwalk02LS"
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
#

color_range = {
    'yellow_door': [(20, 140, 60), (40, 240, 150)],
    'black_door': [(25, 25, 10), (110, 150, 30)],
    'black_gap': [(0, 0, 0), (180, 255, 70)],
    'yellow_hole': [(20, 120, 95), (30, 250, 190)],
    'black_hole': [(5, 80, 20), (40, 255, 100)],
    'chest_red_floor': [(0, 40, 60), (20, 200, 190)],
    'chest_red_floor1': [(0, 100, 60), (20, 200, 210)],
    'chest_red_floor2': [(110, 100, 60), (180, 200, 210)],
    'green_bridge': [(45, 75, 40), (90, 255, 210)],
    # 'green_bridge': [(52, 106, 91), (90, 255, 255)],
    'blue_bridge': [(50, 160, 60), (120, 255, 255)],
    # 'black_dilei': [(0, 0, 0), (110, 160, 70)],
    'black_dilei': [(0, 0, 0), (120, 255, 50)],
    'white_dilei': [(60, 0, 70), (100, 255, 255)],
    'blue_langan': [(50, 160, 40), (120, 255, 255)]
}

color_dist = {'red': {'Lower': np.array([0, 160, 100]), 'Upper': np.array([180, 255, 250])},
              'black_dir': {'Lower': np.array([0, 0, 10]), 'Upper': np.array([170, 170, 45])},
              'black_line': {'Lower': np.array([0, 0, 20]), 'Upper': np.array([100, 160, 80])},
              'blue': {'Lower': np.array([100, 80, 46]), 'Upper': np.array([124, 255, 255])},
              'ball_red': {'Lower': np.array([160, 100, 70]), 'Upper': np.array([190, 215, 145])},
              'blue_hole': {'Lower': np.array([110, 50, 50]), 'Upper': np.array([130, 255, 255])},
              }


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

def get_all_area(contours,contour_area_threshold = 0):
    contour_area_sum = 0
    for c in contours:
        contour_area_now = math.fabs(cv2.contourArea(c))
        if contour_area_now > contour_area_threshold:
            contour_area_sum += contour_area_now
    return contour_area_sum

def baffle():
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
        # print('hahah')
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
            #elif step == 3:
            #    if blue_area < 9000:
            #        action_append('Left02move')
             #       time.sleep(1)
             #   elif blue_area > 12000:
             #       action_append('Right02move')
             #       time.sleep(1)
             #   else:
             #       step =4
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
                print("step step step 444 ")
                for i in range(2):
                    action_append("Back0Run")
                action_append("turn004L")
                for i in range(2):
                    action_append("turn001L")

                action_append("Left02move")
                action_append("Left02move")

                xiayige = True

            if xiayige == True:
                break


if __name__ == '__main__':
    baffle()
    print('已经通过')
    cap_chest.release()
    cap_head.release()

    cv2.destroyAllWindows()
