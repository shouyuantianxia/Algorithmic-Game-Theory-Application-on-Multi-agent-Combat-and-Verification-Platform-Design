from shoot_env import ShootEnv
from NashQLearning.RL_brain import NashQLearningTable
import os
import time
from draw_plot import draw_plot

def update(run_times,recent_num,save_file):
    file=None
    if save_file:
        file=open(save_file,'w')
    average_r=0
    recent_r=[]
    recent_r_sum=0
    average_recent_r=0
    for episode in range(run_times):
        # initial observation
        observation = env.reset()
        # print('init_obserbation:',observation)
        total_reward=0
        while True:
            # fresh env
            env.render()

            # RL choose action based on observation
            A_index,A_action = RL_A.choose_action(str(observation[0]))
            B_index,B_action = RL_B.choose_action(str(observation[1]))

            # RL take action and get next observation and reward
            observation_, reward, done = env.step(A_action,B_action)
            total_reward+=reward[0]
            # RL learn from this transition
            RL_A.learn(str(observation[0]), A_index,B_index, reward[0], str(observation_[0]))
            RL_B.learn(str(observation[1]), B_index,A_index, reward[1], str(observation_[1]))

            # swap observation
            observation = observation_

            # break while loop when end of this episode
            if done:
                average_r=(average_r*episode+total_reward)/(episode+1)
                recent_r.append(total_reward)
                recent_r_sum+=total_reward
                if len(recent_r)>recent_num:
                    recent_r_sum-=recent_r.pop(0)
                average_recent_r=recent_r_sum/len(recent_r)
                if save_file:
                    print(episode)
                    file.write(str(episode)+" "+str(average_r) + " " + str(average_recent_r)+'\n')
                else:
                    print(episode, str(average_r) + " " + str(average_recent_r))
                break

    # end of game
    print('game over')

def trained_NashQLearningTable(path,greedy=1.0,greedy_increment=None):
    nashq=NashQLearningTable(learning_rate=0,e_greedy=greedy,e_greedy_increment=greedy_increment)
    nashq.read_trained_table(path)
    return nashq

#4,[2,2],[2,2]下
# greedy_increment=0.000005
# times = 80000 完成收敛
# greedy_increment = 0.00001
# times = 40000 未完成收敛
# greedy_increment=0.000007
# times = 60000 未完成收敛
if __name__ == "__main__":
    single_trained = False #是否将A智能体替换为均衡解的智能体
    random_seed=4
    times = 60000  # 训练的场次
    A_greedy=1 #A选择最优策略的概率
    B_greedy=1 #B
    greedy_increment=1/times/8 #贪婪概率从0逐步递增到设定的值，每次递增的大小，None为不采用
    # A_greedy=0.9
    # B_greedy=0.9
    # greedy_increment=None
    recent = 1000 #绘图统计时reward用最近多少场的平均值
    expectation_r=True
    # name='2_2_increasing_greedy_'
    env = ShootEnv(
        expectation_reward=expectation_r,
        dis=16,
        A=[2],
        B=[2],
        random_seed=random_seed
        # A=[2,2],
        # B=[2,2],
    )
    name='16_2_2'
    if random_seed!=None:
        name+='_seed'+str(random_seed)
    if greedy_increment:
        name+='_increasing_greedy'

    if single_trained:
        RL_A = trained_NashQLearningTable('../nash_matrix',greedy=A_greedy,greedy_increment=greedy_increment)
    else:
        RL_A = NashQLearningTable(e_greedy=A_greedy,e_greedy_increment=greedy_increment)
    RL_B = NashQLearningTable(e_greedy=B_greedy,e_greedy_increment=greedy_increment)
    if single_trained:
        name+='_single_trained'
    else:
        name+='_self'
    name+='_'+str(times)+'_recent_'+str(recent)
    if expectation_r:
        name+='_expectation'

    time_start = time.time()
    os.mkdir(name)
    update(times,recent,'./'+name+'/reward')
    RL_A.save_trained_table('./'+name+'/trained_table_A')
    RL_B.save_trained_table('./'+name+'/trained_table_B')
    action_file=open("./"+name+'/action',"w")
    nash_msg=RL_B.nash_msg
    for state in nash_msg.keys():
        action_file.write(str(state)+";"+str(nash_msg[state])+'\n')
    draw_plot(name+'/reward',
              # expected_value=-0.031093
              expected_value=-0.1523 #16_2_2
              # expected_value=-0.16779
              # expected_value=-0.139886 #12 2 2
              # expected_value=- 0.29657525# 8 4 4
              # expected_value=-0.273745#8 3 3
              )
    time_end = time.time()
    print("cost_time:" + str(time_end - time_start))
    print(RL_A.learn_step)
    print(RL_A.epsilon)
    print(RL_B.learn_step)

