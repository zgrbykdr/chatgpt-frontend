function monitor = ResidualMonitor(maxIterations)
%RESIDUALMONITOR Create residual history monitor.

if nargin < 1 || isempty(maxIterations)
    maxIterations = 500;
end
if ~(isnumeric(maxIterations) && isscalar(maxIterations) && isfinite(maxIterations) && maxIterations >= 1)
    error('cfd:solver:InvalidMaxIterations', 'maxIterations must be >= 1.');
end

monitor = struct();
monitor.max_iterations = double(maxIterations);
monitor.iteration = 0;
monitor.history = struct('u', nan(maxIterations,1), 'v', nan(maxIterations,1), 'p', nan(maxIterations,1), 'continuity', nan(maxIterations,1));
monitor.current = struct('u', inf, 'v', inf, 'p', inf, 'continuity', inf);
end
