#A_s和B_s均为选择的射击距离从大到小排列的数组，例如[4,3]代表选择4,3距离射击
def cal_payoff(A_s,B_s,A_accuracy,B_accuracy,x,y):
    A_s.append(-1)
    B_s.append(-1)
    A_pay_off=0#A的收益，返回值
    All_alive=1#到目前为止双方仍然都存活的概率（也即进入目前情形的概率）
    A=A_accuracy#命中率数组
    B=B_accuracy
    A_shoot=0 #遍历A_s的index，也是目前A射击过的次数
    B_shoot=0 #遍历B_s的index
    # 整体思路是距离数从大到小遍历，每当有人开枪就更新All_alive和A_payoff
    while A_shoot<x or B_shoot<y:
        if A_s[A_shoot]==B_s[B_shoot]:#同时开枪
            dis=A_s[A_shoot]
            A_pay_off+=All_alive*A[dis]*(1-B[dis])#A活B死的概率，正分
            A_pay_off-=All_alive*B[dis]*(1-A[dis])#A死B活概率，负分
            All_alive*=((1-B[dis])*(1-A[dis]))#均存活概率减少
            A_shoot+=1
            B_shoot+=1#双方射击次数+1
        elif A_s[A_shoot]>B_s[B_shoot]:#只有A开枪
            dis = A_s[A_shoot]
            A_pay_off+=All_alive*A[dis]#A活B死的概率，正分
            All_alive*=(1-A[dis])
            A_shoot+=1
        elif A_s[A_shoot]<B_s[B_shoot]:#只有B开枪
            dis=B_s[B_shoot]
            A_pay_off-=All_alive*B[dis]#A死B活概率，负分
            All_alive *= (1 - B[dis])  # A生存率减少
            B_shoot+=1
    return round(A_pay_off,5)



if __name__ == "__main__":
    dis=5#距离数
    x=2 #A导弹数
    y=2 #B导弹数
    # A = [1.0, 0.8, 0.2, 0.1]
    # B = [1.0, 0.6, 0.3, 0.2]
    # A = [1.0, 0.75, 0.5, 0.25]
    # B = [1.0, 0.75, 0.5, 0.25]
    A = [1.0, 0.8, 0.6, 0.2, 0.1] #A在不同距离range(dis)命中率
    B = [1.0, 0.6, 0.5, 0.4, 0.2] #B在不同距离range(dis)命中率
    strategy=[]
    for i in range(dis):
        for j in range(dis-1-i):
            strategy.append([dis-1-i,dis-2-i-j])#仅限x=y=2时，选择两个距离射击作为一个策略
    print(strategy)
    for row in range(len(strategy)):
        A_s=strategy[row]
        row_msg=[]
        for column in range(len(strategy)):
            B_s=strategy[column]
            row_msg.append(cal_payoff(A_s.copy(),B_s.copy(),A,B,x,y))
        print(row_msg)