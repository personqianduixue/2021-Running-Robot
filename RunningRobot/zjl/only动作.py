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
            print(act_name,"动作未执行 执行 Stand")
            acted_name = "Forwalk02RS"
        elif act_name != "forwardSlow0403" and (acted_name == "Forwalk02RL" or acted_name == "Forwalk02L"):
            # CMDcontrol.action_list.append("Forwalk02LS")
            # acted_name = act_name
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

####################################################主程序###################################################
if __name__ == '__main__':
    while len(CMDcontrol.action_list) > 0 : # 等待执行完前面的动作再开始主程序
        print("等待启动")
        time.sleep(1)
    action_append("HeadTurnMM") # 头回正？准备动作？

    while True: # 一直循环这个主程序
        
            print("right02 X8")
            action_append("Stand")
            action_append("Right02move")
            action_append("Right02move")
            action_append("Right02move")
            action_append("Right02move")
            action_append("Right02move")
            action_append("Right02move")
            action_append("Right02move")
            action_append("Right02move")
            #action_append("Right02move")
            action_append("Stand")
            action_append("turn001L")
            #action_append("turn001L")
            #action_append("turn001L")
            #action_append("turn001L")
            #action_append("turn001L")
            #action_append("turn001L")
            
            action_append("Stand")
            action_append("fastForward04")
            action_append("Stand")
            action_append("Left02move")
            action_append("Left02move")
            action_append("Left02move")
            action_append("Left02move")
            action_append("Left02move")
            action_append("Left02move")
            #action_append("Left02move")
            #action_append("Left02move")
            #action_append("Left02move")
            action_append("turn001L")
            action_append("turn001L")
            #action_append("turn001L")
            #action_append("turn001L")
            
            
            break

            while(1):
                print("结束")
                time.sleep(10000)
            
       


