import cv2
import math
import numpy as np
import threading
import time
import datetime

import CMDcontrol

robot_IP = "192.168.137.4"
camera_out = "chest"
stream_pic = False
action_DEBUG = False
#################################################初始化#########################################################


#stream_head = "http://192.168.3.29:8082/?action=stream?dummy=param.mjpg"
cap_head = cv2.VideoCapture(2)
#stream_chest = "http://192.168.3.29:8080/?action=stream?dummy=param.mjpg"
cap_chest = cv2.VideoCapture(0)

box_debug = False
debug = False
img_debug = False

state = 1
step = 0
state_sel = 'hole'
reset = 0
skip = 0

chest_ret = False  # 读取图像标志位
ret = False  # 读取图像标志位
ChestOrg_img = None  # 原始图像更新
HeadOrg_img = None  # 原始图像更新
ChestOrg_copy = None
HeadOrg_copy = None
r_width = 480
r_height = 640

chest_r_width = 480
r_w = 480
r_h= 640
chest_r_height = 640
head_r_width = 640
head_r_height = 480


################################################读取图像线程#################################################
def get_img():
    global ChestOrg_img, HeadOrg_img, HeadOrg_img, chest_ret
    global ret
    global cap_chest
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
            # CMDcontrol.action_list.append("Forwalk02RS")
            # acted_name = act_name
            print(act_name, "动作未执行 执行 Stand")
            acted_name = "Forwalk02RS"
        elif act_name != "forwardSlow0403" and (acted_name == "Forwalk02RL" or acted_name == "Forwalk02L"):
            # CMDcontrol.action_list.append("Forwalk02LS")
            # acted_name = act_name
            print(act_name, "动作未执行 执行 Stand")
            acted_name = "Forwalk02LS"
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
    'yellow_door': [(20, 140, 60), (40, 240, 150)],
    'black_door': [(25, 25, 10), (110, 150, 30)],
    'black_gap': [(0, 0, 0), (180, 255, 70)],
    'yellow_hole': [(0, 40, 30), (20, 240, 230)],
    # 'yellow_hole': [(55, 40, 40), (85, 240, 250)],
    # 'yellow_hole': [(95, 115, 115), (120, 220, 250)],
    # 'yellow_hole': [(60, 100, 70), (80, 220, 200)],

    'green_bridge_1': [(35, 43, 46), (80, 255, 255)],
    'blue_bridge_1':[(83,86,135),(122,255,255)],
    'blue' :[(95, 80, 46), (124,255, 255)],


    'black_hole': [(5, 80, 20), (40, 255, 100)],
    'chest_red_floor': [(0, 40, 60), (20, 200, 190)],
    'chest_red_floor1': [(0, 100, 60), (20, 200, 210)],
    'chest_red_floor2': [(110, 100, 60), (180, 200, 210)],
    'green_bridge': [(50, 75, 70), (80, 240, 210)],
}

color_dist = {'red': {'Lower': np.array([0, 160, 100]), 'Upper': np.array([180, 255, 250])},
              'black_dir': {'Lower': np.array([0, 0, 10]), 'Upper': np.array([170, 170, 45])},
              'black_line': {'Lower': np.array([0, 0, 20]), 'Upper': np.array([100, 160, 80])},
              'blue': {'Lower': np.array([100, 80, 46]), 'Upper': np.array([124, 255, 255])},
              'ball_red': {'Lower': np.array([160, 100, 70]), 'Upper': np.array([190, 215, 145])},
              'blue_hole': {'Lower': np.array([100, 130, 80]), 'Upper': np.array([130, 255, 150])},
              }


