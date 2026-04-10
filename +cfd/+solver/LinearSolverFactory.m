function [x, info] = LinearSolverFactory(A, b, solverName, tol, maxit, x0)
%LINEARSOLVERFACTORY Solve sparse linear system with GMRES/BiCGSTAB.

if nargin < 3 || isempty(solverName)
    solverName = 'gmres';
end
if nargin < 4 || isempty(tol)
    tol = 1e-8;
end
if nargin < 5 || isempty(maxit)
    maxit = 200;
end
if nargin < 6
    x0 = [];
end

if ~issparse(A)
    A = sparse(A);
end
if ~(isnumeric(b) && isvector(b) && size(A,1)==numel(b) && size(A,2)==numel(b))
    error('cfd:solver:InvalidLinearSystem', 'Invalid A/b dimensions.');
end
b = b(:);

switch lower(solverName)
    case 'gmres'
        restart = min(50, numel(b));
        [x, flag, relres, iter] = gmres(A, b, restart, tol, maxit, [], [], x0);
        if flag ~= 0
            [x2, flag2, relres2, iter2] = bicgstab(A, b, tol, maxit, [], [], x0);
            if flag2 == 0 || relres2 < relres
                x = x2; flag = flag2; relres = relres2; iter = iter2;
            end
        end
    case 'bicgstab'
        [x, flag, relres, iter] = bicgstab(A, b, tol, maxit, [], [], x0);
        if flag ~= 0
            restart = min(50, numel(b));
            [x2, flag2, relres2, iter2] = gmres(A, b, restart, tol, maxit, [], [], x0);
            if flag2 == 0 || relres2 < relres
                x = x2; flag = flag2; relres = relres2; iter = iter2;
            end
        end
    otherwise
        error('cfd:solver:UnknownLinearSolver', 'Unknown solverName: %s', solverName);
end

info = struct('flag',flag,'relres',relres,'iter',iter,'solver',solverName);
end
