import random
from tkinter import messagebox

def getHitRatio(state):
    if state == Vertex.A_TEAM:
        return 1
    else:
        return 1

def getDeathRatio(attacked_count):
    if attacked_count==0:
        return 0
    else:
        return pow(attacked_count,2)*0.1

class Vertex(object):
    A_TEAM=0
    B_TEAM=1
    EMPTY=2#状态的enum
    def __init__(self,x,y,z,x_2d,y_2d,index,id,state):
        self.x=x
        self.y=y
        self.z=z # 坐标
        self.x_2d=x_2d
        self.y_2d=y_2d # 2d化坐标
        self.index=index # 据点在列表中的序号
        self.id=id # 位于据点的单位序号
        self.state=state # 状态,归属红/蓝或无
        self.attacked_count=0 #被攻击次数
        self.edges=[] #所连接的全部其它顶点的序号
        self.last_action=None #上一次行动
        self.action_todo=None #之后要做的行动

    def addEgde(self,vertex):
        self.edges.append(vertex)

class Battlefield(object):
    def __init__(self):
        self.vertexes=[]
        V,E,S,V_2d=self.readFile()
        for i in range(60):
            self.vertexes.append(Vertex(V[i][0],V[i][1],V[i][2],V_2d[i][0],V_2d[i][1],
                                        i,i,S[i]))
        for edge in E:
            start_v=edge[0]
            end_v=edge[1]
            self.vertexes[edge[0]].addEgde(edge[1])
            self.vertexes[edge[1]].addEgde(edge[0]) # 是否有序？待考

    #读入V和E的文件信息
    def readFile(self):
        VFIle=open("V","r")
        V=[]
        for vertex in VFIle.readlines():
            single_v=vertex.replace("\n","").split(",")
            for index in range(len(single_v)):
                single_v[index]=float(single_v[index])
            V.append(single_v)
        VFIle.close()

        EFile=open("E","r")
        E=[]
        for edge in EFile.readlines():
            single_e=edge.replace("\n","").split(",")
            for index in range(len(single_e)):
                single_e[index]=int(single_e[index])-1 #-1从1-60变为0-59
            E.append(single_e)
        EFile.close()

        SFile=open("S","r")
        S=[]
        for state in SFile.readlines():
            S.append(int(state))
        SFile.close()

        V2dFIle = open("V_2d", "r")
        V_2d = []
        for vertex in V2dFIle.readlines():
            single_v = vertex.replace("\n", "").split(",")
            for index in range(len(single_v)):
                single_v[index] = float(single_v[index])
            V_2d.append(single_v)
        V2dFIle.close()

        return V,E,S,V_2d

    #某一顶点的单位对另一单位发起攻击
    def attack(self,start,end):
        if end.state==Vertex.EMPTY or start.state==Vertex.EMPTY or start.state==end.state:
            raise Exception("攻击：错误的攻击指示",start.state,end.state)
        print("%d attack %d"%(start.id,end.id))
        if random.random()<=getHitRatio(start.state):#命中
            end.attacked_count+=1


    #从一个顶点移动到另一个空顶点
    def move(self,start,end):
        if end.state!=Vertex.EMPTY:
            raise Exception("移动：错误的目标地点",start,end)
        end.state=start.state
        end.id=start.id # id作为身份标识跟着移动
        start.state = Vertex.EMPTY

    #进行结算
    def doSettlement(self,vertex):
        if random.random()<=getDeathRatio(vertex.attacked_count):
            vertex.state=Vertex.EMPTY #被击杀状态置空
            print("%d dead"%vertex.id)
        vertex.attacked_count=0 #计数清空


    #根据action_todo行动进行动作
    def doAction(self,vertex):
        if 'attack' in vertex.action_todo.keys():
            self.attack(vertex,vertex.action_todo['attack'])

    #每个顶点用此函数决策
    def doDecision(self,vertex):
        for edge in vertex.edges:  # 简单的测试的行动规则
            # if self.vertexes[edge].state == Vertex.EMPTY:  # 能够移动就移动
            #     vertex.action_todo = {'move': self.vertexes[edge]}
            #     break
            if self.vertexes[edge].state!=Vertex.EMPTY  \
                    and self.vertexes[edge].state != vertex.state:  # 阵营不同发起攻击
                vertex.action_todo = {'attack': self.vertexes[edge]}
                break

    #每个回合做的事情
    def periodicExecution(self):
        vertexes = self.vertexes
        #决策
        for vertex in vertexes:
            if vertex.state==Vertex.EMPTY:#空顶点，不需继续
                continue
            if vertex.action_todo: #本回合已经下达过行动命令的单位，不需继续
                continue
            self.doDecision(vertex)
        #进行行动
        for vertex in vertexes:
            if vertex.state==Vertex.EMPTY:#空顶点，不需继续
                continue
            if vertex.action_todo:
                self.doAction(vertex)
        #死亡处理等结果结算
        for vertex in vertexes:
            vertex.last_action = vertex.action_todo  # 重置上次行动与下次行动
            vertex.action_todo = {}
            if vertex.state==Vertex.EMPTY:
                continue
            self.doSettlement(vertex)

    def controlAction(self,control_target_index,action,action_target_index):
        attacker_state=self.vertexes[control_target_index].state
        attacked_state=self.vertexes[action_target_index].state
        if attacker_state!= Vertex.EMPTY and attacked_state != Vertex.EMPTY \
                and attacker_state != attacked_state:
            # 符合发起攻击的条件，阵营不同且不为空
            self.vertexes[control_target_index].action_todo={action:self.vertexes[action_target_index]}
        else:
            messagebox.showerror('错误', "控制指令无法执行!")


