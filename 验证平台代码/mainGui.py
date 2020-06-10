import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot,axes,image
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.figure import Figure
from tkinter import *
import numpy as np
import random
import cv2
import os
import datetime
from PIL import Image,ImageTk

import battlefield
from messageGui import MessageGui
from controlGui import ControlGui

random.seed(2)

#图片操作制作背景的函数，暂不需要了
# def generateBackground():
#     try:
#         os.remove('./temp_background.jpg')
#     except:
#         pass
#     background_pic=Image.open('./background.jpg')
#     background_pic.resize((mainGui.WIDTH_HUNDRED_PIXEL_2d*100,mainGui.HEIGHT_HUNDRED_PIXEL*100)
#                           ,Image.BILINEAR)#2d使用的地图背景
#     blank_pic=Image.new(background_pic.mode,(mainGui.WIDTH_HUNDRED_PIXEL*100,mainGui.HEIGHT_HUNDRED_PIXEL*100)
#                         ,(255,255,255))#整体背景
#     blank_pic.paste(background_pic,box=(mainGui.WIDTH_HUNDRED_PIXEL_3d*100,0))
#     blank_pic.save('./temp_background.jpg')


def removePictures():
    img_dir = './pictures/'
    for root, dirs, files in os.walk(img_dir):
        for file in files:
            img_name = os.path.join(img_dir, file)
            os.remove(img_name)

def generateVideo():
    # 图片路径
    img_dir = './pictures/'
    # 输出视频路径
    video_dir = './videos/'+\
                str(datetime.datetime.now().strftime('%c').replace(":","-"))+'.avi'
    print(video_dir)
    # 帧率
    fps = 1
    real_fps=1
    # # 图片尺寸
    img_size = (MainGui.WIDTH_HUNDRED_PIXEL * 100, MainGui.HEIGHT_HUNDRED_PIXEL * 100)
    fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')  # opencv3.0
    videoWriter = cv2.VideoWriter(video_dir, fourcc, fps, img_size)

    for root, dirs, files in os.walk(img_dir):
        for index in range(len(files)):
            img_name = os.path.join(img_dir, str(index)+".jpg")
            frame = cv2.imread(img_name)
            repeat_time=fps/real_fps
            for i in range(int(repeat_time)):
                videoWriter.write(frame)
    videoWriter.release()

def main():
    gui=MainGui()
    gui.go()