###############得到线形的总的轮廓###############
# 这个比值适应调整  handling
# 排除掉肩部黑色
def getLine_SumContour(contours, area=1):
    global handling
    contours_sum = None
    for c in contours:  # 初始化    contours_sum
        area_temp = math.fabs(cv2.contourArea(c))
        rect = cv2.minAreaRect(c)  # 最小外接矩形
        box = np.int0(cv2.boxPoints(rect))  # 最小外接矩形的四个顶点
        edge1 = math.sqrt(math.pow(box[3, 1] - box[0, 1], 2) + math.pow(box[3, 0] - box[0, 0], 2))
        edge2 = math.sqrt(math.pow(box[3, 1] - box[2, 1], 2) + math.pow(box[3, 0] - box[2, 0], 2))
        ratio = edge1 / edge2  # 长与宽的比值大于3认为是条线
        center_y = (box[0, 1] + box[1, 1] + box[2, 1] + box[3, 1]) / 4
        if (area_temp > area) and (ratio > 3 or ratio < 0.33) and center_y > 240:
            contours_sum = c
            break
    for c in contours:
        area_temp = math.fabs(cv2.contourArea(c))
        rect = cv2.minAreaRect(c)  # 最小外接矩形
        box = np.int0(cv2.boxPoints(rect))  # 最小外接矩形的四个顶点
        edge1 = math.sqrt(math.pow(box[3, 1] - box[0, 1], 2) + math.pow(box[3, 0] - box[0, 0], 2))
        edge2 = math.sqrt(math.pow(box[3, 1] - box[2, 1], 2) + math.pow(box[3, 0] - box[2, 0], 2))
        ratio = edge1 / edge2
        # print("ratio:",ratio,"area_temp:",area_temp)

        if (area_temp > area) and (ratio > 3 or ratio < 0.33):  # 满足面积条件 长宽比条件

            rect = cv2.minAreaRect(c)  # 最小外接矩形
            box = np.int0(cv2.boxPoints(rect))  # 最小外接矩形的四个顶点
            center_x = (box[0, 0] + box[1, 0] + box[2, 0] + box[3, 0]) / 4
            center_y = (box[0, 1] + box[1, 1] + box[2, 1] + box[3, 1]) / 4

            if center_y > 240:  # 满足中心点坐标条件
                contours_sum = np.concatenate((contours_sum, c), axis=0)  # 将所有轮廓点拼接到一起
                if box_debug:
                    cv2.drawContours(handling, [box], -1, (0, 255, 0), 5)
                    cv2.imshow('handling', handling)
                    cv2.waitKey(10)
            else:
                if box_debug:
                    cv2.drawContours(handling, [box], -1, (0, 0, 255), 5)
                    cv2.imshow('handling', handling)
                    cv2.waitKey(10)
        else:  # 弃
            rect = cv2.minAreaRect(c)  # 最小外接矩形
            box = np.int0(cv2.boxPoints(rect))  # 最小外接矩形的四个顶点
            if box_debug:
                cv2.drawContours(handling, [box], -1, (0, 0, 255), 5)
                cv2.imshow('handling', handling)
                cv2.waitKey(10)

    return contours_sum


# 得到最大轮廓和对应的最大面积
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


