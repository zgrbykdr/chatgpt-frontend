function [u, v, p, res] = CouplingSchemePISO(state, cfg, fields)
%COUPLINGSCHEMEPISO Two pressure-correction loops (PISO-like).

[u1,v1,p1,res1] = cfd.solver.CouplingSchemeSIMPLE(state, cfg, fields);
fields2 = fields;
fields2.u = u1; fields2.v = v1; fields2.p = p1;
fields2.urf.p = min(1.0, max(fields.urf.p, 0.8));
[u,v,p,res2] = cfd.solver.CouplingSchemeSIMPLE(state, cfg, fields2);

res = struct();
res.u = res2.u;
res.v = res2.v;
res.p = min(res1.p, res2.p);
res.continuity = min(res1.continuity, res2.continuity);
end
