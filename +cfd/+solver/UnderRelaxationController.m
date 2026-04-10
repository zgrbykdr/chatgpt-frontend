function urf = UnderRelaxationController(cfg, iter, monitor)
%UNDERRELAXATIONCONTROLLER Adaptive under-relaxation factors.

if nargin < 2; iter = 1; end
if nargin < 3; monitor = struct('current',struct('u',inf,'v',inf,'p',inf,'continuity',inf)); end
cfg = cfd.config.validateConfig(cfg);

urf = struct('u',0.7,'v',0.7,'p',0.3);
if strcmp(cfg.solver.solver_type, 'SIMPLEC')
    urf.u = 0.85; urf.v = 0.85; urf.p = 0.4;
elseif strcmp(cfg.solver.solver_type, 'PISO')
    urf.u = 0.95; urf.v = 0.95; urf.p = 0.7;
end

if iter > 10
    ru = monitor.current.u;
    rv = monitor.current.v;
    rp = monitor.current.p;
    if max([ru rv rp]) > 1e-1
        urf.u = max(0.3, 0.8*urf.u);
        urf.v = max(0.3, 0.8*urf.v);
        urf.p = max(0.2, 0.8*urf.p);
    end
end
end