# 通过两边的黑线，调整左右位置 和 角度
def head_angle_dis():
    global HeadOrg_img, chest_copy, reset, skip
    global handling
    angle_ok_flag = False
    angle = 90
    dis = 0
    bottom_centreX = 0
    bottom_centreY = 0
    see = False
    dis_ok_count = 0
    headTURN = 0

    step = 1
    print("/-/-/-/-/-/-/-/-/-head*angle*dis")
    while True:

        OrgFrame = HeadOrg_img.copy()

        x_start = 260
        blobs = OrgFrame[int(0):int(480), int(x_start):int(380)]  # 只对中间部分识别处理  Y , X
        # cv2.rectangle(blobs,(0,460),(120,480),(255,255,255),-1)       # 涂白
        handling = blobs.copy()
        frame_mask = blobs.copy()

        # 获取图像中心点坐标x, y
        center = []

        # 开始处理图像

        hsv = cv2.cvtColor(frame_mask, cv2.COLOR_BGR2HSV)
        hsv = cv2.GaussianBlur(hsv, (3, 3), 0)
        Imask = cv2.inRange(hsv, color_dist['black_line']['Lower'], color_dist['black_line']['Upper'])
        # Imask = cv2.erode(Imask, None, iterations=1)
        Imask = cv2.dilate(Imask, np.ones((3, 3), np.uint8), iterations=2)
        _, cnts, hierarchy = cv2.findContours(Imask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)  # 找出所有轮廓
        # print("327L len:",len(cnts))
        cnt_sum = getLine_SumContour(cnts, area=300)

        # 初始化
        L_R_angle = 0
        blackLine_L = [0, 0]
        blackLine_R = [0, 0]

        if cnt_sum is not None:
            see = True
            rect = cv2.minAreaRect(cnt_sum)  # 最小外接矩形
            box = np.int0(cv2.boxPoints(rect))  # 最小外接矩形的四个顶点
            # cv2.drawContours(OrgFrame, [box], 0, (0, 255, 0), 2)  # 将大矩形画在图上

            if math.sqrt(math.pow(box[3, 1] - box[0, 1], 2) + math.pow(box[3, 0] - box[0, 0], 2)) > math.sqrt(
                    math.pow(box[3, 1] - box[2, 1], 2) + math.pow(box[3, 0] - box[2, 0], 2)):
                if box[3, 0] - box[0, 0] == 0:
                    angle = 90
                else:
                    angle = - math.atan((box[3, 1] - box[0, 1]) / (box[3, 0] - box[0, 0])) * 180.0 / math.pi
                if box[3, 1] + box[0, 1] > box[2, 1] + box[1, 1]:
                    Ycenter = int((box[2, 1] + box[1, 1]) / 2)
                    Xcenter = int((box[2, 0] + box[1, 0]) / 2)
                    if box[2, 1] > box[1, 1]:
                        blackLine_L = [box[2, 0], box[2, 1]]
                        blackLine_R = [box[1, 0], box[1, 1]]
                    else:
                        blackLine_L = [box[1, 0], box[1, 1]]
                        blackLine_R = [box[2, 0], box[2, 1]]
                    cv2.circle(OrgFrame, (Xcenter + x_start, Ycenter), 10, (255, 255, 0), -1)  # 画出中心点
                else:
                    Ycenter = int((box[3, 1] + box[0, 1]) / 2)
                    Xcenter = int((box[3, 0] + box[0, 0]) / 2)
                    if box[3, 1] > box[0, 1]:
                        blackLine_L = [box[3, 0], box[3, 1]]
                        blackLine_R = [box[0, 0], box[0, 1]]
                    else:
                        blackLine_L = [box[0, 0], box[0, 1]]
                        blackLine_R = [box[3, 0], box[3, 1]]
                    cv2.circle(OrgFrame, (Xcenter + x_start, Ycenter), 10, (255, 255, 0), -1)  # 画出中心点
            else:
                if box[3, 0] - box[2, 0] == 0:
                    angle = 90
                else:
                    angle = - math.atan(
                        (box[3, 1] - box[2, 1]) / (box[3, 0] - box[2, 0])) * 180.0 / math.pi  # 负号是因为坐标原点的问题
                if box[3, 1] + box[2, 1] > box[0, 1] + box[1, 1]:
                    Ycenter = int((box[1, 1] + box[0, 1]) / 2)
                    Xcenter = int((box[1, 0] + box[0, 0]) / 2)
                    if box[0, 1] > box[1, 1]:
                        blackLine_L = [box[0, 0], box[0, 1]]
                        blackLine_R = [box[1, 0], box[1, 1]]
                    else:
                        blackLine_L = [box[1, 0], box[1, 1]]
                        blackLine_R = [box[0, 0], box[0, 1]]
                    cv2.circle(OrgFrame, (Xcenter + x_start, Ycenter), 10, (255, 255, 0), -1)  # 画出中心点
                else:
                    Ycenter = int((box[2, 1] + box[3, 1]) / 2)
                    Xcenter = int((box[2, 0] + box[3, 0]) / 2)
                    if box[3, 1] > box[2, 1]:
                        blackLine_L = [box[3, 0], box[3, 1]]
                        blackLine_R = [box[2, 0], box[2, 1]]
                    else:
                        blackLine_L = [box[2, 0], box[2, 1]]
                        blackLine_R = [box[3, 0], box[3, 1]]
                    cv2.circle(OrgFrame, (Xcenter + x_start, Ycenter), 10, (255, 255, 0), -1)  # 画出中心点

            if blackLine_L[0] == blackLine_R[0]:
                L_R_angle = 0
            else:
                L_R_angle = -math.atan(
                    (blackLine_L[1] - blackLine_R[1]) / (blackLine_L[0] - blackLine_R[0])) * 180.0 / math.pi

            if img_debug:
                cv2.circle(OrgFrame, (blackLine_L[0] + x_start, blackLine_L[1]), 5, [0, 255, 255], 2)
                cv2.circle(OrgFrame, (blackLine_R[0] + x_start, blackLine_R[1]), 5, [255, 0, 255], 2)
                cv2.line(OrgFrame, (blackLine_R[0] + x_start, blackLine_R[1]),
                         (blackLine_L[0] + x_start, blackLine_L[1]), (0, 255, 255), thickness=2)
                cv2.putText(OrgFrame, "L_R_angle:" + str(L_R_angle), (10, OrgFrame.shape[0] - 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)
                cv2.putText(OrgFrame, "Xcenter:" + str(Xcenter + x_start), (10, OrgFrame.shape[0] - 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)
                cv2.putText(OrgFrame, "Ycenter:" + str(Ycenter), (200, OrgFrame.shape[0] - 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)

                # cv2.drawContours(frame_mask, cnt_sum, -1, (255, 0, 255), 3)
                # cv2.imshow('frame_mask', frame_mask)
                cv2.imshow('black', Imask)
                cv2.imshow('OrgFrame', OrgFrame)
                cv2.waitKey(10)
        else:
            see = False

        # 决策执行动作
        if step == 1:
            print("157L 向右看 HeadTurn015")
            action_append("HeadTurn015")
            time.sleep(1)  # timefftest
            step = 2
        elif step == 2:
            if not see:  # not see the edge
                print("276L 右侧看不到黑线 左侧移 Left3move")
                action_append("Left3move")
                headTURN += 1
                if headTURN > 3:
                    headTURN = 0
                    print("276L 右侧看不到黑线 转为左看 waitKey")
                    step = 3
            else:  # 0
                headTURN = 0
                if L_R_angle > 2:
                    if L_R_angle > 7:
                        print("416L 左da旋转 turn001L ", L_R_angle)
                        action_append("turn001L")
                    # elif L_R_angle > 5:
                    #     print("419L 左da旋转 turn001L ",L_R_angle)
                    #     action_append("turn001L")
                    else:
                        print("422L 左旋转 turn000L ", L_R_angle)
                        action_append("turn000L")
                    # time.sleep(1)   # timefftest
                elif L_R_angle < -2:
                    if L_R_angle < -7:
                        print("434L 右da旋转  turn001R ", L_R_angle)
                        action_append("turn001R")
                    # elif L_R_angle < -5:
                    #     print("437L 右da旋转  turn001R ",L_R_angle)
                    #     action_append("turn001R")
                    else:
                        print("461L 右旋转  turn000R ", L_R_angle)
                        action_append("turn000R")
                    # time.sleep(1)   # timefftest
                elif Ycenter >= 430:
                    if Ycenter > 450:
                        print("451L 左da侧移 Left3move >440 ", Ycenter)
                        action_append("Left3move")
                    else:
                        print("439L 左侧移 Left02move > 365 ", Ycenter)
                        action_append("Left02move")
                elif Ycenter < 390:
                    if Ycenter < 370:
                        print("474L 右da侧移 Right3move <380 ", Ycenter)
                        action_append("Right3move")
                    else:
                        print("448L 右侧移 Right02move <400 ", Ycenter)
                        action_append("Right02move")
                else:
                    dis_ok_count
                    print("444L 右看 X位置ok")
                    cv2.destroyAllWindows()
                    break

        elif step == 3:
            print("157L 向左看 HeadTurn180")
            action_append("HeadTurn180")
            time.sleep(1)  # timefftest
            step = 4
        elif step == 4:
            if not see:  # not see the edge
                print("294L 左侧 看不到黑线  转为右看")
                headTURN += 1
                if headTURN > 5:
                    headTURN = 0
                    print("error 两侧都看不到  右侧移 Right3move")
                    action_append("Right3move")
            else:  # 0 +-1
                headTURN = 0
                if L_R_angle > 3:
                    if L_R_angle > 8:
                        print("304L 左da旋转 turn001L  ", L_R_angle)
                        action_append("turn001L")
                    else:
                        print("304L 左旋转 turn000L  ", L_R_angle)
                        action_append("turn000L")
                    # time.sleep(1)   # timefftest
                elif L_R_angle < -3:
                    if L_R_angle < -8:
                        print("307L 右da旋转  turn001R  ", L_R_angle)
                        action_append("turn001R")
                    else:
                        print("307L 右旋转  turn000R  ", L_R_angle)
                        action_append("turn000R")
                    # time.sleep(1)   # timefftest
                elif Ycenter >= 430:
                    if Ycenter > 450:
                        print("498L 右da侧移 Right3move  ", L_R_angle)
                        action_append("Right3move")
                    else:
                        print("501L 右侧移 Right02move  ", L_R_angle)
                        action_append("Right02move")
                elif Ycenter < 390:
                    if Ycenter < 370:
                        print("497L 左da侧移 Left3move  ", L_R_angle)
                        action_append("Left02move")
                    else:
                        print("500L 左侧移 Left02move  ", L_R_angle)
                        action_append("Left02move")
                else:
                    dis_ok_count
                    print("495L 左看 X位置ok")

                    cv2.destroyAllWindows()
                    break

def getAreaMaxContour(contours):
    contour_area_temp = 0
    contour_area_max = 0
    area_max_contour = None
    #area_max_contour = np.array([[[0, 0]], [[0, 1]], [[1, 1]], [[1, 0]]])
    for c in contours:  # 历遍所有轮廓
        contour_area_temp = math.fabs(cv2.contourArea(c))  # 计算轮廓面积
        if contour_area_temp > contour_area_max:
            contour_area_max = contour_area_temp
            if contour_area_temp > 25:  #只有在面积大于25时，最大面积的轮廓才是有效的，以过滤干扰
                area_max_contour = c
    return area_max_contour, contour_area_max  # 返回最大的轮廓



def bridge_choose(r_w, r_h):
    # 10.16 16:00
    global ChestOrg_img
    while ChestOrg_img is not None:
        Corg_img = ChestOrg_img.copy()
        Corg_img = np.rot90(Corg_img)
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
            print('this is a blue bridge')
            return 1
        else:
            print('this is a green bridge')
            return 0

##################################################第八关：过洞##################################################
def square_hole():
    global  state, state_sel, step, reset, skip, debug, ChestOrg_img

    r_w = chest_r_width
    r_h = chest_r_height
    state_sel = 'hole'
    hole_color = bridge_choose(r_w, r_h)
    step = 0
    state = 8
    while state == 8:  # 初始化
        if ChestOrg_img is None:
            continue
        # 开始处理图像
        if True:  # head发现黄色区域
            t1 = cv2.getTickCount()

            ChestOrg_copy = np.rot90(ChestOrg_img)
            ChestOrg_copy[0:200,:] = 0
            ChestOrg_copy[600:680,:] = 0
            #ChestOrg_copy[:,0:20] = 0
            #ChestOrg_copy[:,460:480] = 0
            #ChestOrg_copy = ChestOrg_copy.copy()
            # ChestOrg_img = cv2.imread('E:\\pic\\09172.PNG')
            # ChestOrg_img = cv2.resize(ChestOrg_img, (640, 480))
            # ChestOrg_copy = np.rot90(ChestOrg_img)
            # ChestOrg_copy = ChestOrg_copy.copy()
            #cv2.rectangle(ChestOrg_copy, (0, 580), (480, 640), (0, 0, 0), -1)  # 底部涂白，遮盖双脚
            handling = cv2.resize(ChestOrg_copy, (480, 640), interpolation=cv2.INTER_CUBIC)  # 将图片缩放
            #handling = ChestOrg_copy.copy()
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
                #print('rect:',rect)
                box = np.int0(cv2.boxPoints(rect))  # 最小外接矩形的四个顶点
                #print('box',box)
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
                    print('ratio:',ratio)
                    print('area_temp',area_temp)
                    tiaojian1 = ((ratio > 0.25) and (ratio < 4) and (area_temp > 1000) and (step > 2))
                    tiaojian2 = ((ratio > 0.25) and (ratio < 4) and (area_temp > 1000) and (area_temp < 10000) and (
                            step <= 2))
                    print('tiaojian1,tiaojian2:',tiaojian1,' ### ',tiaojian2)
                    if  tiaojian1 or tiaojian2:
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

            
        if action_DEBUG == False:
            if step == 0:  # 依据yellow调整左右位置  到接触黑色
                if bottom_center_y > 320:  # 黑色方框
                    print("进入step 1,当前中心坐标： ", bottom_center_x, bottom_center_y)
                    step = 1
                elif bottom_center_x < 200:
                    print("向左移动 Left02move,当前中心坐标： ", bottom_center_x, bottom_center_y)
                    time.sleep(1)
                    action_append("Left02move")
                elif bottom_center_x > 280:
                    print("向右移动 Right02move,当前中心坐标： ", bottom_center_x, bottom_center_y)
                    time.sleep(1)
                    action_append("Right02move")
                else:
                    print("继续前进,当前底部坐标： ", bottom_center_x, bottom_center_y)
                    action_append("forwardSlow0403")

            elif step == 1:  # 看黑色下顶点,调整方向和位置
                # angle
                print("进入step1,当前中心坐标： ", bottom_center_x, bottom_center_y)

                if angle_bottom < -2.0:  # 右转
                    if angle_bottom < -6.0:  # 大右转
                        print("Black_angle_bottom < -6 右转 turn001R,当前底部角度为： ", angle_bottom)
                        action_append("turn001R")
                    elif angle_bottom < -6.0:  # 大右转
                        print("Black_angle_bottom < -4 右转 turn001R,当前底部角度为：  ", angle_bottom)
                        action_append("turn001R")
                    else:
                        print("Black_angle_bottom < -2 右转 turn000R,当前底部角度为：  ", angle_bottom)
                        action_append("turn000R")

                    # time.sleep(1)   # timefftest
                elif angle_bottom > 2.0:  # 左转
                    if angle_bottom > 6.0:  # 大左转
                        print("Black_angle_bottom > 6 大左转 turn001L,当前底部角度为：  ", angle_bottom)
                        action_append("turn001L")
                    elif angle_bottom > 6.0:  # 大左转
                        print("Black_angle_bottom > 4 大左转 turn001L,当前底部角度为：  ", angle_bottom)
                        action_append("turn001L")
                    else:
                        print("Black_angle_bottom > 2 左转 turn000L,当前底部角度为：  ", angle_bottom)
                        action_append("turn000L")

                    # time.sleep(1)   # timefftest
                # x 225 # 240
                elif bottom_center_x > 235:  # 小右移 249.6
                    if bottom_center_x > 245:  # 大右移
                        print("bottom_center_x > 0.54 大右移 Right02move，当前中心点x坐标为：  ", bottom_center_x)
                        time.sleep(1)
                        action_append("Right02move")
                        if bottom_center_y > 420:
                            action_append('Back2Run')
                    else:
                        print("bottom_center_x > 0.54 小右移 Right1move，当前中心点x坐标为：   ", bottom_center_x)
                        time.sleep(1)
                        action_append("Right1move")
                        if bottom_center_y > 420:
                            action_append('Back2Run')
                elif bottom_center_x < 215:  # 小左移 230.4
                    if bottom_center_x < 205:  # 大左1移
                        print("bottom_center_x < 0.48 大左移 Left02move，当前中心点x坐标为：   ", bottom_center_x)
                        time.sleep(1)
                        action_append("Left02move")
                        if bottom_center_y > 420:
                            action_append('Back2Run')
                    else:
                        print("bottom_center_x < 0.48 小左移 Left1move，当前中心点x坐标为：   ", bottom_center_x)
                        time.sleep(1)
                        action_append("Left1move")
                        if bottom_center_y > 420:
                            action_append('Back2Run')
                # y
                if bottom_center_y > 370:
                    print("进入step 2")
                    step = 2
                elif bottom_center_y <= 320:
                    print("383L 继续往前挪动 forwardSlow0403")  # <480 Forwalk01
                    action_append("forwardSlow0403")
                elif bottom_center_y <= 340:
                    print("继续往前挪动 Forwalk01,当前中心坐标： ", bottom_center_x, bottom_center_y)  # Forwalk01
                    action_append("Forwalk01")
                else:
                    print("继续往前挪动 Forwalk00,当前中心坐标： ", bottom_center_x, bottom_center_y)
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

                if bottom_center_y < 390:  # 小步前挪
                    print("2627L  Black_bottom_center_y < 500 小步前挪 Forwalk01")
                    action_append("Forwalk01")
                elif bottom_center_y < 420:  # 小步前挪
                    print("2630L  Black_bottom_center_y < 560 小步前挪 Forwalk00")
                    action_append("Forwalk00")
                elif bottom_center_y >= 460:
                    print("417L  Black_bottom_center_y > 580 后退一点点 Back0Run")
                    action_append("Back1Run")
                elif 420 <= bottom_center_y <= 460:
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
                        time.sleep(1)
                        action_append("Right02move")
                    else:
                        print("小右移 当前中心点x坐标为：   ", bottom_center_x)
                        time.sleep(1)
                        action_append("Right1move")
                elif bottom_center_x < 215:  # 小左移 230.4
                    if bottom_center_x < 205:  # 大左1移
                        print("大左移 当前中心点x坐标为：   ", bottom_center_x)
                        time.sleep(1)
                        action_append("Left02move")
                    else:
                        print("小左移 当前中心点x坐标为：   ", bottom_center_x)
                        time.sleep(1)
                        action_append("Left1move")
                elif 215 < bottom_center_x < 235:
                    action_append("Stand")
                    #action_append("lieForward")
                    time.sleep(1)
                    action_append("Right02move")
                    time.sleep(1)
                    action_append("Right02move")
                    time.sleep(1)
                    action_append("Right02move")
                    time.sleep(1)
                    action_append("Right02move")
                    time.sleep(1)
                    action_append("Right02move")
                    time.sleep(1)
                    action_append("Right02move")
                    time.sleep(1)
                    action_append("Right02move")
                    time.sleep(1)
                    action_append("Right02move")
                    print("进入step4")
                    step = 4
                
                
                
                
            elif step==4:   
                print("进入step4,当前中心坐标： ", bottom_center_x, bottom_center_y)
                if angle_bottom < -32.0:  # 右转
                    if angle_bottom < -35.0 :  # 大右转
                        print("大右转 turn001R,当前底部角度为： ", angle_bottom)
                        action_append("turn001R")
                    else:
                        print("右转 turn000R,当前底部角度为：  ", angle_bottom)
                        action_append("turn000R")

                    # time.sleep(1)   # timefftest
                elif angle_bottom > -28.0 : # 左转
                    if angle_bottom > -25.0 :  # 大左转
                        print("大左转 turn001L,当前底部角度为：  ", angle_bottom)
                        action_append("turn001L")
                    else:
                        print("左转 turn000L,当前底部角度为：  ", angle_bottom)
                        action_append("turn000L")
                
                
                
                action_append("Stand")
                action_append("fastForward04")
                action_append("Stand")
                time.sleep(1)
                action_append("Left02move")
                time.sleep(1)
                action_append("Left02move")
                time.sleep(1)
                action_append("Left02move")
                time.sleep(1)
                action_append("Left02move")
                time.sleep(1)
                action_append("Left02move")
                time.sleep(1)
                action_append("Left02move")
                time.sleep(1)
                #######################
                #action_append("turn001L")
                #######################
                action_append("Left02move")
                time.sleep(1)
                action_append("Left02move")


                print("成功过关啦 ")
                action_append("Stand")
                # action_append("forwardSlow0403")
                # action_append("forwardSlow0403")
                # action_append("forwardSlow0403")
                # action_append("Stand")

                cv2.destroyAllWindows()
                break
        else:
            print(angle_bottom, bottom_center_x, bottom_center_y)

square_hole()
