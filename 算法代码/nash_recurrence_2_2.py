import copy
import time
import os
import math
from LH import LH_zero
from shoot_env import sigmoid_accuracy

#存储某个子博弈状态的纳什均衡解，包括A、B策略和A的期望损益值
class NashMessage():
    def __init__(self,A_strategy=[],B_strategy=[],A_profit=0):
        self.A_strategy = A_strategy
        self.B_strategy = B_strategy
        self.A_profit=A_profit

    def __str__(self):
        return "A策略:"+str(self.A_strategy)+"\nB策略"+str(self.B_strategy)+"\nA获益/B损失"+str(self.A_profit)

#提供某一方的状态和index之间互相转换
#形成一个类似[],[0],[1],[2],[0,0],[0,1]……[2,2]的状态顺序(人数导弹数均从少到多)
class StateIndexTransfer():
    def __init__(self,max_list):
        self.state_dict={}#{state:index}的字典
        self.state_list=[]#按index排序的state
        self.n_state=0
        max_list.sort(reverse=True)
        for i in range(len(max_list)+1):#依次截取前1、2、3……位，从人少状态到人多状态
            self.init_add_state(max_list[:i])

    def init_add_state(self,max_list):
        states=[[]]
        for i in max_list:#按顺序生成max_list中每个数从0取到最大值的所有排列组合（即所有可能的state）
            states = [s + [a] for s in states for a in range(i + 1)]
        for state in states:#将所有state储存方便转换
            self.state_dict[str(state)]=self.n_state
            self.state_list.append(state)
            self.n_state+=1

    #状态转序号
    def listToInt(self,list=[]):
        return self.state_dict[str(list)]

    #序号转状态
    def intToList(self,num=0):
        return self.state_list[num]

#主函数，依次遍历所有的子博弈状态并计算该状态的纳什均衡，以此得到整体的纳什均衡解
def mainLoop (dis: int, x, y, accuracy_A, accuracy_B, save_dir:str):
    x_max=A_state.listToInt(list=x);y_max=B_state.listToInt(list=y)
    # print(x_max,y_max)
    #存储所有子博弈状态计算的均衡结果的三维数组，dis,A_state,B_state
    nash = [[[NashMessage() for i in range(y_max + 1)] for j in range(x_max + 1)] for k in range(dis + 1)]
    for i in range(1,dis+1):#遍历距离
        for j in range(x_max+1):#遍历A的所有可能状态
            for k in range(1,y_max+1):#遍历B的所有可能状态
                calNash(i, j, k, accuracy_A[i-1], accuracy_B[i-1], nash, save_dir)
                # print(str(nash[i][j][k]))
    return nash

# 分列出所有可能的死活情况以及概率
# 输入实例,双方每一个单位的存活率：A_alive=[0.6],B_alive=[0.5]
# 输出实例，每种情况的出现概率以及此时双方每个单位是否存活（bool类型）：alive_or_death=[
# [0.24, [True], [True]], [0.36, [False], [True]],[0.16, [True], [False]], [0.24, [False], [False]]
# ]
def getAllCases(A_alive,B_alive):
    alive_or_death = [[1, [], []]]
    alive_list = [A_alive, B_alive]
    # print("存活概率",alive_list)
    for alive in range(len(alive_list)):
        for k in range(len(alive_list[alive])):
            for result in range(len(alive_or_death)):
                temp = copy.deepcopy(alive_or_death[result])
                alive_or_death[result][0] *= alive_list[alive][k]
                alive_or_death[result][alive + 1].append(True)
                temp[0] *= (1 - alive_list[alive][k])
                temp[alive + 1].append(False)
                alive_or_death.append(temp)
                # print(alive_or_death)
    return alive_or_death


#计算存活概率，根据calNash传入的a，b策略例如[0,1]代表有两人，分别不射击和射击对面第一人，返回此时双方每一人的存活概率
#输入示例：A_s=[0,1],B_s=[1],A=[0.3,0.3],B=[0.6]
#输出示例：[0.4,1],[0.7]
def calAliveRate(A_s,B_s,A,B):
    A_alive=[1 for i in range(len(A_s))]
    B_alive=[1 for i in range(len(B_s))]
    for i in range(len(A_s)):
        if A_s[i]!=0:
            B_alive[A_s[i]-1]*=(1-A[i])
    for i in range(len(B_s)):
        if B_s[i] != 0:
            A_alive[B_s[i] - 1] *= (1 - B[i])
    return A_alive,B_alive

