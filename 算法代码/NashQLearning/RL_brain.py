"""
This part of code is the Q learning brain, which is a brain of the agent.
All decisions are made in here.

View more on my tutorial page: https://morvanzhou.github.io/tutorials/
"""
import random
from LH import LH_zero

def random_pick(some_list, probabilities):
    x = random.uniform(0,1)
    cumulative_probability = 0.0
    for item, item_probability in zip(some_list, probabilities):
        cumulative_probability += item_probability
        if x < cumulative_probability:break
    return item

class NashQLearningTable:
    def __init__(self,learning_rate=0.01, reward_decay=1, e_greedy=0.9,e_greedy_increment=None):
        self.lr = learning_rate
        self.gamma = reward_decay
        self.epsilon_max = e_greedy
        self.q_table_nash={}#每个元素是一个状态下的nash支付矩阵
        self.nash_msg={}#每个元素是一个状态下的nash均衡下的[自己的动作、对手的动作、期望收益]
        self.state_actions={}#每个元素是一个状态下的动作集合[a1.a2,…,an]
        self.state_oppo_actions={}#对手的动作，结构同上
        self.epsilon_increment = e_greedy_increment
        self.epsilon = 0 if e_greedy_increment is not None else self.epsilon_max#参考DQN逐步增加greedy的方式
        self.learn_step=0

    def save_trained_table(self,file_path):
        file = open(file_path, "w")
        for state in self.q_table_nash.keys():
            matrix = self.q_table_nash[state]
            n_rows = len(matrix)
            file.write(str(state)+"\n")#状态
            file.write(str(n_rows)+"\n")#矩阵行数
            for i in range(n_rows):
                file.write(str(matrix[i])+"\n")


    def read_trained_table(self,file_path):
        file = open(file_path, "r")
        line=file.readline()
        while(line):
            state=line.strip('\n')
            n_rows=int(file.readline().strip('\n'))
            matrix=[]
            for i in range(n_rows):
                matrix.append(eval(file.readline().strip('\n')))
            self.q_table_nash[state]=matrix
            self.nash_msg[state] = LH_zero(self.q_table_nash[state])#重新计算？
            self.find_actions(state)
            line = file.readline()

    def choose_action(self, observation):
        self.check_state_exist(observation)
        actions,oppo_actions=self.find_actions(observation)
        # action selection
        if random.random() < self.epsilon and self.nash_msg[observation]:
            # choose best action
            state_action = self.nash_msg[observation][0]
            # some actions may have the same value, randomly choose on in these actions
            action_index = random_pick(range(len(actions)),state_action)
            action=actions[action_index]
        else:
            # choose random action
            state_action=[1/len(actions) for i in range(len(actions))]
            action_index = random_pick(range(len(actions)),state_action)
            action = actions[action_index]
        return action_index,action

    def learn(self, s, a_index,oppo_a_index, r, s_):
        if self.lr==0:
            self.epsilon = self.epsilon + self.epsilon_increment if self.epsilon < self.epsilon_max else self.epsilon_max
            self.learn_step += 1
            return
        self.check_state_exist(s_)
        q_predict = float(self.q_table_nash[s][a_index][oppo_a_index])
        if s_ != 'terminal' and self.nash_msg[s_]:
            q_target = r + self.gamma * float(self.nash_msg[s_][2])  # next state is not terminal
        else:
            q_target = r  # next state is terminal
        self.q_table_nash[s][a_index][oppo_a_index] += self.lr * (q_target - q_predict)  # update
        self.nash_msg[s] = LH_zero(self.q_table_nash[s])
        # increasing epsilon
        self.epsilon = self.epsilon + self.epsilon_increment if self.epsilon < self.epsilon_max else self.epsilon_max
        self.learn_step += 1

    def get_actions(self,A_list, B_list):
        strategy = [[]]
        for i in A_list:
            if i == 0:
                for s in strategy:
                    s.append(0)
            else:
                strategy = [s + [a] for s in strategy for a in range(len(B_list) + 1)]
        for i in range(len(strategy)):
            strategy[i] = str(strategy[i])
        return strategy

    def find_actions(self,state):
        if state not in self.state_actions.keys():
            list_state=eval(state)#重新作为list解析，包含dis,A_state,B_state三个元素_
            self.state_actions[state]=self.get_actions(list_state[1],list_state[2])
            self.state_oppo_actions[state]=self.get_actions(list_state[2],list_state[1])
        return self.state_actions[state],self.state_oppo_actions[state]


    def check_state_exist(self, state):
        if state not in self.q_table_nash.keys():
            # if self.lr==0:
            #     print(state)
            # append new state to q table
            actions, opponent_actions = self.find_actions(state)
            self.q_table_nash[state]=[[0 for i in range(len(opponent_actions))]
                                      for j in range(len(actions))]#支付矩阵初始化
            self.nash_msg[state]=[]

    def setEGreedy(self,value):
        self.epsilon=value