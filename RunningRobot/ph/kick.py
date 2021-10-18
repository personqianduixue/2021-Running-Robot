#!/usr/bin/env python3
# coding:utf-8
# Opencv 3.4
# 第七关踢球进洞
#640*480

import sys

sys.path.append('./PyTorch-YOLOv3-master/pytorchyolo')

import detect, models

import cv2
import math
import numpy as np
import threading


import time

import CMDcontrol


#################################################初始化#########################################################
camera_out = "chest"
'''stream_head = "http://192.168.137.2:8082/?action=stream?dummy=param.mjpg"
cap_head = cv2.VideoCapture(stream_head)
stream_chest = "http://192.168.137.2:8080/?action=stream?dummy=param.mjpg"
cap_chest = cv2.VideoCapture(stream_chest)'''
cap_chest = cv2.VideoCapture(0)
cap_head = cv2.VideoCapture(2)  
# Running = False
Running = True
debug = False
state = 1
step = 0
# state_sel = None
state_sel = 'floor'
reset = 0
skip = 0
#初始化头部舵机角度

chest_ret = False     # 读取图像标志位
ret = False     # 读取图像标志位
ChestOrg_img = None  # 原始图像更新
HeadOrg_img = None  # 原始图像更新


HeadOrg_copy = None
picnum = 0
debug_pic = False
################################################读取图像线程#################################################
def get_img():
    global ChestOrg_img,HeadOrg_img,HeadOrg_img
    global ret
    global Running
    global cap_chest
    while True:
        if cap_chest.isOpened():
        # if False:
            chest_ret, ChestOrg_img = cap_chest.read()
            
            ret, HeadOrg_img = cap_head.read()
            if HeadOrg_img is None:
                print("HeadOrg_img error")
            if ChestOrg_img is None:
                print("ChestOrg_img error")
            if chest_ret == False:
                print("chest_ret faile ------------------")
        else:
            time.sleep(0.01)
            #ret=True
            print("58L pic  error ")

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

    # print("执行动作名：",act_name)
    # time.sleep(3) # fftest




# cv2.namedWindow("hole_mask",cv2.WINDOW_NORMAL)
# cv2.resizeWindow("hole_mask", 640, 480)
# cv2.moveWindow("hole_mask",150,0) # left top

#cv2.namedWindow("Hole_OrgFrame",cv2.WINDOW_NORMAL)
#cv2.resizeWindow("Hole_OrgFrame", 480, 640)
#cv2.moveWindow("Hole_OrgFrame",350,530) # left top

# cv2.namedWindow("ball_mask",cv2.WINDOW_NORMAL)
# cv2.resizeWindow("ball_mask", 640, 480)
# cv2.moveWindow("ball_mask",800,0) # left top

#cv2.namedWindow("Ball_OrgFrame",cv2.WINDOW_NORMAL)
#cv2.resizeWindow("Ball_OrgFrame", 480, 640)
#cv2.moveWindow("Ball_OrgFrame",800,530) # left top






################################################第七关：踢球进洞########################################



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



golf_angle_ball = 90
Chest_ball_angle = 90
hole_Angle = 45
golf_angle = 0
Chest_ball_x = 0
Chest_ball_y = 0
golf_dis_flag = False   #未使用
golf_angle_flag = False
golf_dis_start = True
golf_angle_start = False
golf_ok = False
hole_flag = False
Chest_ball_flag = False
Chest_golf_angle = 0

ball_dis_start = True
hole_angle_start = False

head_state = 0      # 90 ~ -90      左+90   右-90   

hole_x = 0
hole_y = 0

angle_dis_count = 0

