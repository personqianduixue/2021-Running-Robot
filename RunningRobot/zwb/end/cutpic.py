import glob
import cv2
src_dir='./'
save_dir='./save/'
for i in range(15):
    filepath=glob.glob(src_dir+str(i+1)+'/*.jpg')
    for j in range(len(filepath)):
        img_src=cv2.imread(filepath[i])
        img_new=img_src[160:640, :, :]
        save_eachdir=save_dir+str(i+1)+'/'+str(j+1)+'.jpg'
        cv2.imwrite(save_eachdir,img_new)

        