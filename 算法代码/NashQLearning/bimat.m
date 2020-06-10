
% >> d=-12;M=[0 -1 1+d; 1+d 0 -1; -1 1+d 0]; N=M'; [A,B,a,b,iterations,err,ms]=bimat(M,N)


% >> M=[5 0; 0 5]; N=[0 5; 5 0];[A,B,a,b,iterations,err,ms]=bimat(M,N)
% http://www.mathworks.com/matlabcentral/fileexchange/22356-bimatrix-game 
% Two example
% JOURNAL OF MATHEMATICAL ANALYSIS AND APPLICATIONS 9, 348-355 (1964)
% Two-Person Nonzero-Sum Games and Quadratic Programming
% 0. L. MANGASARIAN AND H. STONE 
%Example 1:
% >> M=[2 -1; -1 1]; N=[1 -1; -1 2];[A,B,a,b,iterations,err,ms]=bimat(M,N);
% Optimization terminated.
% 
% A =
% 
%     0.6000    0.4000
% 
% 
% B =
% 
%     0.4000    0.6000
% 
% 
% a =
% 
%     0.2000
% 
% 
% b =
% 
%     0.2000
% 
% 
% iterations =
% 
%      4
% 
% 
% err =
% 
%      0
% 
% 
% ms =
% 
% The bimatrix game has pure Nash equilibria as:- (A1,B1) with payoff to Ist player=2 and payoff to IInd player=1; (A2,B2) with payoff to Ist player=1 and payoff to IInd player=2; And one mixed strategy Nash Equilibrium is given in the solution matrix. Also we mention that the mixed strategy solution is reasonably relevent!

%Example 2:
%>>  M=[	0.00 	0.20 	0.40 	0.60 	0.80 	1.00 	
% 	0.20 	0.00 	0.20 	0.40 	0.60 	0.80 	
% 	0.40 	0.20 	0.00 	0.20 	0.40 	0.60 	
% 	0.60 	0.40 	0.20 	0.00 	0.20 	0.40 	
% 	0.80 	0.60 	0.40 	0.20 	0.00 	0.20 	
% 	1.00 	0.80 	0.60 	0.40 	0.20 	0.00 	]
% 							
% N=[	0.00 	-0.02 	-0.08 	-0.18 	-0.32 	-0.50 	
% 	0.00 	0.02 	0.00 	-0.06 	-0.16 	-0.30 	
% 	0.00 	0.06 	0.08 	0.06 	0.00 	-0.10 	
% 	0.00 	0.10 	0.16 	0.18 	0.16 	0.10 	
% 	0.00 	0.14 	0.24 	0.30 	0.32 	0.30 	
% 	0.00 	0.16 	0.32 	0.42 	0.48 	0.50 	];

%  [A,B,a,b,iterations,err,ms]=bimat(M,N)

% Optimization terminated.
% 
% A =
% 
%     0.5000         0         0         0         0    0.5000
% 
% 
% B =
% 
%          0         0    0.5000    0.5000         0         0
% 
% 
% a =
% 
%     0.5000
% 
% 
% b =
% 
%     0.1200
% 
% 
% iterations =
% 
%     12
% 
% 
% err =
% 
%      0
% 
% 
% ms =
% 
% The bimatrix game has no pure strategy Nash Equillibrium; And one mixed strategy Nash Equilibrium is given in the solution matrix. Also we mention that the mixed strategy solution is reasonably relevent!

%  Player1payoffM=[ 5 0; 0 5]; Player2payoffN=[0 5; 5 0]; ; [A,B,a,b,iterations,err,ms]=bimat(Player1payoffM,Player2payoffN)
%  Player1payoffM=[ 5 0; 0 5]; Player2payoffN=[0 5; 5 0]; ; [A,B,a,b,iterations,err,ms]=bimat(Player1payoffM,Player2payoffN)
%  aa=PoMSeltene1Binmore2Roth3(1,1);M=[aa(1) aa(3);aa(5) aa(7)]; N=[aa(1+1) aa(3+1);aa(5+1) aa(7+1)]; [M N];[A,B,a,b,iterations,err,ms]=bimat(M,N)
% A =
% 
%     0.0909    0.9091
% 
% 
% B =
% 
%     0.9091    0.0909
% 
% 
% a =
% 
%     9.0909
% 
% 
% b =
% 
%     8.9091