def act_move():
    global step, state, reset, skip
    global hole_Angle,ball_hole
    global golf_angle_ball, golf_angle ,Chest_ball_angle ,Chest_golf_angle
    global hole_x, hole_y, Chest_ball_x, Chest_ball_y
    global golf_angle_flag, golf_dis_flag   #golf_dis_flag未使用
    global golf_angle_start, golf_dis_start
    global golf_ok
    global hole_flag,Chest_ball_flag
    global ball_dis_start,hole_angle_start
    global head_state, angle_dis_count
    ball_hole_angle_ok = False


        # 由脚底到红球延伸出一条射线，依据球洞与该射线的关系，调整机器人位置
        # ball_hole_local()

    if True:
        if step == 0:   # 发现球，发现球洞，记录球与球洞的相对位置
            # print("看黑线调整居中")
            if Chest_ball_flag == True:   # 前进到球跟前
                if Chest_ball_y <= 310:  # 340
                    print("226L 快走前进 fastForward05 ",Chest_ball_y)
                    # action_append("forwardSlow0403")
                    # action_append("forwardSlow0403")
                    action_append("fastForward05")
                elif 310< Chest_ball_y <380:   # 390
                    # X
                    if Chest_ball_x < 140:  # 240 - 100
                        print("159L Chest_ball_x < 180 左侧移 ",Chest_ball_x)
                        action_append("Left3move")
                    elif Chest_ball_x > 340:    # 240 + 100
                        print("161L Chest_ball_x > 300 右侧移 ",Chest_ball_x)
                        action_append("Right3move")
                    else:
                        print("168L 前挪一点点 1111111 ",Chest_ball_y)
                        action_append("forwardSlow0403")
                else: # Chest_ball_y>380
                    print("goto step 1")
                    step = 1
            else:
                print("183L 未发现红球  左右旋转头部摄像头 寻找红球")
                print("238L 前进")
                # 目前假设红球在正前方，能看到
                
                # if head_state == 0:
                #     print("头右转(-60)寻找球")
                #     head_state = -60
                # elif head_state == -60:
                #     print("头由右转变为左转(+60)寻找球")
                #     head_state = 60
                # elif head_state == 60:
                #     print("头部 恢复0 向前迈进")
                
        elif step == 1:     # 看球调整位置   逐步前进调整至看球洞
            if Chest_ball_y <= 350:
                print("174L 前挪一点点 Forwalk00 < 380 ",Chest_ball_y)
                action_append("Forwalk00")
            elif Chest_ball_y > 480:
                print("177L 后一步 Back2Run > 480",Chest_ball_y)
                action_append("Back2Run")
            elif 350< Chest_ball_y <= 480:
                
                if hole_flag == True:
                    if head_state == -60:
                        print("头右看，看到球洞")
                        step = 2
                        # print("172L 头恢复0 向右平移")
                        # head_state = 0
                    elif head_state == 60:
                        print("头左看，看到球洞")
                        step = 3
                        # print("172L 头恢复0 向左平移")
                        # head_state = 0
                    elif head_state == 0:     # 头前看 看到球洞
                        print("270L step4")
                        step = 4
                else:
                    print("273error 左右旋转头 寻找球洞")
                    # 目前假设球洞在前方，head能看到
                
                    # if head_state == 0:
                    #     print("头右转(-60)寻找球")
                    #     head_state = -60
                    # elif head_state == -60:
                    #     print("头由右转变为左转(+60)寻找球")
                    #     head_state = 60
                    # elif head_state == 60:
                    #     print("头部 恢复0 向前迈进")
      
        elif step == 2:
            # 红球与球洞都找到     chest看球调整位置
            print("22222222222找到了红球与球洞")
            if Chest_ball_y < 160:
                print("174L 一大步前进")

            elif Chest_ball_y < 360:  
                print("177L 后挪一点点")
            elif 160< Chest_ball_y < 320:
                print("找到了在左边跳第4步，找到了在右边跳第3步")

                if hole_flag == True:
                    if head_state == -60:
                        print("头右看，看到球")
                        step = 3
                        # print("172L 头恢复0 向右平移")
                        # head_state = 0
                    elif head_state == 60:
                        print("头左看，看到球")
                        step = 4
                        # print("172L 头恢复0 向左平移")
                        # head_state = 0
                    elif head_state == 0:     # 头前看 看到球洞
                        step = 1
                else:
                    print("左右旋转头 寻找球洞")
                    # 目前假设球洞在前方，head能看到
                
                    if head_state == 0:
                        print("头右转(-60)寻找球")
                        head_state = -60
                    elif head_state == -60:
                        print("头由右转变为左转(+60)寻找球")
                        head_state = 60
                    elif head_state == 60:
                        print("头部 恢复0 向前迈进")

        elif step == 3:
            print("33333333333左侧移")
            if Chest_ball_y > 280:
                print("后挪一点点")
            elif Chest_ball_y < 150:
                print("前挪一点点")
            elif Chest_ball_x < 450:
                print("左侧移")
            
            if hole_flag == False:
                print("右转")
            else:
                step = 1
                ball_dis_start = True
                hole_angle_start = False
            # 完成左侧移后 右转
            # 找球洞
        
        



        elif step == 4:  # 粗略调整朝向   球与球洞大致在一条线
            # print("调整红球在左脚正前方不远处，看球洞的位置调整")
            if ball_dis_start:
                if Chest_ball_x <= 200:
                    if 240 - Chest_ball_x > 40:
                        print("373L4 需要左侧移 Left3move", Chest_ball_x)
                        action_append("Left3move")
                    else:
                        print("376L4 需要左侧移 Left02move", Chest_ball_x)
                        action_append("Left02move")
                    angle_dis_count = 0
                elif Chest_ball_x > 280:
                    if Chest_ball_x - 240 > 40:
                        print("359L4 需要右侧移 Right3move", Chest_ball_x)
                        action_append("Right3move")
                    else:
                        print("384L4 需要右侧移 Right02move", Chest_ball_x)
                        action_append("Right02move")
                    angle_dis_count = 0
                else:
                    print("388L4 Chest_ball_y---位置ok")
                    ball_dis_start = False
                    hole_angle_start = True
            if hole_angle_start:
                if hole_Angle <= 0:
                    # angle
                    if hole_Angle > -86:
                        if hole_Angle >= -82:
                            if Chest_ball_y > 480:
                                print("392L4 需要后挪一点 Back2Run ",Chest_ball_y)
                                action_append("Back2Run")
                                angle_dis_count = 0
                            elif Chest_ball_y < 350:
                                print("395L4 需要前挪一点 Forwalk00",Chest_ball_y)
                                action_append("Forwalk00")
                                angle_dis_count = 0

                            print("381L4 大左转一下  turn003L ", hole_Angle)
                            action_append("turn003L")
                        else:
                            if Chest_ball_y > 485:
                                print("386L4 需要后挪一点 Back1Run ",Chest_ball_y)
                                action_append("Back1Run")
                                angle_dis_count = 0
                            elif Chest_ball_y < 350:
                                print("427L4 需要前挪一点 Forwalk00 ",Chest_ball_y)
                                action_append("Forwalk00")
                                angle_dis_count = 0
                                
                            print("397L4 左转一下  turn003L ", hole_Angle)
                            action_append("turn003L")
                    else:
                        print("401L4 hole_Angle---角度ok")
                        angle_dis_count = angle_dis_count + 1
                        ball_dis_start = True
                        hole_angle_start = False

                    # ball_dis_start = True
                    # hole_angle_start = False
                if hole_Angle >0:
                    # angle
                    if hole_Angle < 86:
                        if hole_Angle <= 82:
                            if Chest_ball_y > 480:
                                print("409L4 需要后挪一点 Back2Run ",Chest_ball_y)
                                action_append("Back2Run")
                                angle_dis_count = 0
                            elif Chest_ball_y < 350:
                                print("427L4 需要前挪一点 Forwalk00 ",Chest_ball_y)
                                action_append("Forwalk00")
                                angle_dis_count = 0

                            print("250L4 大右转一下 turn003R ", hole_Angle)
                            action_append("turn003R")
                        else:
                            if Chest_ball_y > 485:
                                print("421L4 需要后挪一点 Back1Run ",Chest_ball_y)
                                action_append("Back1Run")
                                angle_dis_count = 0
                            elif Chest_ball_y < 350:
                                print("427L4 需要前挪一点 Forwalk00 ",Chest_ball_y)
                                action_append("Forwalk00")
                                angle_dis_count = 0

                            print("352L4 右转一下 turn003R ", hole_Angle)
                            action_append("turn003R")
                    else:
                        print("417L4 hole_Angle---角度OK")         
                        angle_dis_count = angle_dis_count + 1
                        ball_dis_start = True
                        hole_angle_start = False

                    # ball_dis_start = True
                    # hole_angle_start = False

                if angle_dis_count > 3:
                    angle_dis_count = 0
                    print("step step 5555")
                    step = 5

        elif step == 5:  # 调整 球与球洞在一条直线    球范围  230<Chest_ball_y<250
            # print("55555 球与球洞都在")
            # print("调整红球在左脚正前方不远处，看球洞的位置调整")
            if ball_dis_start:  # 390<y<450  230<x<250
                if Chest_ball_x < 220:
                    # if 240 - Chest_ball_x > 40:
                    #     print("443L 需要左侧移 Left02move")
                    #     action_append("Left02move")
                    # else:
                    print("446L 需要左侧移 Left1move", Chest_ball_x)
                    action_append("Left1move")
                    angle_dis_count = 0
                elif Chest_ball_x > 260:
                    # if Chest_ball_x - 240 > 40:
                    #     print("451L 需要右侧移 Right02move")
                    #     action_append("Right02move")
                    # else:
                    print("454L 需要右侧移 Right1move", Chest_ball_x)
                    action_append("Right1move")
                    angle_dis_count = 0
                else:
                    print("340L Chest_ball_y---位置ok")
                    ball_dis_start = False
                    hole_angle_start = True
            if hole_angle_start:
                if hole_Angle <0:
                    # angle
                    if hole_Angle > -87:
                        # y
                        if Chest_ball_y > 485:
                            print("475L 需要后挪一点 Back1Run ",Chest_ball_y)
                            action_append("Back1Run")
                            angle_dis_count = 0
                        elif Chest_ball_y < 390:
                            print("368L 需要前挪一点 Forwalk00",Chest_ball_y)
                            action_append("Forwalk00")
                            angle_dis_count = 0

                        if hole_Angle >= -82:
                            print("465L 大左转一下  turn003L ", hole_Angle)
                            action_append("turn003L")
                        else:
                            print("468L 左转一下  turn001L ", hole_Angle)
                            action_append("turn001L")
                    else:
                        print("471L hole_Angle---角度ok")
                        angle_dis_count = angle_dis_count + 1

                    ball_dis_start = True
                    hole_angle_start = False
                if hole_Angle >0:
                    # angle
                    if hole_Angle < 87:
                        # y
                        if Chest_ball_y > 485:
                            print("475L 需要后挪一点 Back1Run ",Chest_ball_y)
                            action_append("Back1Run")
                            angle_dis_count = 0
                        elif Chest_ball_y < 390:
                            print("368L 需要前挪一点 Forwalk00 ",Chest_ball_y)
                            action_append("Forwalk00")
                            angle_dis_count = 0

                        if hole_Angle <= 82:
                            print("479L 大右转一下 turn003R ", hole_Angle)
                            action_append("turn003R")
                        else:
                            print("482L 右转一下 turn001R ", hole_Angle)
                            action_append("turn001R")
                    else:
                        print("485L hole_Angle---角度OK")               
                        angle_dis_count = angle_dis_count + 1

                    ball_dis_start = True
                    hole_angle_start = False

                if angle_dis_count > 2:
                    angle_dis_count = 0
                    step = 6


        elif step == 6:
            # print("666")
            if Chest_ball_angle > 88 and hole_Angle > 88:
                ball_hole_angle_ok = True
            if Chest_ball_angle < -88 and hole_Angle > 88:
                ball_hole_angle_ok = True
            if Chest_ball_angle < -88 and hole_Angle < -88:
                ball_hole_angle_ok = True
            if Chest_ball_angle > 88 and hole_Angle < -88:
                ball_hole_angle_ok = True

            if Chest_ball_angle > 86 and hole_Angle > 86 and ball_hole_angle_ok == False:
                print("391L 右转一点点 turn001R")
                action_append("turn001R")
            elif Chest_ball_angle < -86 and hole_Angle < -86 and ball_hole_angle_ok == False:
                print("393L 左转一点点 turn001L")
                action_append("turn001L")
            elif Chest_ball_y <= 470:
                print("289L 向前挪动一点点 Forwalk00")
                action_append("Forwalk00")
            else:
                print("next step")
                step = 7

        elif step == 7:
            if Chest_ball_x > 210:
                print("410L 向右移动 Right1move")
                action_append("Right1move")
            elif Chest_ball_x < 180:
                print("412L 向左移动 Left1move")
                action_append("Left1move")
            elif Chest_ball_y < 490:
                print("289L 向前挪动一点点 Forwalk00")
                action_append("Forwalk00")
            else:
                print("414L 踢球踢球 LfootShot")
                action_append("LfootShot")
                step = 8
                print("完成")
                print("please enter ... 000")
                cv2.waitKey(0)
                step = 0

    # 待修改，未完成
 
            


