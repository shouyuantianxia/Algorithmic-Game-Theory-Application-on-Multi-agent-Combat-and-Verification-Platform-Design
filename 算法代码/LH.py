import matlab.engine
eng=matlab.engine.start_matlab()
#输入支付矩阵，返回A的各策略概率、B的各策略概率、A的期望收益
def LH_zero(payoff_matrix):
    # 1x1,1x2或2x1矩阵直接处理不调用bimat
    height = len(payoff_matrix);
    width = len(payoff_matrix[0])
    if height == 1 and width == 1:
        nash_msg = [[[1]], [[1]], payoff_matrix[0][0]]
    elif height == 1 and width == 2:
        if payoff_matrix[0][0] == payoff_matrix[0][1]:
            choose_first = 0.5
        else:
            choose_first = 1 if payoff_matrix[0][0] < payoff_matrix[0][1] else 0
        nash_msg = [[[1]],[[choose_first, 1 - choose_first]], min(payoff_matrix[0][0], payoff_matrix[0][1])]
    elif height == 2 and width == 1:
        if payoff_matrix[0][0] == payoff_matrix[1][0]:
            choose_first = 0.5
        else:
            choose_first = 1 if payoff_matrix[0][0] > payoff_matrix[1][0] else 0
        nash_msg = [[[choose_first, 1 - choose_first]], [[1]], max(payoff_matrix[0][0], payoff_matrix[1][0])]
    else:
        nash_msg=list(eng.bimat_zero(matlab.double(payoff_matrix), nargout=3))
    #对于单一策略原算法不会作为数组返回，需要进行统一格式处理
    for i in range(2):
        if isinstance(nash_msg[i],float):
            nash_msg[i]=[[nash_msg[i]]]
    nash_msg[0]=list(nash_msg[0][0])
    nash_msg[1]=list(nash_msg[1][0])
    return nash_msg

