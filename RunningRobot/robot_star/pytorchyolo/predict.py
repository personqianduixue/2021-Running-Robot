import cv2
import detect, models

model = models.load_model('../config/yolov3-tiny-custom.cfg',
                          'best.weights')

img = cv2.imread('../for_detect/chest_90_10.jpg')

img_1 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

boxes = detect.detect_image(model, img_1, conf_thres=0.1)

for box in boxes:
    x1, y1, x2, y2 = int(box[0]), int(box[1]),int(box[2]), int(box[3])
    cv2.rectangle(img, (int(x1),int(y1)), (int(x2),int(y2)), (0,0,255),2)
    cv2.putText(img, str(box[5])+'_'+str(box[4]), (int(x1),int(y1-10)),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),3)


print(boxes)
cv2.imshow('img', img)
cv2.waitKey(0)