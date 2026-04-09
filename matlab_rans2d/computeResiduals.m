function [res, summary] = computeResiduals(prev, s, c, mesh, iter)
% Compute normalized algebraic residual indicators.

du = s.u - prev.u;
dv = s.v - prev.v;
dp = s.p - prev.p;
dk = s.k - prev.k;
de = s.epsilon - prev.epsilon;
do = s.omega - prev.omega;

res.u = norm(du(:),2) / max(norm(s.u(:),2),1e-12);
res.v = norm(dv(:),2) / max(norm(s.v(:),2),1e-12);
res.p = norm(dp(:),2) / max(norm(s.p(:),2),1e-12);

if strcmpi(c.model,'Laminar')
    res.k = 0;
    res.epsilon = 0;
    res.omega = 0;
else
    res.k = norm(dk(:),2) / max(norm(s.k(:),2),1e-12);
    res.epsilon = norm(de(:),2) / max(norm(s.epsilon(:),2),1e-12);
    res.omega = norm(do(:),2) / max(norm(s.omega(:),2),1e-12);
end

res.global = max([res.u,res.v,res.p,res.k,res.epsilon,res.omega]);

allVals = [s.u(:);s.v(:);s.p(:);s.k(:);s.epsilon(:);s.omega(:);s.mut(:)];
summary.diverged = any(isnan(allVals)) || any(isinf(allVals));
summary.iter = iter;
summary.negKCount = nnz(s.k < c.clip.kMin);
summary.negEpsCount = nnz(s.epsilon < c.clip.epsMin);
summary.negOmCount = nnz(s.omega < c.clip.omMin);
summary.activeCells = nnz(mesh.fluidMask);
end
