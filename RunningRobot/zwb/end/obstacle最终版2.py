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
#             #CMDcontrol.action_list.append("Forwalk02RS")#原来是注释
#             #acted_name = act_name#原来是注释
#             print(act_name,"动作未执行 执行 Stand")#原来不是注释
#             acted_name = "Forwalk02RS"#原来不是注释
#         elif act_name != "forwardSlow0403" and (acted_name == "Forwalk02RL" or acted_name == "Forwalk02L"):
#             #CMDcontrol.action_list.append("Forwalk02LS")#原来是注释
#             #acted_name = act_name#原来是注释
#             print(act_name,"动作未执行 执行 Stand")
#             acted_name = "Forwalk02LS"
#         elif act_name == "forwardSlow0403":
#             acted_name = "Forwalk02R"
#         else:
#             acted_name = act_name
#
#         CMDcontrol.actionComplete = False
#         if len(CMDcontrol.action_list) > 0 :
#             print("队列超过一个动作")
#             CMDcontrol.action_list.append(acted_name)
#         else:
#             CMDcontrol.action_list.append(acted_name)
#         CMDcontrol.action_wait()
#
#     else:
#         print("-----------------------执行动作名：",act_name)
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

    #'green_bridge_1': [(52, 106, 91), (90, 255, 255)],
    #'blue_bridge_1': [(83, 86, 135), (122, 255, 255)],
    'green_bridge_1': [(60, 90, 40), (80, 255, 255)],
    'blue_bridge_1': [(50, 160, 60), (120, 255, 255)],
    'green_bridge': [(50, 100, 80), (80, 255, 255)],#正常
    'blue_bridge': [(50, 95, 120), (120, 255, 255)],#正常
    #'green_bridge': [(50, 75, 30), (100, 255, 210)],  # 前射强光(正常也满足)
    #'blue_bridge': [(50, 95, 90), (120, 255, 255)],  # 前射强光(正常也满足)
    #'black_dilei': [(0, 0, 0), (110, 160, 80)],
    'black_dilei': [(0, 0, 0), (130, 160, 80)],
    'white_dilei': [(60, 0, 70), (100, 255, 255)],
    'blue_langan': [(50, 160, 40), (120, 255, 255)]
}

def getAreaMaxContour1(contours):    # 返回轮廓 和 轮廓面积
    contour_area_temp = 0
    contour_area_max = 0
    area_max_contour = None
    for c in contours:  # 历遍所有轮廓
        contour_area_temp = math.fabs(cv2.contourArea(c))  # 计算轮廓面积
        if contour_area_temp > contour_area_max:
            contour_area_max = contour_area_temp
            if contour_area_temp > 25:  #只有在面积大于25时，最大面积的轮廓才是有效的，以过滤干扰
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


debug_action = 1

the_forwalk_total = 0
Last_baffle_dis_Y = 190
def obstacle():
    global ChestOrg_img, HeadOrg_img, the_forwalk_total, Last_baffle_dis_Y

    print("/-/-/-/-/-/-/-/-/-进入obstacle")
    is_enter = 0
    is_center = 0
    is_end = 0
    while True:
        print('the_forwalk_total:',the_forwalk_total)
        if the_forwalk_total > 2:
            is_enter = 1

