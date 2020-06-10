function [A,B,a]=bimat_zero(matrix)
   M=matrix;
   N=-M;
   [A,B,a,b,iterations,err,ms]=bimat(M,N);
end