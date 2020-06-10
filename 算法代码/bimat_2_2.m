function [A,B,a]=bimat_2_2(a,b,c,d)
   M=[a,b
       c,d];
   N=-M;
   [A,B,a,b,iterations,err,ms]=bimat(M,N);
end