#         if the_forwalk_total >=12 and the_forwalk_total <=14:
#             is_center = 1

        #if Last_baffle_dis_Y >=350 and the_forwalk_total > 10:
         #   is_end = 1
   
        if ChestOrg_img is None:
            continue
        
        
        Corg_img0 = ChestOrg_img.copy()
        Corg_img0 = np.rot90(Corg_img0)

        Corg_img = Corg_img0.copy()
        if is_enter:
            Corg_img[0:290, :] = 255
            Corg_img[550:640, :] = 255
        else:
            Corg_img[0:290, :] = 255
            Corg_img[500:640, :] = 255
        '''if is_center:
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
            #the_distance_left, the_distance_right, the_distance_y, theta, Area = get_angle2()
            print('baffle_angle, baffle_dis_Y:',baffle_angle,' ### ', baffle_dis_Y)
            #print('the_distance_left, the_distance_right:',the_distance_left, ' ### ',the_distance_right)
            #print('the_distance_y, theta, Area:',the_distance_y,' ### ', theta, ' ### ', Area)

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

            if debug_action:

                
                if baffle_angle < -1 and the_forwalk_total%1 == 0:
                    action_append("turn001R")
                elif baffle_angle > 1 and the_forwalk_total%1 == 0:
                    action_append("turn001L")
                    
                elif baffle_dis_Y > 350 and the_forwalk_total > 18:
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
        # if the_forwalk_total >= 22:
        #     action_append("Stand")
        #     break
        # else:
        #     pass

def get_angle1():
    global  ChestOrg_img, HeadOrg_img, the_forwalk_total, Last_baffle_dis_Y
    if ChestOrg_img is None:
        baffle_angle,baffle_dis_Y = 0,200
        
    else:
        Corg_img = ChestOrg_img.copy()
        #Corg_img = HeadOrg_img.copy()
        Corg_img = np.rot90(Corg_img)
        OrgFrame = Corg_img.copy()
        if the_forwalk_total < 4:
            baffle_angle,baffle_dis_Y = 0,200
            
        
            #cv2.imshow('O',OrgFrame)
            #OrgFrame[0:210, :] = 255#qidian
            #OrgFrame[0:240, :] = 255#zhongjian
            #OrgFrame[0:280, :] = 255#3/4shaoyidian
            #OrgFrame[0:330, :] = 255#3/4duoyidian
            #OrgFrame[0:410, :] = 255#zhongdian
            
            #OrgFrame[0:180, :] = 255#qidian 195
            #OrgFrame[0:220, :] = 255#zhongjian 237 
            #OrgFrame[0:245, :] = 255#3/4shaoyidian 264
            #OrgFrame[0:300, :] = 255#3/4duoyidian 320
            #OrgFrame[0:400, :] = 255#zhongdian 440
            #y=0.8984*x+7.378
        
            max_index=int(0.8984*Last_baffle_dis_Y+30)
            if max_index>450:
                max_index = 180
            OrgFrame[0:max_index, :] = 255
            OrgFrame[500:640, :] = 255
        else:
            max_index=int(0.8984*Last_baffle_dis_Y+30)
            if max_index>450:
                max_index = 180
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
            baffle_angle,baffle_dis_Y = 0, 200
            
    return baffle_angle,baffle_dis_Y


def get_angle2():
    global ChestOrg_img

    r_w = chest_r_width
    r_h = chest_r_height

    # 可加入先调好位置
    #time.sleep(1)
    ChestOrg_copy = ChestOrg_img.copy()
    ChestOrg_copy = np.rot90(ChestOrg_img)
    ChestOrg_copy = ChestOrg_copy.copy()
    # cv2.imshow('1',ChestOrg_copy)
    ChestOrg_copy = ChestOrg_copy[150:585, 0:480]
    # cv2.imshow('2',ChestOrg_copy)
    border = cv2.copyMakeBorder(ChestOrg_copy, 12, 12, 16, 16, borderType=cv2.BORDER_CONSTANT,
                                value=(255, 255, 255))  # 扩展白边，防止边界无法识别
    Chest_img_copy = cv2.resize(border, (r_w, r_h), interpolation=cv2.INTER_CUBIC)  # 将图片缩放
    #cv2.imshow('3', Chest_img_copy)
    # cv2.waitKey(0)
    Chest_frame_gauss = cv2.GaussianBlur(Chest_img_copy, (3, 3), 0)  # 高斯模糊
    Chest_frame_hsv = cv2.cvtColor(Chest_frame_gauss, cv2.COLOR_BGR2HSV)  # 将图片转换到HSV空间


    Chest_frame_green = cv2.inRange(Chest_frame_hsv, color_range['white_dilei'][0],
                                    color_range['white_dilei'][1])  # 对原图像和掩模(颜色的字典)进行位运算
    #cv2.imshow('4', Chest_frame_green)
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

        Area = cv2.contourArea(Chest_areaMaxContour)



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
            cv2.imshow('Angle2', Chest_img_copy)
            cv2.waitKey(1)

    return the_distance_left, the_distance_right, the_distance_y, theta, Area

if __name__ == '__main__':
    # action_append('Stand')
    obstacle()
    print('已经通过雷区')
    cap_chest.release()
    cap_head.release()

    cv2.destroyAllWindows()
