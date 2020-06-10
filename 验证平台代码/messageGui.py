import tkinter
from tkinter import ttk
from battlefield import Vertex

class MessageGui(tkinter.Toplevel):
    def __init__(self,root,vertexes):
        tkinter.Toplevel.__init__(self,root)
        self.title("列表信息")
        self.protocol("WM_DELETE_WINDOW", self.hide)  # 关闭窗口时隐藏窗口而不关闭
        self.showing=True
        self.messageList=[]
        self.statisticsMessage=None
        self.createTreeviews()
        self.A_team_total= 0#A组初始总数
        self.B_team_total = 0#B组初始总数
        for vertex in vertexes:
            if vertex.state==Vertex.A_TEAM:
                self.A_team_total+=1
            elif vertex.state==Vertex.B_TEAM:
                self.B_team_total+=1
        self.A_team_alive=self.A_team_total
        self.B_team_alive=self.B_team_total

        self.periodicExecution(vertexes)

    def createTreeviews(self):
        column = ['id', 'last_action', 'action_to_do']
        for index in range(3):
            self.messageList.append(ttk.Treeview(self, height=20, show="headings", columns=column))
            for i in range(len(column)):
                self.messageList[index].column(str(i), width=90, anchor='center')
                self.messageList[index].heading(str(i), text=str(column[i]))
                self.messageList[index].tag_configure(tagname='red', background='red', foreground='white')
                self.messageList[index].tag_configure(tagname='blue', background='blue', foreground='white')
            self.messageList[index].grid(column=index, row=0)
        column = ['team', 'alive/total', 'kill']
        self.statisticsMessage = ttk.Treeview(self, height=2, show="headings", columns=column)
        for i in range(len(column)):
            self.statisticsMessage.column(str(i), width=200, anchor='center')
            self.statisticsMessage.heading(str(i), text=str(column[i]))
            self.statisticsMessage.tag_configure(tagname='red', foreground='red')
            self.statisticsMessage.tag_configure(tagname='blue',foreground='blue')
        self.statisticsMessage.grid(column=0,columnspan=3,row=1)


    #每个周期调用以更新显示内容
    def periodicExecution(self,vertexes):
        self.A_team_alive=0
        self.B_team_alive=0
        for vertex in vertexes: #统计存活数量
            if vertex.state==Vertex.A_TEAM:
                self.A_team_alive+=1
            elif vertex.state==Vertex.B_TEAM:
                self.B_team_alive+=1
        self.statisticsMessage.insert("", 0, tags='red',
                                      values=['A_TEAM', str(self.A_team_alive) + '/' + str(self.A_team_total)
                                          , str(self.B_team_total - self.B_team_alive)], )
        self.statisticsMessage.insert("", 1, tags='blue',
                                      values=['B_TEAM', str(self.B_team_alive) + '/' + str(self.B_team_total)
                                          , str(self.A_team_total - self.A_team_alive)], )
        for index in range(len(vertexes)):
            vertex=vertexes[index]
            if vertex.last_action:
                action=list(vertex.last_action.keys())[0]
                last_action=str(action+"-"+str(vertex.last_action[action].id))
            else:
                last_action=""
            if vertex.action_todo:
                action=list(vertex.action_todo.keys())[0]
                action_todo=str(action+"-"+str(vertex.action_todo[action].id))
            else:
                action_todo=""
            if vertex.state==Vertex.EMPTY:
                tag="empty"
            elif vertex.state==Vertex.A_TEAM:
                tag='red'
            elif vertex.state==Vertex.B_TEAM:
                tag='blue'
            self.messageList[int(index/20)].insert("", index%20, values=[vertex.id,last_action,action_todo],tags=tag)

    def hide(self):
        self.showing = False
        self.withdraw()

    def show(self):
        self.showing = True
        self.update()
        self.deiconify()

