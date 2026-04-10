function [isConverged, reason] = ConvergenceController(monitor, tolerances, minIterations)
%CONVERGENCECONTROLLER Determine convergence from residual monitor.

if nargin < 2 || isempty(tolerances)
    tolerances = struct('u',1e-6,'v',1e-6,'p',1e-5,'continuity',1e-6);
end
if nargin < 3 || isempty(minIterations)
    minIterations = 5;
end
if ~isstruct(monitor) || ~isscalar(monitor)
    error('cfd:solver:InvalidMonitor', 'monitor must be scalar struct.');
end

iter = monitor.iteration;
if iter < minIterations
    isConverged = false;
    reason = 'minimum_iterations_not_reached';
    return;
end

r = monitor.current;
isConverged = (r.u <= tolerances.u) && (r.v <= tolerances.v) && (r.p <= tolerances.p) && (r.continuity <= tolerances.continuity);
if isConverged
    reason = 'residual_tolerances_met';
else
    reason = 'residuals_above_tolerance';
end
end
