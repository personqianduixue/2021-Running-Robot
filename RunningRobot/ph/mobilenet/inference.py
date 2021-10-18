import sys


import os
import random
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import torchvision.transforms as transforms
import torch.optim as optim
from matplotlib import pyplot as plt
from dataset import myDataset
from model import MobileNetV3_large
from model import MobileNetV3_small
import torchvision
from torch.autograd import Variable
import cv2
from PIL import Image


# 创建一个检测器类，包含了图片的读取，检测等方法
class Detector(object):
    # netkind为'large'或'small'可以选择加载MobileNetV3_large或MobileNetV3_small
    # 需要事先训练好对应网络的权重
    def __init__(self,net_kind,num_classes=7):
        super(Detector, self).__init__()
        kind=net_kind.lower()
        if kind=='large':
            self.net = MobileNetV3_large(num_classes=num_classes)
        elif kind=='small':
            self.net = MobileNetV3_small(num_classes=num_classes)
        self.net.eval()
        #if torch.cuda.is_available():
        #   self.net.cuda()

    def load_weights(self,weight_path):
        self.net.load_state_dict(torch.load(weight_path))

    # 检测器主体
    def detect(self,weight_path,pic):



        # 先加载权重
        self.load_weights(weight_path=weight_path)
        # 读取图片
        img =Image.fromarray(cv2.cvtColor(pic, cv2.COLOR_BGR2RGB))
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
        ])
        img_tensor = transform(img).unsqueeze(0)
        #if torch.cuda.is_available():
        #   img_tensor=img_tensor.cuda()
        net_output = self.net(img_tensor)
        print(net_output)
        _, predicted = torch.max(net_output.data, 1)
        result = predicted[0].item()
        print("预测的结果为：",result)
        return result




if __name__=='__main__':
    detector=Detector('small',num_classes=15)
    #for i in range(14):
    #   path = os.path.join('.', str(i+1)+'.jpg')
    #   detector.detect('./weights/best.pkl', path)

    #detector.detect('./weights/best.pkl', './18.jpg')