def calNash (dis: int, x, y, A:float, B:float, nash, save_dir:str):
    nash_to_cal=nash[dis][x][y]
    x_list=A_state.intToList(x)
    y_list=B_state.intToList(y)#x_list,y_list为A，B队的子弹数list比如[1,2]意味着该队伍有2个存活分别有1,2枚子弹
    A_strategy = [[]]#示例[[0,0],[0,1],[0,2]]意味着一个人没有子弹只能不射击0，另一个人可选择不射击或射击对面2人中一个
    B_strategy = [[]]
    # print("子弹数",x_list, y_list)
    # 生成AB的单步策略集，每个队伍的每个单位可以任意射击对方队伍的任一单位
    #例子：x_list=[0,2],y_list=[1,1]
    #A_strategy=[[0,0],[0,1],[0,2]]意味着一个人没有子弹只能不射击0，另一个人可选择不射击或射击对面2人中一个
    #B_strategy=[[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2], [2, 0], [2, 1], [2, 2]]
    for i in x_list:
        if i==0:
            for s in A_strategy:
                s.append(0)
        else:
            A_strategy = [s+[a] for s in A_strategy for a in range(len(y_list)+1)]
    for i in y_list:
        if i==0:
            for s in B_strategy:
                s.append(0)
        else:
            B_strategy = [s+[a] for s in B_strategy for a in range(len(x_list)+1)]
    # print("策略",A_strategy, B_strategy)
    # 计算单步下的支付矩阵
    payoff_matrix=[[0 for j in range(len(B_strategy))]for i in range(len(A_strategy))]
    for i in range(len(A_strategy)):
        for j in range(len(B_strategy)):#遍历双方的所有策略对抗可能，并赋值支付矩阵的对应元素位置
            A_alive,B_alive=calAliveRate(A_strategy[i],B_strategy[j],[A for i in range(len(init_x))],
                                         [B for i in range(len(init_y))])
            alive_or_death=getAllCases(A_alive,B_alive)
            # print("可能结局",alive_or_death)
            # 这里需要分情况根据死亡人数用到多个下位的nash值
            for case in alive_or_death:#每个case是[发生概率.A队伍[False代表死亡,True代表存活],B队伍[True]]
                if case[0]!=0:
                    temp_x = x_list.copy()
                    temp_y = y_list.copy()
                    temp_x_y=[temp_x,temp_y]
                    for temp_index in range(len(temp_x_y)):#根据A,B的策略扣除子弹数
                        s_index=[i,j][temp_index]
                        strategy=[A_strategy,B_strategy][temp_index][s_index]
                        for shoot_index in range(len(strategy)):
                            if strategy[shoot_index]!=0:
                                temp_x_y[temp_index][shoot_index]-=1
                        #根据存活case情况生成新的x,y，死亡者将被移除
                        temp_x_y[temp_index]=[temp_x_y[temp_index][k]
                                    for k in range(len(temp_x_y[temp_index])) if case[temp_index+1][k]]
                    temp_x,temp_y=temp_x_y[0],temp_x_y[1]#通过扣除子弹及阵亡单位计算出这个case下的下一子博弈状态
                    kill=len(y_list)-len(temp_y)-(len(x_list)-len(temp_x))#净击杀个数
                    # 考虑多人对战中对于双方剩余多人多枚子弹一次交火后仍有存活后的情况特别处理
                    if dis==1 and (temp_x!=x_list or temp_y!=y_list):
                        next_situation=nash[dis][A_state.listToInt(temp_x)][B_state.listToInt(temp_y)]
                    else:#不需要特别处理的情况
                        next_situation = nash[dis - 1][A_state.listToInt(temp_x)][B_state.listToInt(temp_y)]
                    #更新支付矩阵在当前case的收益，为发生率*（立即得分kill+未来得分next_situation的纳什均衡期望）
                    payoff_matrix[i][j] +=(case[0]*(kill+next_situation.A_profit))
            # print(payoff_matrix[i][j])
    #使用LH算法利用支付矩阵计算纳什均衡策略和期望收益
    nash_msg = LH_zero(payoff_matrix)
    nash_to_cal.A_strategy,nash_to_cal.B_strategy,nash_to_cal.A_profit\
        =nash_msg[0],nash_msg[1],float(nash_msg[2])
    if save_dir:#计算结果存储到本地文件，如果是空字符串则不存
        save_single_matrix([dis,x_list,y_list], payoff_matrix, save_dir + '/matrix')
        save_single_action([dis,x_list,y_list], nash_msg[0],nash_msg[1], save_dir + '/action')

