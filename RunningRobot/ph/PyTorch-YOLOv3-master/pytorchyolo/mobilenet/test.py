import sys

sys.path.append('./data')
sys.path.append('./model')

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

split_dir = os.path.join(".", "data", "splitData")
valid_dir = os.path.join(split_dir, "valid")

valid_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

valid_data = myDataset(data_dir=valid_dir, transform=valid_transform)
valid_loader = DataLoader(dataset=valid_data, batch_size=2)

weight_path = './weights/best.pkl'

def detect(mode, num_classes):
    total_v = 0.
    correct_valid = 0.
    if mode=='small':
        net = MobileNetV3_small(num_classes=num_classes)
    if mode=='large':
        net = MobileNetV3_large(num_classes=num_classes)
    net.eval()
    net.load_state_dict(torch.load(weight_path))
    for j,data_v in enumerate(valid_loader):
        img_v, label_v = data_v
        img_v = Variable(img_v)
        label_v = Variable(label_v)
        out_v = net(img_v)
        _, predicted_v = torch.max(out_v.data, 1)
        total_v += label_v.size(0)
        correct_valid += (predicted_v == label_v).sum()
    accurancy_valid = correct_valid / total_v
    print('valid_data识别准确率为：%d%%' % (100 * accurancy_valid))


if __name__=='__main__':
    detect('small', 7)