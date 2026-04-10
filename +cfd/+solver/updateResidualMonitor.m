function monitor = updateResidualMonitor(monitor, iter, ru, rv, rp, rc)
%UPDATERESIDUALMONITOR Update residual monitor entries.

if ~isstruct(monitor) || ~isscalar(monitor)
    error('cfd:solver:InvalidMonitor', 'monitor must be scalar struct.');
end
vals = [ru rv rp rc];
if ~all(isfinite(vals))
    error('cfd:solver:InvalidResidual', 'Residuals must be finite.');
end
if iter < 1 || iter > monitor.max_iterations
    error('cfd:solver:IterationRange', 'iter out of range.');
end

monitor.iteration = iter;
monitor.current = struct('u',ru,'v',rv,'p',rp,'continuity',rc);
monitor.history.u(iter) = ru;
monitor.history.v(iter) = rv;
monitor.history.p(iter) = rp;
monitor.history.continuity(iter) = rc;
end