class MainGui(object):
    PERIODIC_TIME = 1000  # 每个周期实际的时长，root.after的参数
    DRAW_PERIOD = 1  # 每两次调用画图之间间隔的周期数
    WIDTH_HUNDRED_PIXEL_3d= 4
    WIDTH_HUNDRED_PIXEL_2d= 8
    WIDTH_HUNDRED_PIXEL=WIDTH_HUNDRED_PIXEL_3d+WIDTH_HUNDRED_PIXEL_2d # 整体宽度，单位百像素
    HEIGHT_HUNDRED_PIXEL = 4 #整体高度，单位百像素
    def __init__(self):
        removePictures()
        # generateBackground()
        self.root = Tk()
        self.root.resizable(width=False, height=False)
        self.root.title("主界面")
        self.figure = pyplot.figure(figsize=(self.WIDTH_HUNDRED_PIXEL,self.HEIGHT_HUNDRED_PIXEL))
        self.background_image = matplotlib.image.imread("./background.jpg")
        self.background=self.figure.add_subplot(position=[self.WIDTH_HUNDRED_PIXEL_3d / self.WIDTH_HUNDRED_PIXEL, 0,
                                                self.WIDTH_HUNDRED_PIXEL_2d / self.WIDTH_HUNDRED_PIXEL, 0.99])
        self.background.imshow(self.background_image,extent=
                [0,self.WIDTH_HUNDRED_PIXEL_2d/self.HEIGHT_HUNDRED_PIXEL,0,1])#extent调节长宽比，图像自动居中
        self.background.axis('off')

        # self.figure.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0, hspace=0) #调整子图位置
        self.axes_3d = self.figure.add_subplot(position=[0,0,self.WIDTH_HUNDRED_PIXEL_3d/self.WIDTH_HUNDRED_PIXEL,1]
                                               ,projection='3d')#Axes3D(self.figure)  # 定义画布中的点
        self.axes_2d = self.figure.add_subplot(position=[self.WIDTH_HUNDRED_PIXEL_3d / self.WIDTH_HUNDRED_PIXEL, 0,
                                                self.WIDTH_HUNDRED_PIXEL_2d / self.WIDTH_HUNDRED_PIXEL, 1])
        self.figure.patch.set_alpha(0.0)#设置透明
        self.canvas = FigureCanvasTkAgg(self.figure, self.root)  # figure是定义的图像，root是tkinter中画布的定义位置
        self.canvas.get_tk_widget().grid(column=0, row=0,columnspan=4)
        self.battlefield=battlefield.Battlefield()
        self.messageGui = MessageGui(self.root,self.battlefield.vertexes.copy())
        self.controlGui= ControlGui(self.root,self.battlefield.vertexes.copy(),self.controlAction)
        self.root.protocol("WM_DELETE_WINDOW", lambda: sys.exit(0))#关闭窗口时关闭进程
        self.periodic_count=0
        self.picture_count=0
        self.running=False
        self.buttons = self.createButtons()
        for i in range(len(self.buttons)):
            self.buttons[i].grid(column=i,row=1)
        self.drawCanvas()



    def go(self):
        self.root.after(self.PERIODIC_TIME,self.periodicExecution)
        self.root.mainloop()

    def drawCanvas(self,event=None):
        if self.running:
            self.canvas.print_jpg("./pictures/" + str(self.picture_count) + ".jpg")
            self.picture_count+=1
        self.axes_3d.clear()
        self.axes_2d.clear()
        self.axes_2d.patch.set_alpha(0.0)#设置透明
        # self.axes.axis('off')
        # 关闭坐标轴
        vertexes=self.battlefield.vertexes
        for vertex in vertexes:
            if vertex.state==battlefield.Vertex.EMPTY:
                self.axes_2d.scatter(vertex.x_2d, vertex.y_2d,color='', marker='o', edgecolors='black', s=150)
                self.axes_3d.scatter3D(vertex.x, vertex.y, vertex.z,color='black')
            else:
                if vertex.state==battlefield.Vertex.A_TEAM:
                    color="red"
                elif vertex.state == battlefield.Vertex.B_TEAM:
                    color = "blue"
                self.axes_3d.scatter3D(vertex.x, vertex.y, vertex.z, c=color)
                self.axes_2d.scatter(vertex.x_2d, vertex.y_2d, c=color,s=150)
            self.axes_2d.annotate(str(vertex.id),xy=(vertex.x_2d,vertex.y_2d))
            for edge in vertex.edges:
                if edge>vertex.index:
                    self.axes_3d.plot3D(
                        [vertex.x,vertexes[edge].x],[vertex.y,vertexes[edge].y],
                        [vertex.z,vertexes[edge].z],'black'
                    )
                    if abs(vertex.y_2d-vertexes[edge].y_2d)+abs(vertex.x_2d-vertexes[edge].x_2d)<2:
                        self.axes_2d.plot([vertex.x_2d,vertexes[edge].x_2d],
                                          [vertex.y_2d,vertexes[edge].y_2d],'black')
        self.canvas.draw()


    def periodicExecution(self):
        self.periodic_count += 1
        if self.running:
            self.battlefield.periodicExecution()
            if self.messageGui:
                self.messageGui.periodicExecution(self.battlefield.vertexes.copy())
            if self.controlGui:
                self.controlGui.periodicExecution(self.battlefield.vertexes.copy())
        if self.periodic_count%MainGui.DRAW_PERIOD==0 and self.running:#只有运行中再重画图，减少画图频率
            self.drawCanvas()
        self.root.after(MainGui.PERIODIC_TIME, self.periodicExecution)

    def createButtons(self):
        buttons = []
        buttons.append(Button(self.root, text='start', command=self.startOrPause, width=20, height=5))
        #buttons.append(Tkinter.Button(self.root, text='reset', command=self.reset, width=20, height=5))
        buttons.append(
            Button(self.root, text='outputVedio', command=generateVideo, width=20, height=5)
        )
        buttons.append(
            Button(self.root, text='messageGui', command=self.messageShowOrHide, width=20, height=5)
        )
        buttons.append(
            Button(self.root, text='control', command=self.controlShowOrHide, width=20, height=5)
        )
        return buttons

    def startOrPause(self):
        self.running=not self.running
        if self.running:
            self.buttons[0]['text']='pause'
        else:
            self.buttons[0]['text'] = 'start'
        print('running:'+str(self.running))

    def messageShowOrHide(self):
        if self.messageGui.showing:
            self.messageGui.hide()
        else:
            self.messageGui.show()

    def controlShowOrHide(self):
        if self.controlGui.showing:
            self.controlGui.hide()
        else:
            self.controlGui.show()

    def controlAction(self,control_target_index,action,action_target_index):
        self.battlefield.controlAction(control_target_index,action,action_target_index)
        self.messageGui.periodicExecution(self.battlefield.vertexes.copy())

if __name__=="__main__":
    main()