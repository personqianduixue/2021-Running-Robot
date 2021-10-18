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
import data_transform

#宏定义一些数据，如epoch数，batchsize等
MAX_EPOCH=10
BATCH_SIZE=12
LR=0.0001
log_interval=3
val_interval=1

# ============================ step 1/5 数据 ============================
split_dir=os.path.join(".","data","splitData")
train_dir=os.path.join(split_dir,"train")
#valid_dir=os.path.join(split_dir,"valid")

#对训练集所需要做的预处理

add_noise = data_transform.AddGaussNoise(mean=0, var=0.001)
light_augment = data_transform.LightChange(1.3)
light_weak = data_transform.LightChange(0.8)

train_transform_0=transforms.Compose([
    add_noise,
    transforms.Resize((224,224)),
    transforms.ToTensor(),
])

train_transform_1=transforms.Compose([
    light_augment,
    add_noise,
    transforms.Resize((224,224)),
    transforms.ToTensor(),
])

train_transform_2=transforms.Compose([
    light_weak,
    add_noise,
    transforms.Resize((224,224)),
    transforms.ToTensor(),
])

train_transform_3=transforms.Compose([
    transforms.RandomHorizontalFlip(),
    add_noise,
    transforms.Resize((224,224)),
    transforms.ToTensor(),
])


#对验证集所需要做的预处理
'''
valid_transform=transforms.Compose([
   transforms.Resize((224,224)),
   transforms.ToTensor(),
])
'''
# 构建MyDataset实例
train_data_0=myDataset(data_dir=train_dir,transform=train_transform_0)
train_data_1=myDataset(data_dir=train_dir,transform=train_transform_1)
train_data_2=myDataset(data_dir=train_dir,transform=train_transform_2)
train_data_3=myDataset(data_dir=train_dir,transform=train_transform_3)
#valid_data=myDataset(data_dir=valid_dir,transform=valid_transform)

train_data = train_data_0 + train_data_1 + train_data_2 + train_data_3

# 构建DataLoader
# 训练集数据最好打乱
# DataLoader的实质就是把数据集加上一个索引号，再返回
train_loader=DataLoader(dataset=train_data,batch_size=BATCH_SIZE,shuffle=True)
#valid_loader=DataLoader(dataset=valid_data,batch_size=2)

# ============================ step 2/5 模型 ============================
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
net=MobileNetV3_small(num_classes=15)
net.load_state_dict(torch.load('./weights/best.pkl'))
# if torch.cuda.is_available():
#     net.to(device)
# ============================ step 3/5 损失函数 ============================
criterion=nn.CrossEntropyLoss()
# ============================ step 4/5 优化器 ============================
optimizer=optim.Adam(net.parameters(),lr=LR, betas=(0.9, 0.99))# 选择优化器
# ============================ step 5/5 训练 ============================
# 记录每一次的数据，方便绘图
train_curve=list()
#valid_curve=list()
net.train()
accurancy_global= 0.0
for epoch in range(MAX_EPOCH):
    loss_mean=0.
    correct=0.
    total=0.
    running_loss = 0.0



    for i,data in enumerate(train_loader):
        img,label=data
        img = Variable(img)
        label = Variable(label)
        # if torch.cuda.is_available():
        #     img=img.to(device)
        #     label=label.to(device)
        #前向传播
        out=net(img)

        optimizer.zero_grad()  # 归0梯度
        loss=criterion(out,label.long())#得到损失函数

        print_loss=loss.data.item()

        loss.backward()#反向传播
        optimizer.step()#优化
        if (i+1)%log_interval==0:
            print('epoch:{},loss:{:.4f}'.format(epoch+1,loss.data.item()))
        _, predicted = torch.max(out.data, 1)
        total += label.size(0)
        #print("============================================")
        #print("源数据标签：",label)
        #print("============================================")
        #print("预测结果：",predicted)
        # print("相等的结果为：",predicted == label)
        correct += (predicted == label).sum()




    print("============================================")
    accurancy=correct / total

    if accurancy>accurancy_global:
        torch.save(net.state_dict(), './weights/best.pkl')
        print("准确率由：", accurancy_global, "上升至：", accurancy, "已更新并保存权值为weights/best.pkl")
        accurancy_global=accurancy
    print('第%d个epoch的train_data识别准确率为：%d%%' % (epoch + 1, 100*accurancy))

torch.save(net.state_dict(), './weights/last.pkl')
print("训练完毕，权重已保存为：weights/last.pkl")