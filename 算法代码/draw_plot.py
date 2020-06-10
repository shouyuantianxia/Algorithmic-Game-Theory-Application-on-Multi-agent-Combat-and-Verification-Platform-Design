import os

def draw_and_save(x,y,save_path,expected_value):
    import matplotlib.pyplot as plt
    plt.plot(x,y)
    if expected_value:
        plt.plot(x,[expected_value for i in range(len(x))])
    # plt.plot(0,0.6)
    plt.ylabel('reward_recent_1000')
    plt.xlabel('training times')
    save_path+=".png"
    if os.path.exists(save_path):
        os.remove(save_path)
    plt.savefig(save_path)
    plt.show()

def draw_plot(path,expected_value=None,num=None):
    file=open(path,errors='ignore')
    y=[]
    if num:
        for i in range(num):
            line=file.readline().strip('\n')
            index,aver,aver_recent=map(float,line.split(" "))
            y.append(aver_recent)
    else:
        for line in file.readlines():
            line=line.strip('\n')
            index, aver, aver_recent = map(float, line.split(" "))
            y.append(aver_recent)
    file.close()
    draw_and_save(range(len(y)),y,path,expected_value)

class Strategy():
    def __init__(self,n_max_A,n_max_B):
        self.count=0
        self.A_s = [0 for i in range(n_max_A)]
        self.B_s = [0 for i in range(n_max_B)]

    def __str__(self):
        for s in [self.A_s,self.B_s]:
            sum_num=sum(s)
            for index in range(len(s)):
                s[index]=s[index]/sum_num
        return str(self.count)+';'+str(self.A_s)+";"+str(self.B_s)

    def add(self,A_index,B_index):
        self.count+=1
        self.A_s[A_index] += 1
        self.B_s[B_index] += 1


class Statistic():
    def __init__(self,agent_num):
        self.statistics={}
        # 供cal_nash_accuracy使用，取值为1,2仅支持4,[2],[2]和4,[2,2],[2,2]两种计算
        self.agent_num=agent_num

    #应在Strategy()的__str__执行后调用(依照action_statistics的顺序)
    def cal_nash_accuracy(self):
        sum_num=0#总共权重数
        A_sum_accuracy=0#乘以权重后，加权计算（最后需除以sum_num）
        B_sum_accuracy=0
        if self.agent_num==1:
            strategy=self.statistics[str([4,2,2])]
            sum_num+=strategy.count
            A_sum_accuracy += strategy.A_s[0]*strategy.count
            B_sum_accuracy += strategy.B_s[0]*strategy.count
            strategy = self.statistics[str([3, 2, 2])]
            sum_num += strategy.count
            A_sum_accuracy += strategy.A_s[1] * strategy.count
            B_sum_accuracy += strategy.B_s[1] * strategy.count
            strategy = self.statistics[str([2, 1, 1])]
            sum_num += strategy.count
            A_sum_accuracy += strategy.A_s[1] * strategy.count
            B_sum_accuracy += strategy.B_s[1] * strategy.count
        else:
            strategy=self.statistics[str([4,2,2,2,2])]
            sum_num += strategy.count
            A_sum_accuracy += strategy.A_s[0] * strategy.count
            B_sum_accuracy += strategy.B_s[0] * strategy.count
            strategy = self.statistics[str([3, 2, 2, 2, 2])]
            sum_num += strategy.count
            A_sum_accuracy += (strategy.A_s[5]+strategy.A_s[7]) * strategy.count
            B_sum_accuracy += (strategy.B_s[5]+strategy.B_s[7]) * strategy.count
            strategy = self.statistics[str([2, 1, 1, 1, 1])]
            sum_num += strategy.count
            A_sum_accuracy += (strategy.A_s[5] + strategy.A_s[7]) * strategy.count
            B_sum_accuracy += (strategy.B_s[5] + strategy.B_s[7]) * strategy.count
        return str(A_sum_accuracy/sum_num)+';'+str(B_sum_accuracy/sum_num)


    #仅适用于[0,0] [0,1] [0,2] [1,0] [1,1] [1,2] [2,0] [2,1] [2,2]
    def action_to_index(self,action):
        return action[0]*3+action[1] if len(action)==2 else action[0]

    def add(self,state,A_action,B_action):
        if state not in self.statistics.keys():
            strategy_num=2 if self.agent_num==1 else 9
            self.statistics[state] = Strategy(strategy_num, strategy_num)
        self.statistics[state].add(self.action_to_index(A_action),self.action_to_index(B_action))


def action_statistics(source_path,save_path,agent_num,start_index=0,end_index=None):
    statistics_file=open(save_path,'w+')
    statistics=Statistic(agent_num)
    with open(source_path,'r') as action_file:
        for line in action_file:
            msg=line.strip('\n').split(';')
            if int(msg[0])>=start_index:
                if end_index and int(msg[0])>end_index:
                    continue
                statistics.add(msg[1],eval(msg[2]),eval(msg[3]))
        action_file.close()
    for state in statistics.statistics.keys():
        statistics_file.write(str(state)+';'+str(statistics.statistics[state])+'\n')
    statistics_file.write(statistics.cal_nash_accuracy())


if __name__ == "__main__":
    path='./DQN/self_50000_expectation_'
    # path='./DQN/2_2_self_greedy_increment_1200000_expectation'
    action_statistics(path+'/action',path+'/action_statistics',1,start_index=35000,end_index=37000)
    # draw_plot(path+'/reward',0.012)
    # draw_plot('./NashQLearning/2_2_self_1000000_recent_1000_expectation/reward',expected_value=-0.031093)
    # draw_plot('./DQN/self_200000')
    # draw_plot('./trained_vs_DQN/2_2_100000',expected_value=-0.031093)
    # draw_plot('./trained_vs_DQN/50000(3)')
    # A_strategy=[[]]
    # B_strategy=[[]]
    # for i in [2,2]:
    #     if i==0:
    #         for s in A_strategy:
    #             s.append(0)
    #     else:
    #         A_strategy = [s+[a] for s in A_strategy for a in range(3)]
    # print(A_strategy)
