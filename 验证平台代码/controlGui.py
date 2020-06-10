import tkinter
from tkinter import ttk
from tkinter import messagebox


class ControlGui(tkinter.Toplevel):
    def __init__(self,root,vertexes,control_func):
        tkinter.Toplevel.__init__(self, root)
        self.vertexes=vertexes
        self.control_func=control_func#回调函数，用于进行控制
        self.title("参数控制")
        self.protocol("WM_DELETE_WINDOW", self.hide) # 关闭窗口时隐藏窗口而不关闭
        self.showing=True
        self.input,self.input_guis=self.generateInputGuis()
        self.verify_button=tkinter.Button(self,text='verify',command=self.verify)
        self.verify_button.grid(column=1,row=2)

    def generateInputGuis(self):
        input_list=['controlTarget','action','actionTarget']
        input=[]
        input_guis=[]
        for i in range(len(input_list)):
            tkinter.Label(self,text=input_list[i]).grid(column=i,row=0)
            text = tkinter.StringVar()
            combobox= ttk.Combobox(self, width=12, textvariable=text,state='readonly')
            input.append(text)
            input_guis.append(combobox)
            if i ==0:
                combobox['values']=list(range(len(self.vertexes)))
                combobox.bind("<<ComboboxSelected>>", self.changeControlTarget)
            elif i==1:
                combobox['values'] = ['attack']
            combobox.grid(column=i,row=1)
        return input,input_guis

    def changeControlTarget(self,event):
        target_index=int(self.input[0].get())
        self.input_guis[2]['values']=self.vertexes[target_index].edges
        self.input[2].set("")

    def verify(self):
        control_target_index=self.input[0].get()
        if not control_target_index:
            messagebox.showerror('错误', "控制对象不能为空!")
            return
        action=self.input[1].get()
        if not action:
            messagebox.showerror('错误', "行动内容不能为空!")
            return
        action_target_index=self.input[2].get()
        if not action_target_index:
            messagebox.showerror('错误', "行动目标不能为空!")
            return
        self.control_func(int(control_target_index),action,int(action_target_index))

    # 每个周期调用以更新显示内容
    def periodicExecution(self, vertexes):
        self.vertexes=vertexes

    def hide(self):
        self.showing = False
        self.withdraw()

    def show(self):
        self.showing = True
        self.update()
        self.deiconify()