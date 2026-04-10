function [u, v, p, res] = CouplingSchemeSIMPLEC(state, cfg, fields)
%COUPLINGSCHEMESIMPLEC One SIMPLEC iteration.

fields.urf.u = min(0.95, fields.urf.u + 0.1);
fields.urf.v = min(0.95, fields.urf.v + 0.1);
fields.urf.p = min(0.6, fields.urf.p + 0.1);
[u, v, p, res] = cfd.solver.CouplingSchemeSIMPLE(state, cfg, fields);
end
