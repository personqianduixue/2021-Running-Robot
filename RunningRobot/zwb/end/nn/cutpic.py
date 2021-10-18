import glob
import cv2
import os

src_dir='./'
save_dir='./save/'
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

for i in range(14):
    filepath=glob.glob(src_dir+str(i+1)+'/*.jpg')
    save_eachdir = save_dir + str(i + 1) + '/'
    if not os.path.exists(save_eachdir):
        os.makedirs(save_eachdir)
    for j in range(len(filepath)):
        img_src=cv2.imread(filepath[j])
        img_new=img_src[160:640, :, :]
        save_eachdir=save_dir+str(i+1)+'/'+str(j+1)+'.jpg'
        cv2.imwrite(save_eachdir,img_new)

