# ###################### 过            门-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-
door_flag = True
Angle = 0
angle_top = 0
Bottom_center_y = 0
Bottom_center_x = 0
Top_center_x = 0
Top_center_y = 0
Top_lenth = 0
camera_choice = "Head"


def door_act_move():
    global step, state, reset, skip
    global door_flag
    global real_test
    global camera_choice
    global Angle, angle_top, Bottom_center_y, Bottom_center_x, Top_center_y, Top_center_x, Top_lenth   
    
    step0_far = 130
    step0_close = 24
    step0_angle_top_R = -8
    step0_angle_top_L = 8
    step0_top_center_x_L = 365
    step0_top_center_x_R = 315
    step0_delta = 30 
    step0_turn_times = 3

    step1_angle_top_L = 3
    step1_angle_top_R = -3
    step1_head_bottom_x_F = 310
    step1_head_bottom_x_B = 340
    step1_delta = 20
    step1_close = 375

    step2_get_close = 5

    if step == 0:  # 接近 看下边沿  角度  Chest_percent > 5
        if door_flag == False:
            print("1346L step=0 什么也没有看到，向左转45° turn005L")
            if real_test:
                action_append("turn005L")
                time.sleep(sleep_time_s)

        elif Top_center_y > 160:
            print("1352L step = 0 距离门很远， 快走靠近 fastForward03 Top_center_y={} > 150".format(Top_center_y))
            if real_test:
                action_append("fast_forward_step")
                action_append("turn001R")
                action_append("fast_forward_step")
                time.sleep(sleep_time_l)

        elif Top_center_y > step0_far:
            print("1360L step = 0 再往前一些，慢走 fast_forward_step Top_center_y={} > {}".format(Top_center_y, step0_far))
            if real_test:
                action_append("fast_forward_step")
                time.sleep(sleep_time_l)

        elif Top_center_y < step0_close:
            print("1366L step = 0 距离门很近了, 后退一点 Back2Run Top_center_y={} < {}".format(Top_center_y, step0_close))
            if real_test:
                action_append("Back2Run")
                time.sleep(sleep_time_l)

        elif angle_top < step0_angle_top_R:
            print("1372L step = 0 方向偏了， 向左转 turn001L  angel_top = {} < {}".format(angle_top, step0_angle_top_R))
            if real_test:
                action_append("turn001L")

        elif angle_top > step0_angle_top_L:
            print("1377L step = 0 方向偏了， 向右转 turn001R  angel_top = {} > {}".format(angle_top, step0_angle_top_L))
            if real_test:
                action_append("turn001R")

        elif Top_center_x > step0_top_center_x_L:
            if Top_center_x > step0_top_center_x_L + step0_delta:
                print("1383L step = 0 站位很偏了， 向右移， Right3move Top_center_x = {} > {}".format(Top_center_x, step0_top_center_x_L+step0_delta))
                if real_test:
                    action_append("Right3move")
                    time.sleep(sleep_time_s)
            else:
                print("1388L step = 0 站位偏了， 向右移， Right2move Top_center_x = {} > {}".format(Top_center_x, step0_top_center_x_L))
                if real_test:
                    action_append("Right02move")
                    time.sleep(sleep_time_s)
        elif Top_center_x < step0_top_center_x_R:
            if Top_center_x < step0_top_center_x_R - step0_delta:
                print("1394L step = 0 站位很偏了， 向左移， Left3move Top_center_x = {} < {}".format(Top_center_x, step0_top_center_x_R - step0_delta))
                if real_test:
                    action_append("Left3move")
                    time.sleep(sleep_time_s)
            else:
                print("1399L step = 0 站位偏了， 向左移， Left02move Top_center_x = {} < {}".format(Top_center_x, step0_top_center_x_R))
                if real_test:
                    action_append("Left02move")
                    time.sleep(sleep_time_s)

        else:
            print("1405L 进入下一阶段， 调整侧身 turn005R x {} HeadTurn185".format(step0_turn_times))
            # cv2.waitKey(0)
            if real_test:
                for i in range(0, step0_turn_times):
                    action_append("turn005R")
                    time.sleep(sleep_time_l)

                # action_append("turn004R")
                # action_append("turn001R")
                # action_append("turn001R")
                action_append("HeadTurn185")
                time.sleep(sleep_time_l)
            step = 1
    
    elif step == 1:
        if Top_lenth < 100:
            print("1421L 歪了！ 左转， 再向右移")
            if real_test:
                action_append("Back1Run")
                action_append("Right02move")

        elif angle_top > step1_angle_top_L or 0 < Angle < 85:
            print("1427L step = 1, 方向偏了， 向右转 turn000R angle_top={} > {}".format(angle_top, step1_angle_top_L))
            if real_test:
                action_append("turn001R")
                time.sleep(sleep_time_l)
        elif angle_top < step1_angle_top_R or -85 < Angle < 0 :
            print("1432L step = 1 方向偏了， 向左转 turn000L angle_top={} < {}".format(angle_top, step1_angle_top_R))
            if real_test:
                action_append("turn001L")
                time.sleep(sleep_time_l)
        
        elif Bottom_center_x < step1_head_bottom_x_F:
            if Bottom_center_x < step1_head_bottom_x_F - step1_delta:
                print("1439L step = 1 站位很靠前了，向后移 Back2Run Bottom_center_x={} < {}".format(Bottom_center_x, step1_head_bottom_x_F - step1_delta))
                if real_test:
                    action_append("Back2Run")
                    time.sleep(sleep_time_s)
            else:
                print("1444L step = 1 站位靠前了，向后移 Back1Run Bottom_center_x={} < {}".format(Bottom_center_x, step1_head_bottom_x_F))
                if real_test:
                    action_append("Back1Run")
                    time.sleep(sleep_time_s)
        
        elif Bottom_center_x > step1_head_bottom_x_B:
            if Bottom_center_x > step1_head_bottom_x_B + step1_delta:
                print("1451L step = 1 站位很靠后了，向前移 Forwalk01 Bottom_center_x={} > {}".format(Bottom_center_x, step1_head_bottom_x_B + step1_delta))
                if real_test:
                    action_append("Forwalk01")
                    time.sleep(sleep_time_s)
            else:
                print("1456L step = 1 站位靠后了，向前移 Forwalk01 Bottom_center_x={} > {}".format(Bottom_center_x, step1_head_bottom_x_B))
                if real_test:
                    action_append("Forwalk01")
                    time.sleep(sleep_time_s)

        elif Bottom_center_y < step1_close:
            print("1462L step = 1, 靠近门, Left3move Bottom_center_y={} < {}".format(Bottom_center_y, step1_close))
            if real_test:
                action_append("Left3move")
                time.sleep(sleep_time_l)
        
        elif Bottom_center_y > step1_close:
            print("1468L 已经接近门了，进入下一阶段，摸黑过门, Bottom_center_y = {} > {}".format(Bottom_center_y, step1_close))
            step = 2

    elif step == 2:
        print("-------/////////////////过门 Left3move x 4")
        # action_append("Back2Run")
        for i in range(0, step2_get_close):
            if real_test:
                action_append("Left3move")
                time.sleep(sleep_time_l)
        # print("向后退一点！ Back1Run")
        # if real_test:
        #     action_append("Back1Run")

        # cv2.waitKey(0)

        for i in range(0, 7):
            if real_test:
                action_append("Left3move")
                if i==3:
                    action_append("turn001R")
                    action_append("turn001R")
                time.sleep(sleep_time_l)

        # cv2.waitKey(0)

        print("完成! ")

        if real_test:
            for i in range(0, step0_turn_times):
                action_append("turn005L")
                time.sleep(sleep_time_l)
            action_append("HeadTurnMM")
            action_append("fast_forward_step")
        
        state = -1


