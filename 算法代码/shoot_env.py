import numpy as np
import time
import random
import math,sys
random.seed(2)

# 通过sigmoid函数进行命中率初始化,截取定义域(-5,+5)部分，值域约为（0.0067，0.993）
def sigmoid_accuracy(dis):
    accuracy=[(dis-i)/dis*10 for i in range(dis)]
    for i in range(len(accuracy)):
        accuracy[i]-=5
        accuracy[i]=1/(1+pow(math.e,-accuracy[i]))
    return accuracy

class ShootEnv():
    init_A = [2]
    init_B = [2]
    # init_A=[2, 2]
    # init_B=[2, 2]
    init_dis = 4
    accuracy_A = [1, 0.8, 0.2, 0.1]
    accuracy_B = [1, 0.6, 0.3, 0.2]
    def __init__(self,expectation_reward=False,A=None,B=None,dis=None,random_seed=None):
        if random_seed!=None:
            random.seed(random_seed)
        if A:
            self.init_A=A
        if B:
            self.init_B=B
        if dis:
            self.init_dis=dis
            if dis!= 4:
                self.accuracy_A=sigmoid_accuracy(dis)#sigmod函数命中率曲线
                self.accuracy_B=[(dis - i) * (1 / dis) for i in range(dis)]#线性命中率函数
        self.n_actions = int(pow(len(self.init_A) + 1, len(self.init_B)))
        self.n_features = 1+len(self.init_A)+len(self.init_B)
        self.A=self.init_A.copy()
        self.B=self.init_B.copy()
        self.dis=self.init_dis
        self.expectation_reward=expectation_reward#True的话会根据期望返回reward，下一状态仍随机返回

    def reset(self):
        self.A = self.init_A.copy()
        self.B = self.init_B.copy()
        self.dis=self.init_dis
        return [[self.dis,self.A.copy(),self.B.copy()],[self.dis,self.B.copy(),self.A.copy()]]

    # 计算存活概率，根据calNash传入的a，b策略例如[0,1]代表有两人，分别不射击和射击对面第一人，返回此时双方每一人的存活概率
    def calAliveRate(self, A_s, B_s, A_accuracy, B_accuracy):
        A_alive = [1 for i in range(len(A_s))]
        B_alive = [1 for i in range(len(B_s))]
        # print(A_s,B_s)
        for i in range(len(A_s)):
            if A_s[i] != 0:
                B_alive[A_s[i] - 1] *= (1 - A_accuracy[i])
        for i in range(len(B_s)):
            if B_s[i] != 0:
                A_alive[B_s[i] - 1] *= (1 - B_accuracy[i])
        return A_alive, B_alive

    #用于修正无子弹开枪或开枪目标不存在
    def check_and_fix_action(self,action,state,oppo_num):
        fixed=False
        # print("action,state:",action,state)
        for i in range(len(action)-1,-1,-1):
            if i>=len(state):
                action.pop(i)
            elif (state[i]==0 and action[i]!=0) or action[i]>oppo_num:
                action[i]=0#没有子弹或者射击对象不存在，修正为选择不射击
                fixed=True
                # print("fixed")
        return fixed


    def get_next_s(self,action,old_state,alive):
        new_state=[]
        for i in range(len(action)):
            if action[i]!=0:
                old_state[i]-=1
                if old_state[i]<0:
                    raise Exception("无子弹却射击！")
            if random.random()<alive[i]:
                new_state.append(old_state[i])
        return new_state

    def step(self, action_A,action_B):
        action_A=eval(action_A)
        action_B=eval(action_B)
        self.check_and_fix_action(action_A,self.A,len(self.B))
        fixed=self.check_and_fix_action(action_B,self.B,len(self.A))
        A_alive, B_alive = self.calAliveRate(action_A, action_B,
                                             [self.accuracy_A[self.dis-1] for i in range(len(self.init_A))],
                                             [self.accuracy_B[self.dis-1] for i in range(len(self.init_B))])
        n_A,n_B=len(self.A),len(self.B)
        #更新A,B的状态
        self.A,self.B=self.get_next_s(action_A,self.A,A_alive),self.get_next_s(action_B,self.B,B_alive)
        self.A.sort()
        self.B.sort()
        self.dis-=1
        s_ = [[self.dis, self.A.copy(), self.B.copy()], [self.dis, self.B.copy(), self.A.copy()]]
        if self.expectation_reward:#按照期望值返回reward,s_
            expectation_kill=0
            for b in B_alive:
                expectation_kill += (1-b)
            for a in A_alive:
                expectation_kill -= (1 - a)
            reward=[expectation_kill,-expectation_kill]
        else:#按照下一个状态的实际人数差值返回reward,s_
            net_kill = len(self.A) - n_A + n_B - len(self.B)  # A的净击杀
            reward=[net_kill,-net_kill]#每阵亡一人对方+1分，自己-1分
        done=not self.A or not self.B or not self.dis#一方全部阵亡或经过最近距离则游戏结束
        # if fixed:
        #     reward[1]-=100#对于做出错误动作进行惩罚？DQN
        return s_, reward, done

    def render(self):
        pass

    #供DQN使用，通过index转化为action（全动作，不考虑是否有效）
    def indexToAction(self,index):
        #len(A)每个人选择不射击或射击len(B)中的某个
        action=[0 for i in range(len(self.init_A))]
        loop_time=0
        while(index):
            action[loop_time]=index % (len(self.init_B)+1)
            index//=(len(self.init_B)+1)
            loop_time+=1
        return str(action)


