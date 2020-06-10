文件说明：
一、算法代码文件夹内容：
附录A:
cal_matrix.py 是仅限1v1情形下计算“normal form”的支付矩阵中的每一个元素的值的代码，
用于一致性检验，例如<4,2,2>情形下其输出为一个6x6矩阵。
附录B:
LH.py是使用LH源代码的matlab代码的接口文件，由于LH源代码在健壮性和格式统一上有所不足，
因而编写该文件方便进行调用。
bimat.m即为LH源代码的matlab文件。
bimat_zero.m是适应零和博弈的情形的接口改动，LH.py实际直接调用的文件为此文件。
nash_recurrence.py是最初只适应于1v1的子博弈递推计算的代码。
nash_recurrence_2_2.py是在nash_recurrence.py基础上实现了双方智能体的扩展，
泛用于m v n 的情形，功能上可以完全取代nash_recurrence.py。
附录D:
强化学习代码相关文件。
包括DQN、NashQLearning两个文件中的强化学习代码以及trained_vs_DQN_main.py，shoot_env.py是训练环境代码，
其它代码：
draw_plot.py，主要是绘图和数据统计等功能性函数。
二、验证平台代码文件夹内容：
附录C:
验证平台代码，包括battlefield.py,controlGui.py,mainGui.py,messageGui.py几个文件。


依赖库说明：
由于直接调用matlab文件，需要在安装matlab后，进入 "matlab安装目录\extern\engines\python"目录下，shift+右键打开powershell
之后输入python setup.py install进行安装，即可在python文件中调用matlab文件。
其余应均为python自带的标准库，不需要额外安装，如有遗漏，请根据import错误的位置百度查找对应的库并使用pip install安装。
强化学习相关的代码主要使用TensorFlow和gym库。
验证平台的相关代码使用库包括opencv-python, pillow, matplotlib, tkinter

开源代码说明：
本项目的强化学习部分的源代码参考https://github.com/MorvanZhou/Reinforcement-learning-with-tensorflow