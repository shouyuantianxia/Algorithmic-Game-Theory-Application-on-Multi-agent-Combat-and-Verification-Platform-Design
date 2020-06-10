import matlab.engine
import time
eng=matlab.engine.start_matlab()

#存储某个子博弈状态的纳什均衡解，包括A、B策略和A的期望损益值
class NashMessage():
    def __init__(self,A_strategy=[],B_strategy=[],A_profit=0):
        self.A_strategy = A_strategy
        self.B_strategy = B_strategy
        self.A_profit=A_profit

    def __str__(self):
        return "A策略:"+str(self.A_strategy)+"\nB策略"+str(self.B_strategy)+"\nA获益/B损失"+str(self.A_profit)

def findStrategy(dis:int,x:int,y:int,nash):
    A_strategy=[]
    B_strategy=[]
    if dis ==0:
        return [{"probability":1,"distance":[]}],[{"probability":1,"distance":[]}]
    nash_msg=nash[dis][x][y]
    for i in range(len(nash_msg.A_strategy)):
        for j in range(len(nash_msg.B_strategy)):#排列组合所有可能策略0不射击1射击
            probability=nash_msg.A_strategy[i]*nash_msg.B_strategy[j]
            if probability != 0:#0可能策略组合忽视
                temp_A,temp_B=findStrategy(dis-1,x-i,y-j,nash)
                for strategy in temp_A:
                    strategy['probability']*=probability
                    if i!=0:
                        strategy['distance'].append(dis)
                for strategy in temp_B:
                    strategy['probability']*=probability
                    if j!=0:
                        strategy['distance'].append(dis)
                A_strategy.extend(temp_A)
                B_strategy.extend(temp_B)
    A_strategy=[{"probability":1,"distance":[]}] if not A_strategy else A_strategy
    B_strategy=[{"probability":1,"distance":[]}] if not B_strategy else B_strategy
    return A_strategy,B_strategy

def mainLoop ( dis: int, x: int, y: int, accuracy_A,accuracy_B):
    nash = [[[NashMessage() for i in range(y + 1)] for j in range(x + 1)] for k in range(dis + 1)]
    for i in range(1,dis+1):
        for j in range(x+1):
            for k in range(y+1):
                calNash(i, j, k, accuracy_A[i-1],accuracy_B[i-1],nash)
    return nash

#计算至多2x2的零和博弈支付矩阵的纳什均衡
#[ a,  b
#  c,  d]
def calNash ( dis: int, x: int, y: int, A:float,B:float,nash):
    nash_to_cal=nash[dis][x][y]
    if x and y:#双方均有子弹，2x2的支付矩阵
        a=nash[dis-1][x][y].A_profit #双方均不射击
        b=nash[dis-1][x][y-1].A_profit*(1-B)-B #仅B射击
        c=nash[dis-1][x-1][y].A_profit*(1-A)+A #仅A射击
        d=nash[dis-1][x-1][y-1].A_profit*(1-A)*(1-B)+A*(1-B)-B*(1-A) #双方均射击
        nash_msg=eng.bimat_2_2(float(a),float(b),float(c),float(d),nargout=3)
        nash_to_cal.A_strategy,nash_to_cal.B_strategy,nash_to_cal.A_profit\
            =list(nash_msg[0][0]),list(nash_msg[1][0]),float(nash_msg[2])
    elif x: #仅A有子弹，是1x2矩阵，不需要LH计算
        a=nash[dis-1][x][y].A_profit
        c = nash[dis - 1][x - 1][y].A_profit * (1 - A) + A
        nash_to_cal.A_profit = max(a,c)
        if a==c:
            nash_to_cal.A_strategy=[0.5,0.5]
        else:
            nash_to_cal.A_strategy=[0,1] if a<c else [1,0]
        nash_to_cal.B_strategy = [1, 0]
    elif y: #仅B有子弹是2x1矩阵，不需要LH计算
        a = nash[dis - 1][x][y].A_profit
        b = nash[dis - 1][x][y - 1].A_profit * (1 - B) - B
        nash_to_cal.A_profit = min(a, b)
        if a==b:
            nash_to_cal.B_strategy=[0.5,0.5]
        else:
            nash_to_cal.B_strategy=[0,1] if a>b else [1,0]
        nash_to_cal.A_strategy=[1,0]
    else:
        nash_to_cal.A_profit=0
        nash_to_cal.A_strateg=[1,0]
        nash_to_cal.B_strateg=[1, 0]
def main():
    x = 2
    y = 2
    # dis=5
    # accuracy_A = [1.0, 0.8, 0.6, 0.2,0.1]
    # accuracy_B = [1.0, 0.6, 0.5, 0.4,0.2]
    dis=4
    accuracy_A=[1,0.8,0.2,0.1]
    accuracy_B=[1,0.6,0.3,0.2]
    # accuracy_A=[1.0, 0.75, 0.5, 0.25]
    # accuracy_B=[1.0, 0.75, 0.5, 0.25]
    # dis=100
    # accuracy_A=[(dis-i)*(1/dis) for i in range(dis)]
    # accuracy_B = accuracy_A.copy()
    nash=mainLoop(dis,x,y,accuracy_A,accuracy_B)
    print(str(nash[dis][x][y]))
    A_strategy,B_strategy=findStrategy(dis,x,y,nash)
    print("A整体策略")
    for strategy in A_strategy:
        print(strategy)
    print("B整体策略")
    for strategy in B_strategy:
        print(strategy)
    #输出全部nash值
    # for i in range(dis + 1):
    #     for j in range(3):
    #         for k in range(3):
    #             print(nash[i][j][k].A_profit, end=" ")
    #         print(end="\n")
    #     print("-----------")

if __name__=="__main__":
    time_start=time.time()
    main()
    time_end=time.time()
    print(time_end-time_start)