def kick_ball():
    global state, state_sel, step, reset, skip
    global hole_Angle
    global golf_angle_ball, golf_angle ,Chest_ball_angle, Chest_golf_angle
    global hole_x, hole_y,Chest_ball_x, Chest_ball_y
    global hole_flag ,Chest_ball_flag
    global ChestOrg_img, HeadOrg_img
    global picnum,debug_pic

    # 初始化
    hole_chest = None
    ball_chest = None
    hole_head = None
    ball_head = None
    step = 0
    model = models.load_model('./PyTorch-YOLOv3-master/config/yolov3-tiny-custom.cfg',
                          './PyTorch-YOLOv3-master/pytorchyolo/best.weights')   
    while state == 7:
        if 0<=step <= 8: #踢球的六步
            
            HeadOrg = HeadOrg_img.copy()
            head = HeadOrg.copy()
            

            ChestOrg = ChestOrg_img.copy()
            ChestOrg = np.rot90(ChestOrg)
            chest = ChestOrg.copy()
            
            #Hole_OrgFrame = ChestOrg.copy()
            #Ball_OrgFrame = ChestOrg.copy()
            
            

            img_h, img_w = ChestOrg.shape[:2]

            # 把上中心点和下中心点200改为640/2  fftest
            bottom_center = (int(img_w/2), int(img_h))  #图像底中点
            top_center = (int(img_w/2), int(0))     #图像顶中点
            # bottom_center = (int(640/2), int(img_h))  #图像底中点
            # top_center = (int(640/2), int(0))     #图像顶中点
            img_chest = cv2.cvtColor(ChestOrg, cv2.COLOR_BGR2RGB)
            img_head = cv2.cvtColor(HeadOrg, cv2.COLOR_BGR2RGB)
            
            boxes_chest = detect.detect_image(model, img_chest, conf_thres=0.1)
            boxes_head = detect.detect_image(model, img_head, conf_thres=0.1)
            
            for box in boxes_chest:
                
                x1, y1, x2, y2 = int(box[0]), int(box[1]),int(box[2]), int(box[3])
