#!/usr/bin/env python3
# coding:utf-8
# Opencv 3.4
# 第七关踢球进洞
#640*480

import cv2
import math
import numpy as np
import threading
import time

import detect, models

import CMDcontrol


#################################################初始化#########################################################
camera_out = "chest"
#stream_head = "http://192.168.137.8:8082/?action=stream?dummy=param.mjpg"
cap_head = cv2.VideoCapture(2)
#stream_chest = "http://192.168.137.8:8080/?action=stream?dummy=param.mjpg"
cap_chest = cv2.VideoCapture(0)
# Running = False
Running = True
debug = True
FLAG = 6
step = 0

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
            ret=True
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
        # CMDcontrol.action_list.append("Forwalk02RS")
        # acted_name = act_name
        acted_name = "Forwalk02RS"
    elif act_name != "forwardSlow0403" and (acted_name == "Forwalk02RL" or acted_name == "Forwalk02L"):
        # CMDcontrol.action_list.append("Forwalk02LS")
        # acted_name = act_name
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

    # print("执行动作名：",act_name)
    # time.sleep(3) # fftest





################################################第七关：踢球进洞########################################

color_dist1 = {'ball_red': {'Lower': np.array([0, 160, 40]), 'Upper': np.array([190, 255, 255])},
              'blue_hole': {'Lower': np.array([100, 45, 40]), 'Upper': np.array([130, 255, 90])},
              'green': {'Lower': np.array([35, 43, 46]), 'Upper': np.array([77, 255, 255])},
              'black': {'Lower': np.array([0, 0, 0]), 'Upper': np.array([180, 255, 46])},
              'black_obscle': {'Lower': np.array([0, 0, 0]), 'Upper': np.array([180, 255, 60])},
              'black_dir': {'Lower': np.array([0, 0, 0]), 'Upper': np.array([180, 255, 46])},
              'white_ball':[(0, 0, 178), (180, 60, 255)]
              }

color_range = {
    'white_ball': [(0, 0, 183), (180, 33, 255)]
}

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
angle_flag = False
Chest_golf_angle = 0

ball_dis_start = True
hole_angle_start = False

head_state = 0      # 90 ~ -90      左+90   右-90   

hole_x = 0
hole_y = 0
ball_x = 0
ball_y = 0

angle_dis_count = 0