def into_the_door():
    global state_sel, org_img, step, reset, skip, debug, chest_ret, HeadOrg_img, state
    global door_flag
    global camera_choice
    global Angle, angle_top, Bottom_center_y, Bottom_center_x, Top_center_x, Top_center_y, Top_lenth
    step = 0
    state = 5


    r_w = chest_r_width
    r_h = chest_r_height
    

    print("/-/-/-/-/-/-/-/-/-开始过门")

    while(state == 5):
        Area = []
        if camera_choice == "Chest":
            # print("胸部相机")
            chest_OrgFrame = np.rot90(ChestOrg_img)
            Img_copy = chest_OrgFrame.copy()

        elif camera_choice == "Head":
            # print("头部相机")
            Img_copy = HeadOrg_img.copy()
            # Img_copy = cv2.resize(border, (r_w, r_h), interpolation=cv2.INTER_CUBIC)
            # Img_copy = Head_OrgFrame
                    
    
        Frame_gauss = cv2.GaussianBlur(Img_copy, (3, 3), 0)  # 高斯模糊
        Frame_hsv = cv2.cvtColor(Frame_gauss, cv2.COLOR_BGR2HSV)  # 将图片转换到HSV空间
        if camera_choice == "Chest":
            Frame_blue = cv2.inRange(Frame_hsv, color_range['chest_blue_door'][0], color_range['chest_blue_door'][1])  # 对原图像和掩模(颜色的字典)进行位运算
        elif camera_choice == "Head":
            Frame_blue = cv2.inRange(Frame_hsv, color_range['head_blue_door'][0], color_range['head_blue_door'][1])  # 对原图像和掩模(颜色的字典)进行位运算
        Opened = cv2.morphologyEx(Frame_blue, cv2.MORPH_OPEN, np.ones((1, 1), np.uint8))  # 开运算 去噪点
        Closed = cv2.morphologyEx(Opened, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))  # 闭运算 封闭连接
        Closed = cv2.dilate(Closed, np.ones((5, 5), np.uint8), iterations=3)
        if img_debug:
            cv2.imshow("Imask", Closed)

        _, contours, hierarchy = cv2.findContours(Closed, cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)  # 找出轮廓cv2.CHAIN_APPROX_NONE

        if len(contours) == 0:
            print("没有找到门！")
            door_flag = False
        
        else:
            door_flag = True
            for i in range(0,len(contours)):
                #print("len[Chest_contours]={}——i:{}".format(len(Chest_contours), i))
                area = cv2.contourArea(contours[i])
                if 2000 < area < 640 * 480 * 0.45:
                    Area.append((area,i))
                
                # print("area{} = {}".format(i, area))
                # cv2.imshow("Processed", Img_copy)
                # cv2.waitKey(0)
            # cv2.drawContours(Img_copy, contours, -1, (0, 0, 255), 1)

            AreaMaxContour, Area_max = getAreaMaxContour1(contours)


            if step != 2 and camera_choice == "Head":
                Rect = cv2.minAreaRect(AreaMaxContour)
                Box = np.int0(cv2.boxPoints(Rect))

                cv2.drawContours(Img_copy, [Box], -1, (255, 200, 100), 2)

                Top_left = AreaMaxContour[0][0]
                Top_right = AreaMaxContour[0][0]
                Bottom_left = AreaMaxContour[0][0]
                Bottom_right = AreaMaxContour[0][0]
                for c in AreaMaxContour:  # 遍历找到四个顶点
                    if c[0][0] + 1.5 * c[0][1] < Top_left[0] + 1.5 * Top_left[1]:
                        Top_left = c[0]
                    if (r_w - c[0][0]) + 1.5 * c[0][1] < (r_w - Top_right[0]) + 1.5 * Top_right[1]:
                        Top_right = c[0]
                    if c[0][0] + 1.5 * (r_h - c[0][1]) < Bottom_left[0] + 1.5 * (r_h - Bottom_left[1]):
                        Bottom_left = c[0]
                    if c[0][0] + 1.5 * c[0][1] > Bottom_right[0] + 1.5 * Bottom_right[1]:
                        Bottom_right = c[0]

                angle_top = - math.atan(
                    (Top_right[1] - Top_left[1]) / (Top_right[0] - Top_left[0])) * 180.0 / math.pi

                Top_lenth = abs(Top_right[0] - Top_left[0])
                Top_center_x = int((Top_right[0] + Top_left[0]) / 2)
                Top_center_y = int((Top_right[1] + Top_left[1]) / 2)
                Bottom_center_x = int((Bottom_right[0] + Bottom_left[0]) / 2)
                Bottom_center_y = int((Bottom_right[1] + Bottom_left[1]) / 2)

                cv2.circle(Img_copy, (Top_right[0], Top_right[1]), 5, [0, 255, 255], 2)
                cv2.circle(Img_copy, (Top_left[0], Top_left[1]), 5, [0, 255, 255], 2)
                cv2.circle(Img_copy, (Bottom_right[0], Bottom_right[1]), 5, [0, 255, 255], 2)
                cv2.circle(Img_copy, (Bottom_left[0], Bottom_left[1]), 5, [0, 255, 255], 2)
                cv2.circle(Img_copy, (Top_center_x, Top_center_y), 5, [0, 255, 255], 2)
                cv2.circle(Img_copy, (Bottom_center_x, Bottom_center_y), 5, [0, 255, 255], 2)
                cv2.line(Img_copy, (Top_center_x, Top_center_y),
                         (Bottom_center_x, Bottom_center_y), [0, 255, 255], 2)  # 画出上下中点连线
                
                if math.fabs(Top_center_x - Bottom_center_x) <= 1:  # 得到连线的角度
                    Angle = 90
                else:
                    Angle = - math.atan((Top_center_y - Bottom_center_y) / (
                            Top_center_x - Bottom_center_x)) * 180.0 / math.pi


                if img_debug:
                    cv2.putText(Img_copy, "angle_top:" + str(int(angle_top)), (30, 425), cv2.FONT_HERSHEY_SIMPLEX, 0.65,(0, 0, 255), 2)
                    cv2.putText(Img_copy, "Head_bottom_center(x,y): " + str(int(Bottom_center_x)) + " , " + str(int(Bottom_center_y)), (30, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)  # (0, 0, 255)BGR
                    cv2.putText(Img_copy,"Head_top_center(x,y): " + str(int(Top_center_x)) + " , " + str(int(Top_center_y)),(30, 470), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)  # (0, 0, 255)BGR
                    cv2.putText(Img_copy, "Angle:" + str(int(Angle)), (30, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)  # (0, 0, 255)BGR
                    cv2.putText(Img_copy, "Top_lenth:" + str(int(Top_lenth)), (400, 20), cv2.FONT_HERSHEY_SIMPLEX,0.65, (0, 0, 255), 2)  # (0, 0, 255)BGR

        if img_debug:
            cv2.imshow("Processed", Img_copy)
            cv2.waitKey(10)

        door_act_move()
        print("state={}".format(state))

                

        # if len(Area) > 2:
        #     Area = find_two(Area)
        
        # elif len(Area) < 2:
        #     door_found = False
        #     print("没有发现门框,调用头部相机")
        #     camera_choice = "Head"
        #     # cv2.drawContours(Img_copy, Chest_contours[Area[0][1]], -1, (0, 0, 255), 1)

        # if len(Area) == 2:
        #     door_found = True
        #     Chest_rect1 = cv2.minAreaRect(Chest_contours[Area[0][1]])
        #     Chest_box1 = np.int0(cv2.boxPoints(Chest_rect1))
        #     Chest_rect2 = cv2.minAreaRect(Chest_contours[Area[1][1]])
        #     Chest_box2 = np.int0(cv2.boxPoints(Chest_rect2))

        #     cv2.drawContours(Img_copy, [Chest_box1], -1, (255, 200, 100), 2)
        #     cv2.drawContours(Img_copy, [Chest_box2], -1, (255, 200, 100), 2)

        #     Chest_top_left1 = Chest_contours[Area[0][1]][0][0]
        #     Chest_top_right1 = Chest_contours[Area[0][1]][0][0]
        #     Chest_bottom_left1 = Chest_contours[Area[0][1]][0][0]
        #     Chest_bottom_right1 = Chest_contours[Area[0][1]][0][0]
        #     for c in Chest_contours[Area[0][1]]:  # 遍历找到四个顶点
        #         if c[0][0] + 1.5 * c[0][1] < Chest_top_left1[0] + 1.5 * Chest_top_left1[1]:
        #             Chest_top_left1 = c[0]
        #         if (r_w - c[0][0]) + 1.5 * c[0][1] < (r_w - Chest_top_right1[0]) + 1.5 * Chest_top_right1[1]:
        #             Chest_top_right1 = c[0]
        #         if c[0][0] + 1.5 * (r_h - c[0][1]) < Chest_bottom_left1[0] + 1.5 * (r_h - Chest_bottom_left1[1]):
        #             Chest_bottom_left1 = c[0]
        #         if c[0][0] + 1.5 * c[0][1] > Chest_bottom_right1[0] + 1.5 * Chest_bottom_right1[1]:
        #             Chest_bottom_right1 = c[0]
        #     cv2.circle(Img_copy, (Chest_top_right1[0], Chest_top_right1[1]), 5, [0, 255, 255], 2)
        #     cv2.circle(Img_copy, (Chest_top_left1[0], Chest_top_left1[1]), 5, [0, 255, 255], 2)
        #     cv2.circle(Img_copy, (Chest_bottom_right1[0], Chest_bottom_right1[1]), 5, [0, 255, 255], 2)
        #     cv2.circle(Img_copy, (Chest_bottom_left1[0], Chest_bottom_left1[1]), 5, [0, 255, 255], 2)
        #     angle_Right = - math.atan(
        #     (Chest_top_left1[1] - Chest_bottom_left1[1]) / (Chest_top_left1[0] - Chest_bottom_left1[0])) * 180.0 / math.pi


        #     Chest_top_left2 = Chest_contours[Area[1][1]][0][0]
        #     Chest_top_right2 = Chest_contours[Area[1][1]][0][0]
        #     Chest_bottom_left2 = Chest_contours[Area[1][1]][0][0]
        #     Chest_bottom_right2 = Chest_contours[Area[1][1]][0][0]
        #     for c in Chest_contours[Area[1][1]]:  # 遍历找到四个顶点
        #         if c[0][0] + 1.5 * c[0][1] < Chest_top_left2[0] + 1.5 * Chest_top_left2[1]:
        #             Chest_top_left2 = c[0]
        #         if (r_w - c[0][0]) + 1.5 * c[0][1] < (r_w - Chest_top_right2[0]) + 1.5 * Chest_top_right2[1]:
        #             Chest_top_right2 = c[0]
        #         if c[0][0] + 1.5 * (r_h - c[0][1]) < Chest_bottom_left2[0] + 1.5 * (r_h - Chest_bottom_left2[1]):
        #             Chest_bottom_left2 = c[0]
        #         if c[0][0] + 1.5 * c[0][1] > Chest_bottom_right2[0] + 1.5 * Chest_bottom_right2[1]:
        #             Chest_bottom_right2 = c[0]
        #     cv2.circle(Img_copy, (Chest_top_right2[0], Chest_top_right2[1]), 5, [0, 255, 255], 2)
        #     cv2.circle(Img_copy, (Chest_top_left2[0], Chest_top_left2[1]), 5, [0, 255, 255], 2)
        #     cv2.circle(Img_copy, (Chest_bottom_right2[0], Chest_bottom_right2[1]), 5, [0, 255, 255], 2)
        #     cv2.circle(Img_copy, (Chest_bottom_left2[0], Chest_bottom_left2[1]), 5, [0, 255, 255], 2)
        #     angle_Left = - math.atan(
        #     (Chest_top_right2[1] - Chest_bottom_right2[1]) / (Chest_top_right2[0] - Chest_bottom_right2[0])) * 180.0 / math.pi
            
        #     Chest_top_center_x = int((Chest_top_right2[0] + Chest_top_left1[0]) / 2)
        #     Chest_top_center_y = int((Chest_top_right2[1] + Chest_top_left1[1]) / 2)
        #     cv2.circle(Img_copy, (Chest_top_center_x, Chest_top_center_y), 5, [0, 255, 255], 2)

        #     cv2.putText(Img_copy, "Chest_top_center(x,y): " + str(int(Chest_top_center_x)) + " , " + str(
        #     int(Chest_top_center_y)), (30, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)
        #     cv2.putText(Img_copy, "angle_left:" + str(int(angle_Left)), (30, 425), cv2.FONT_HERSHEY_SIMPLEX, 0.65,
        #             (0, 0, 255), 2)  # (0, 0, 255)BGR
        #     cv2.putText(Img_copy, "angle_right:" + str(int(angle_Right)), (30, 460), cv2.FONT_HERSHEY_SIMPLEX,
        #             0.65, (0, 0, 255), 2)