#               cv2.rectangle(ChestOrg, (int(x1),int(y1)), (int(x2),int(y2)), (0,0,255),2)
                cv2.rectangle(chest, (int(x1),int(y1)), (int(x2),int(y2)), (0,0,255),2)
                cv2.putText(chest, str(box[5])+'_'+str(box[4]), (int(x1),int(y1-10)),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),3)
                
            for box in boxes_head:
                x1, y1, x2, y2 = int(box[0]), int(box[1]),int(box[2]), int(box[3])
                cv2.rectangle(head, (int(x1),int(y1)), (int(x2),int(y2)), (0,0,255),2)
                cv2.putText(head, str(box[5])+'_'+str(box[4]), (int(x1),int(y1-10)),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),3)

            for box in boxes_chest:
                if box[5]==1:
                    hole_chest = box
                    
            for box in boxes_head:
                if box[5]==1:
                    hole_head = box
                    
            if hole_head is not None and hole_chest is not None:

                hole_flag = True
                '''for box in boxes:
                    if box[5]==1:
                        hole = box'''
                hole_chest_x, hole_chest_y = int((hole_chest[0]+hole_chest[2])/2), int((hole_chest[1]+hole_chest[3])/2)
                hole_head_x, hole_head_y = int((hole_head[0]+hole_head[2])/2), int((hole_head[1]+hole_head[3])/2)
                
                hole_offset_x = hole_chest_x - hole_head_x
                hole_offset_y = hole_chest_y - hole_head_y
                #print('hole_offset_x:%d,hole_offset_y:%d'%(hole_offset_x, hole_offset_y))
                                
                if (hole_chest_x - bottom_center[0]) == 0:
                    hole_Angle = 90
                else:
                # hole_Angle  (y1-y0)/(x1-x0)
                    hole_Angle = - math.atan(
                        (hole_chest_y - bottom_center[1]) / (hole_chest_x - bottom_center[0])) * 180.0 / math.pi
            else:
                hole_flag = False
                print("没有找到洞")

      # chest 白球处理
            Chest_ball_x = 0
            Chest_ball_y = 0

                                                    
            for box in boxes_chest:
                if box[5]==0:
                    ball_chest = box
            
            for box in boxes_head:
                if box[5]==0:
                    ball_head = box
                    
            if ball_chest is not None and ball_head is not None:
                
                Chest_ball_flag = True
                
                '''for box in boxes:
                    if box[5]==0:
                        ball = box'''

                Chest_ball_x, Chest_ball_y = int((ball_chest[0]+ball_chest[2])/2), int((ball_chest[1]+ball_chest[3])/2)
                
                head_ball_x, head_ball_y = int((ball_head[0]+ball_head[2])/2), int((ball_head[1]+ball_head[3])/2)
                
                ball_offset_x = Chest_ball_x - head_ball_x
                ball_offset_y = Chest_ball_y - head_ball_y
                #print('ball_offset_x:%d,ball_offset_y:%d'%(ball_offset_x, ball_offset_y))
                
                
                if (Chest_ball_x- top_center[0])==0:
                    Chest_ball_angle = 90
                else:
                    Chest_ball_angle = - math.atan((Chest_ball_y - top_center[1]) / (
                                Chest_ball_x - top_center[0])) * 180.0 / math.pi
                
                

            else:
                Chest_ball_flag = False
                print("没有找到ball")
            
            cv2.imshow('img_chest', chest)
            cv2.imshow('img_head', head)

            k = cv2.waitKey(1) & 0xff
            if k == 27:
                cv2.destroyAllWindows()
                    
                    
            #act_move()




if __name__ == '__main__':  
    print("007seven")
    while True:
        if HeadOrg_img is not None and ret:
            k = cv2.waitKey(100)
            if k == 27:
                cv2.destroyWindow('camera_test')
                break

            state= 7
            step = 0
            kick_ball() #过洞
            
        else:
            print('image is empty')
            time.sleep(0.01)
            cv2.destroyAllWindows()