def act_move():
    global step, angle, chest
    global hole_Angle, ball_hole
    global golf_angle_ball, golf_angle ,ball_angle ,Chest_golf_angle
    global hole_x, hole_y, ball_x, ball_y
    global golf_angle_flag, golf_dis_flag   #golf_dis_flag未使用
    global golf_angle_start, golf_dis_start
    global golf_ok
    global hole_flag,Chest_ball_flag, angle_flag
    global ball_dis_start,hole_angle_start
    global head_state, angle_dis_count
    ball_hole_angle_ok = False


    if True:
        if step == 0:   # 发现球,前进到球跟前

            if Chest_ball_flag == True:
                if ball_y <= 300:  # 340
                    print("step0 ball_y <= 300, forwardSlow0403  ", ball_y)
                    # action_append("forwardSlow0403")
                    # action_append("forwardSlow0403")
                    action_append("forwardSlow0403")
                elif 300< ball_y <340:

                    if ball_x > 340:
                        action_append("Right02move")
                        print('ball_x>340 Right02move', ball_x)
                    elif ball_x < 160:  # 240 - 100

                        print("ball_x <160 Left02move ", ball_x)
                        action_append("Left02move")
                    else:
                        print(" 160<ball_x<340 Forwalk01 ", ball_x)
                        action_append("Forwalk01")

                elif 340<ball_y<420: # ball_y>340

                    if ball_x < 160:  # 240 - 100
                        print("ball_x < 160 Left02move ",ball_x)
                        action_append("Left02move")
                    elif ball_x > 340:    # 240 + 100
                        print("ball_x > 340 Right02move ",ball_x)
                        action_append("Right02move")

                    else:
                        print("from step 0 go to step 1")
                        cv2.imwrite('0->1.jpg', chest)
                        step = 1
                else:
                    action_append('Back2Run')
            else:
                print(" 未发现白球  左右旋转头部摄像头 寻找白球")
                print(" step0 Forwalk01")
                action_append("Forwalk01")

                
        elif step == 1:     # ball_y>340, 160<ball_x<340
            if ball_y <= 340:
                print("step1 ball_y< 340 Forwalk01",ball_y)
                action_append("Forwalk01")
            elif ball_y > 420:
                print("step1 ball_y> 420 Back2Run",ball_y)
                action_append("Back2Run")
            elif 340<= ball_y <= 420:
                
                if angle_flag == True:
                    if angle <75 and angle>0:
                        print("洞在球右边")
                        print('from step 1 go to step 2')
                        cv2.imwrite('1->2.jpg', chest)
                        step = 2
                        # print("172L 头恢复0 向右平移")
                        # head_state = 0
                    elif angle >-80 and angle<0:
                        print("洞在球左边")
                        print('from step 1 go to step 3')
                        cv2.imwrite('1->3.jpg', chest)
                        step = 3
                        # print("172L 头恢复0 向左平移")
                        # head_state = 0
                    elif angle>75 or angle<-80:     # 头前看 看到球洞
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
            if ball_y<370:
                action_append("Forwalk01")
                print('step2, ball_y<370 Forwalk01', ball_y)
            elif ball_y>460:
                action_append("Back2Run")
                print('step2, ball_y>460 Back2Run', ball_y)
            elif 370<= ball_y <= 460:
                # 粗调水平位置
                if ball_x<150:
                    action_append('Left02move')
                    print('step2, 370<= ball_y <= 460 ball_x<180 Left02move', ball_x)
                elif ball_x>300:
                    action_append('Right02move')
                    print('step2, 370<= ball_y <= 460 ball_x>300 Right02move', ball_x)
                elif 150<ball_x<300:

                    if angle_flag == True:
                        # 调整球坑之间角度
                        if 0<angle<60:
                            action_append('turn003R')
                            print('step2 0<angle<60 turn003R', angle)
                        elif 60<angle<75:
                            action_append('turn001R')
                            print('step2 angle>60 turn001R', angle)
                        elif angle>75 or angle<-80:
                            # 进一步调整 球水平位置
                            if ball_x<170:
                                action_append('Left02move')
                                print('step2 angle>75 or angle<-80 ball_x<170 Left02move', ball_x)
                            elif ball_x>280:
                                action_append('Right02move')
                                print('step2 angle>75 or angle<-80 ball_x>280 Right02move', ball_x)
                            else:
                                print('from step 2 go to step 5')
                                cv2.imwrite('2->5.jpg', chest)
                                step = 5

                        elif -80<angle<-60:
                            action_append('turn001L')
                            print('step2 -80<angle<-60 turn001L', angle)

                        else:
                            print('from step 2 go to step 3')
                            cv2.imwrite('2->3.jpg', chest)
                            step = 3

                    else:
                        print('step2找不到angle')
                        action_append('Stand')
                        #action_append('Forwalk00')


        elif step == 3: # -80<angle<0 洞在球左边 340< ball_y <= 420 160< ball_x < 360
            if ball_y<370:
                action_append("Forwalk01")
                print('step3 ball_y<370 Forwalk01', ball_y)
            elif ball_y>460:
                action_append("Back2Run")
                print('step3 ball_y>450 Back2Run', ball_y)

            elif 370<= ball_y <= 460:
                # 粗调水平位置
                if ball_x<150:
                    action_append('Left02move')
                    print('step3 370<= ball_y <= 460 ball_x<180 Left02move', ball_x)

                elif ball_x>300:
                    action_append('Right02move')
                    print('step3 370<= ball_y <= 460 ball_x>300 Right02move', ball_x)

                elif 150<ball_x<300:
                    # 调整球和坑之间角度
                    if angle_flag == True:

                        if -60<angle<0:
                            action_append('turn003L')
                            print('step3 150<ball_x<300 -60<angle<0 turn003L', angle)

                        elif -80<angle<-60:
                            action_append('turn001L')
                            print('step3 150<ball_x<300 -80<angle<-60 turn001L', angle)

                        elif angle>75 or angle<-80:
                            # 进一步调整球水平位置
                            if ball_x<170:
                                action_append('Left02move')
                                print('step3 angle>75 or angle<-80 ball_x<170 Left02move', ball_x)
                            elif ball_x>280:
                                action_append('Right02move')
                                print('step3 angle>75 or angle<-80 ball_x>280 Left02move', ball_x)
                            else:
                                print('from step 3 go to step 5')
                                cv2.imwrite('3->5.jpg', chest)
                                step = 5

                        elif 60<angle<75:
                            action_append('turn001R')
                            print('step3 60<angle<75 turn001R', angle)

                        else:
                            print('from step 3 go to step 2')
                            cv2.imwrite('3->2.jpg', chest)
                            step = 2

                    else:
                        print('step3找不到angle')
                        action_append('Stand')
                        #action_append('Forwalk00')



        elif step == 4:  # angle>75 or angle<-80 洞在球前方 340< ball_y <= 420 160< ball_x < 360
            if ball_y<370:
                action_append("Forwalk01")
                print('step4 ball_y<370 Forwalk01', ball_y)

            elif ball_y>460:
                action_append("Back2Run")
                print('step4 ball_y>460 Back2Run', ball_y)

            elif 370<= ball_y <= 460:
                # 粗调水平位置
                if ball_x<170:
                    action_append('Left02move')
                    print('step4 370<= ball_y <= 460 ball_x<170 Left02move', ball_x)

                elif ball_x>280:
                    action_append('Right02move')
                    print('step4 370<= ball_y <= 460 ball_x>280 Right02move', ball_x)

                elif 170<ball_x<280:

                    if angle_flag==True:

                        if 0<angle<75:
                            print('from step 4 go to step 2', angle)
                            cv2.imwrite('4->2.jpg', chest)
                            step = 2
                        elif -80<angle<0:
                            print('from step 4 go to step 3', angle)
                            cv2.imwrite('4->3.jpg', chest)
                            step = 3
                        elif angle>75 or angle< -80:
                            step = 5
                            print('from step 4 go to step 5', angle)
                            cv2.imshow('4->5.jpg', chest)
                    else:
                        print('step4找不到hole')
                        action_append('Stand')
                        #action_append('Forwalk00')


        elif step == 5:  #angle>75 or angle<-80 洞在球前方 370< ball_y <= 450 200< ball_x < 280
            if ball_y<410:
                action_append('Forwalk00')
                print('step5 ball_y<410 Forwalk00', ball_y)
            elif ball_y>480:
                action_append('Back1Run')
                print('step5 ball_y>480 Back1Run', ball_y)
            elif 410<ball_y<480:
                if ball_x>240:
                    action_append('Right1move')
                    print('step5 410<ball_y<480 ball_x>240 Right1move', ball_x)
                elif ball_x<180:
                    action_append('Left1move')
                    print('step5 410<ball_y<480 ball_x<200 Left1move', ball_x)
                elif 180<ball_x<240:

                    if angle_flag == True:

                        if angle>75 or angle<-88:
                            step = 6
                            print('from step5 go to step6', angle)
                            cv2.imwrite('5->6.jpg', chest)
                        elif 60<angle<75:
                            action_append('turn001R')
                            print('step5 180<ball_x<240 60<angle<75 turn001R', angle)
                        elif 0<angle<60:
                            action_append('turn003R')
                            print('step5 180<ball_x<240 0<angle<60 turn003R', angle)
                        elif -88<angle<-70:
                            action_append('turn001L')
                            print('step5 200<ball_x<240 -88<angle<-60 turn001L', angle)
                        elif -70<angle<0:
                            action_append('turn003L')
                            print('step5 200<ball_x<240 -65<angle<0 turn003L', angle)
                    else:
                        print('step5找不到angle')
                        action_append('Stand')

        elif step == 6:  #angle>78 or angle<-86.5 洞在球前方 410< ball_y <= 460 200< ball_x < 240
            if ball_y<430:
                action_append('Forwalk00')
                print('step6 ball_y<430 Forwalk00', ball_y)
            elif ball_y>480:
                action_append('Back1Run')
                print('step6 ball_y>480 Back1Run', ball_y)
            elif 430<ball_y<480:
                if ball_x>220:
                    action_append('Right1move')
                    print('step6 430<ball_y<480 ball_x>220 Right1move', ball_x)
                elif ball_x<200:
                    action_append('Left1move')
                    print('step6 430<ball_y<480 ball_x<200 Left1move', ball_x)
                elif 200<ball_x<220:

                    if angle_flag == True:

                        if angle>78 and angle<87 :
                            step = 7
                            print('from step6 go to step7', angle)
                            cv2.imwrite('6->7.jpg', chest)
                        elif 60<angle<78:
                            action_append('turn001R')
                            print('step6 200<ball_x<220 65<angle<80 turn001R', angle)
                        elif 0<angle<60:
                            action_append('turn003R')
                            print('step6 200<ball_x<220 0<angle<65 turn003R', angle)
                        elif angle<-75 or angle>87:
                            action_append('turn001L')
                            print('step6 200<ball_x<220 angle<-75 or angle>87 turn001L', angle)
                        elif -75<angle<0:
                            action_append('turn003L')
                            print('step6 200<ball_x<220 -65<angle<0 turn003L', angle)
                    else:
                        print('step6找不到angle')
                        action_append('Stand')

        elif step == 7: #angle>85 or angle<-85 洞在球前方 420< ball_y <= 460 210< ball_x < 230
            print('位置已找好')
            action_append('LfootShot')
            step = 8
            cv2.waitKey(0)




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
    i = 21


    while FLAG==6:
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
                cv2.imwrite('./not_found_pic/not_found_'+str(i)+'.jpg', chest)


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
                cv2.imwrite('./not_found_pic/not_found_'+str(i)+'.jpg', chest)

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

            #act_move()
        else:
            print('踢球完成')
            for i in range(4):
                action_append('turn005L')

            action_append('fastForward03')
            break




if __name__ == '__main__':
    print("007seven")
    while True:
        if HeadOrg_img is not None and ret:
            k = cv2.waitKey(100)
            if k == 27:
                cv2.destroyWindow('camera_test')
                break


            step = 0
            kick_ball() #过洞

        else:
            print('image is empty')
            time.sleep(0.01)
            cv2.destroyAllWindows()