#计算结果存储到本地文件
def save_single_matrix(state,matrix,file_path):
    file = open(file_path, "a")#末尾追加
    n_rows = len(matrix)
    file.write(str(state)+"\n")#状态
    file.write(str(n_rows)+"\n")#矩阵行数
    for i in range(n_rows):
        file.write(str(matrix[i])+"\n")
    file.close()
#计算结果存储到本地文件
def save_single_action(state,action_A,action_B,file_path):
    file = open(file_path, "a")  # 末尾追加
    file.write(str(state)+"\n")#状态
    file.write(str(action_A) + "\n")  # A的动作
    file.write(str(action_B) + "\n")  # B的动作
    file.close()

# init_x = [2,2]#代表A有len(init_x)人，第i人有init_x[i]导弹
# init_y = [2,2]#代表B有同上
init_x = [2]
init_y = [2]
A_state=StateIndexTransfer(init_x)#依据初始状态生成按顺序的所有子博弈状态排序，来进行状态和序号的转换，以进行动态规划
B_state=StateIndexTransfer(init_y)
def main(dis,init_x,init_y):
    # dis = 4 #距离个数
    accuracy_A = sigmoid_accuracy(dis)  # sigmod函数命中率曲线
    accuracy_B = [(dis - i) * (1 / dis) for i in range(dis)]  # 线性命中率函数
    # print(accuracy_A,accuracy_B)
    # dis=5
    # accuracy_A = [1.0, 0.8, 0.6, 0.2,0.1]
    # accuracy_B = [1.0, 0.6, 0.5, 0.4,0.2]
    # dis = 4
    # accuracy_A = [1, 0.8, 0.2, 0.1]
    # accuracy_B = [1, 0.6, 0.3, 0.2]
    # accuracy_A=[1.0, 0.75, 0.5, 0.25]
    # accuracy_B=[1.0, 0.75, 0.5, 0.25]


    save_dir=""#存储路径
    # save_dir="./"+str(dis)+'_'+str(init_x)+'_'+str(init_y)
    # try:
    #     os.mkdir(save_dir)
    # except Exception as e:
    #     print(e)
    #     return
    nash=mainLoop(dis, init_x, init_y, accuracy_A, accuracy_B, save_dir=save_dir)
    # A_strategy,B_strategy=findStrategy(dis,x,y,nash)
    # print(str(nash[dis][A_state.listToInt(init_x)][B_state.listToInt(init_y)]))
    # #全部状态下的策略输出
    # for i in range(1,dis+1):
    #     for j in range(A_state.listToInt(init_x)+1):
    #         for k in range(1,B_state.listToInt(init_y)+1):
    #             print(i,A_state.intToList(j),B_state.intToList(k),str(nash[i][j][k]))
    # print(accuracy_A,accuracy_B)
    # for i in range(dis+1):
    #     for j in range(4):
    #         for k in range(4):
    #             print(nash[i][j][k].A_profit,end=" ")
    #         print(end="\n")
    #     print("-----------")
    # print("A整体策略")
    # for strategy in A_strategy:
    #     print(strategy)
    # print("B整体策略")
    # for strategy in B_strategy:
    #     print(strategy)

if __name__=="__main__":
    repeat_times = 3
    output_file=open("cost_time_SPNA_"+str(repeat_times),"a")
    run_mission=[
        # [4,[[2,2],[3,3],[4,4]]],
        # [8,[[2,2],[3,3],[4,4],[6,6]]],
        # [16,[[2,2],[4,4],[6,6]]],
        # [32,[[2, 2], [4, 4]]],
        # [64, [[2, 2], [4, 4]]],
        # [100,[[2,2]]],
        # [1000,[[2,2]]]
        [16, [[3, 3]]],
        [32, [[3, 3]]],
        [64, [[3, 3]]],
    ]
    print("start")
    for mission in run_mission:
        dis=mission[0]
        for init_x in mission[1].copy():
            for init_y in mission[1].copy():
                print(str([dis, init_x, init_y]),end=";")
                A_state = StateIndexTransfer(init_x)  # 依据初始状态生成按顺序的所有子博弈状态排序，来进行状态和序号的转换，以进行动态规划
                B_state = StateIndexTransfer(init_y)
                time_start=time.time()
                for i in range(repeat_times):
                    main(dis,init_x.copy(),init_y.copy())
                time_end = time.time()
                print(str((time_end-time_start)/repeat_times))
                output_file = open("cost_time_SPNA_" + str(repeat_times), "a")
                output_file.write(str([dis,init_x,init_y])+";"+str((time_end-time_start)/repeat_times)+"\n")
                output_file.close()
