from shoot_env import ShootEnv
from DQN.DQN_RL_brain import DeepQNetwork
import time,os
from draw_plot import draw_plot,action_statistics

def trans_observation(ob,n_A,n_B):
    result=[ob[0]]
    for j in range(2):
        for i in range([n_A,n_B][j]):
            if i< len(ob[j+1]):
                result.append(ob[j+1][i])
            else:
                result.append(-1)
    return result

def update(run_times,recent_num,save_path):
    reward_file=None#保存奖励值的文件
    action_file=None#保存选取的动作的文件
    if save_path:
        reward_file=open(save_path+'/reward','w')
        action_file=open(save_path+'/action','w')
    step = 0
    average_r = 0
    recent_r = []
    recent_r_sum=0
    average_recent_r = 0
    for episode in range(run_times):
        # initial observation
        observation = env.reset()
        n_A, n_B = len(observation[0][1]), len(observation[0][2])
        observation[0] = trans_observation(observation[0], n_A, n_B)
        observation[1] = trans_observation(observation[1], n_B, n_A)
        total_reward = 0
        while True:
            # fresh env
            env.render()
            # RL choose action based on observation
            A_index= RL_A.choose_action(observation[0].copy())
            B_index= RL_B.choose_action(observation[1].copy())
            A_action,B_action=env.indexToAction(A_index),env.indexToAction(B_index)
            # RL take action and get next observation and reward
            observation_, reward, done = env.step(A_action,B_action)
            if action_file and RL_A.epsilon==RL_A.epsilon_max and RL_B.epsilon==RL_B.epsilon_max:
                action_file.write(str(episode)+';')
                action_file.write(str(observation[0]) + ';'+str(A_action)+';'+str(B_action)+'\n')
            else:
                # print(observation[0], A_action, B_action)
                pass
            observation_[0] = trans_observation(observation_[0], n_A, n_B)
            observation_[1] = trans_observation(observation_[1], n_B, n_A)
            total_reward += reward[0]

            RL_A.store_transition(observation[0].copy(), A_index, reward[0], observation_[0].copy())
            RL_B.store_transition(observation[1].copy(), B_index, reward[1], observation_[1].copy())

            if (step > 200) and (step % 5 == 0):
                RL_A.learn()
                RL_B.learn()

            # swap observation
            observation = observation_

            # break while loop when end of this episode
            if done:
                average_r = (average_r * episode + total_reward) / (episode + 1)
                recent_r.append(total_reward)
                recent_r_sum += total_reward
                if len(recent_r) > recent_num:
                    recent_r_sum -= recent_r.pop(0)
                average_recent_r = recent_r_sum / len(recent_r)
                if reward_file:
                    print(episode)
                    reward_file.write(str(episode) + " " + str(average_r) + " " + str(average_recent_r) + '\n')
                else:
                    print(episode, str(average_r) + " " + str(average_recent_r))
                break
            step += 1

    # end of game
    print('game over')


if __name__ == "__main__":
    agent_num=1
    env = ShootEnv(
        True,
        A=[2 for i in range(agent_num)],B=[2 for i in range(agent_num)])
    times=50000
    RL_A = DeepQNetwork(env.n_actions, env.n_features, "A",
                        learning_rate=0.005,
                        reward_decay=0.9,
                        e_greedy=0.9,
                        replace_target_iter=400,
                        memory_size=200000,
                        # output_graph=True
                        )
    RL_B = DeepQNetwork(env.n_actions, env.n_features, "B",
                        learning_rate=0.005,
                        reward_decay=0.9,
                        e_greedy=0.9,
                        replace_target_iter=400,
                        memory_size=200000
                        # output_graph=True
                        )
    # RL_A = DeepQNetwork(env.n_actions, env.n_features,"A",
    #                   learning_rate=0.001,
    #                   reward_decay=0.9,
    #                   e_greedy=1,
    #                   replace_target_iter=1000,
    #                   # memory_size=int(times/10),
    #                     memory_size=200000,
    #                   e_greedy_increment=8/times,
    #                   # output_graph=True
    #                   )
    # RL_B = DeepQNetwork(env.n_actions, env.n_features,"B",
    #                     learning_rate=0.001,
    #                     reward_decay=0.9,
    #                     e_greedy=1,
    #                     replace_target_iter=1000,
    #                     # memory_size=int(times/10),
    #                     memory_size=200000,
    #                     e_greedy_increment = 8 / times,
    #                     # output_graph=True
    #                     )
    dir_path = './self_' + str(times) + '_expectation_'
    # dir_path = './2_2_self_greedy_increment_' + str(times) + '_expectation'
    # dir_path = './self_greedy_increment_' + str(times) + '_expectation'
    os.mkdir(dir_path)
    time_start = time.time()
    update(times, 1000, dir_path)
    time_end=time.time()
    print("cost_time:" + str(time_end - time_start))
    draw_plot(dir_path + '/reward',
              expected_value=[0.012,-0.031093][agent_num-1]
              #   expected_value = 0.012
              )
    #神经网络储存
    os.mkdir(dir_path+'/A_sess')
    os.mkdir(dir_path + '/B_sess')
    RL_A.save(dir_path + '/A_sess/sess')
    RL_B.save(dir_path + '/B_sess/sess')
    #统计动作策略
    action_statistics(dir_path + '/action', dir_path + '/action_statistics',agent_num)
    RL_A.plot_cost()
    RL_B.plot_cost()