function [A,B,a,b,iterations,err,ms]=bimat(M,N)
    C=M+N;[m,n]=size(C);u=[];v=[];a=[];b=[];count=0;ms=[];
    for i=1:m
        for j=1:n
            if (M(i,j)==max(M(:,j)) && N(i,j)==max(N(i,:)))
               count=count+1;u(count)=i;v(count)=j;a(count)=M(i,j);b(count)=N(i,j);
            end
        end
    end%遍历矩阵，如果M（i,j）在右边选j时是最佳策略（得分最高）同时N（i，j）是左面选i时得分最高，记录这个点（i,j）同时count++
    if count>0
        for i=1:count
            ms=[ms ' (A' int2str(u(i)) ',B' int2str(v(i)) ') with payoff to Ist player=' num2str(a(i)) ' and payoff to IInd player=' num2str(b(i)) ';'];
        end
        ms=['The bimatrix game has pure Nash equilibria as:-' ms];%存在纯策略纳什均衡
    else
        ms=['The bimatrix game has no pure strategy Nash Equillibrium;'];
    end
    ms=[ms ' And one mixed strategy Nash Equilibrium is given in the solution matrix.'];%算法将给出一个混合策略纳什均衡
    H=-[zeros(m,m) C zeros(m,2);C' zeros(n,n+2);zeros(2,n+m+2)];%zeros为生成全0矩阵，ones全1矩阵
    f=[zeros(m+n,1);1;1];
    Aeq=[ones(1,m) zeros(1,n+2); zeros(1,m) ones(1,n) zeros(1,2)];
    beq=[1;1];b=zeros(m+n,1);
    A=[zeros(m,m) M -ones(m,1) zeros(m,1); N' zeros(n,n+1) -ones(n,1)];
    lb=[zeros(m+n,1);-inf;-inf];ub=[ones(m+n,1);inf;inf];options=optimset('Largescale','off','MaxIter',500);warning off all;
    options=optimset('Display','off');%display-off让quadprog不打印说明信息
    [x,fval,exitflag,output,lambda]= quadprog(H,f,A,b,Aeq,beq,lb,ub,[],options);X=roundn((x(1:m,1))',-6);Y=roundn((x(m+1:m+n,1))',-6);f=roundn(fval,-6);
    switch exitflag
        case 1
            if abs(fval)<.05
                A=abs(X);B=abs(Y);iterations=output.iterations;a=roundn(x(m+n+1,1),-6);b=roundn(x(m+n+2,1),-6);err=abs(f);
                ms=[ms ' Also we mention that the mixed strategy solution is reasonably relevent!'];
            else
                A=abs(X);B=abs(Y);iterations=output.iterations;a=roundn(x(m+n+1,1),-6);b=roundn(x(m+n+2,1),-6);err=abs(f);
                ms=[ms 'Also we mention that the mixed strategy solution is not reasonably relevent!'];
            end
        case 4
            A=abs(X);B=abs(Y);iterations=output.iterations;a=roundn(x(m+n+1,1),-6);b=roundn(x(m+n+2,1),-6);err=abs(f);
             ms=[ms 'Also we mention that local minimizer was found!'];
        case 0
            A=abs(X);B=abs(Y);iterations=output.iterations;a=roundn(x(m+n+1,1),-6);b=roundn(x(m+n+2,1),-6);err=abs(f);
             ms=[ms 'Also we mention that the number of iterations is too large so the iteration scheme is not easily converging!'];
        case -2
            A=zeros(1,m);B=zeros(1,n);iterations=0;a=0;b=0;err=0;
            ms=['The optimization problem is infeasible!'];
        case -3
            A=zeros(1,m);B=zeros(1,n);iterations=0;a=0;b=0;err=0;
            msgn=['The optimization problem is unbounded!'];
        case -4
            A=zeros(1,m);B=zeros(1,n);iterations=0;a=0;b=0;err=0;
            ms=['The optimization current search direction was not a descent direction. No further progress could be made.'];
        case -7
            A=zeros(1,m);B=zeros(1,n);iterations=0;a=0;b=0;err=0;
            ms=['In the optimization process magnitude of search direction became too small. No further progress could be made.'];
        otherwise
            A=zeros(1,m);B=zeros(1,n);iterations=0;a=0;b=0;err=0;
            ms=['The optimization problem has unexpected error!'];
    end
    
