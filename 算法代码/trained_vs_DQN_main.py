from shoot_env import ShootEnv
from DQN.DQN_RL_brain import DeepQNetwork
from NashQLearning.main_nashQ import trained_NashQLearningTable
import time
import os
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

def update(run_times,recent_num,save_path=''):
    reward_file = None
    action_file = None
    if save_path:
        reward_file = open(save_path + '/reward', 'w')
        action_file = open(save_path + '/action', 'w')
    step = 0
    average_r = 0
    recent_r = []
    recent_r_sum=0
    average_recent_r = 0
    for episode in range(run_times):
        # initial observation
        observation = env.reset()
        n_A,n_B=len(observation[1][1]),len(observation[1][2])
        observation[1]=trans_observation(observation[1],n_A,n_B)
        total_reward = 0
        while True:
            # fresh env
            env.render()
            # RL choose action based on observation
            A_index,A_action = RL_A.choose_action(str(observation[0]))
            B_index= RL_B.choose_action(observation[1].copy())
            B_action=env.indexToAction(B_index)

            # RL take action and get next observation and reward
            observation_, reward, done = env.step(A_action,B_action)
            if action_file and RL_B.epsilon==RL_B.epsilon_max:
                action_file.write(str(episode)+';')
                action_file.write(str(observation[1]) + ';' + str(A_action) + ';' + str(B_action) + '\n')
            # else:
                # print(observation[1], A_action, B_action)
            # print(observation[0][0],A_action)
            observation_[1]=trans_observation(observation_[1],n_A,n_B)
            total_reward += reward[0]

            RL_A.learn(str(observation[0]), A_index, B_index, reward[0], str(observation_[0]))
            RL_B.store_transition(observation[1].copy(), B_index, reward[1], observation_[1].copy())

            if (step > 200) and (step % 5 == 0):
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
    times=1200000
    env = ShootEnv(
        True,
        [2,2],[2,2],4
        )
    RL_A = trained_NashQLearningTable(
                        './nash_matrix'

                        )
    RL_B = DeepQNetwork(env.n_actions, env.n_features, "B",
                        learning_rate=0.001,
                        reward_decay=0.9,
                        e_greedy=1,
                        replace_target_iter=400,
                        memory_size=times,
                        e_greedy_increment=2 / times  #
                        # output_graph=True
                        )

    dir_path='./trained_vs_DQN/2_2_greedy_increment_'+str(times)
    # dir_path = './trained_vs_DQN/greedy_increment_' + str(times)
    # dir_path = './trained_vs_DQN/greedy_0.9_' + str(times)
    os.mkdir(dir_path)
    time_start = time.time()
    update(times, 1000, dir_path)
    time_end = time.time()
    print("cost_time:" + str(time_end - time_start))
    draw_plot(dir_path + '/reward',
              expected_value=-0.031093
              # expected_value=0.012
              )
    # RL_B.plot_cost()
    print(RL_B.learn_step_counter)
    print(RL_B.epsilon)
    RL_B.save(dir_path + '/sess')
    action_statistics(dir_path + '/action', dir_path + '/action_statistics', 2)
