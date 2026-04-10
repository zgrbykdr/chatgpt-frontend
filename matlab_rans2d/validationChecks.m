function v = validationChecks(s, c, mesh)
% Solver self-check and validation utility.
v = struct();
v.converged = s.converged;
v.diverged = s.diverged;

if ~isempty(s.massImbalanceHistory)
    v.massImbalanceFinal = s.massImbalanceHistory(end);
else
    v.massImbalanceFinal = NaN;
end

v.nonNegativeTurbulence = all(s.k(:)>=c.clip.kMin) && all(s.epsilon(:)>=c.clip.epsMin) && all(s.omega(:)>=c.clip.omMin);

post = postProcess(s,c,mesh);
v.yPlusRange = [post.yPlusMin, post.yPlusMax, post.yPlusMean];

if contains(lower(c.model),'epsilon')
    v.yPlusWarning = post.yPlusMean < 20 || post.yPlusMean > 300;
elseif contains(lower(c.model),'omega')
    v.yPlusWarning = post.yPlusMean > 5;
else
    v.yPlusWarning = false;
end

if strcmpi(c.name,'Laminar Channel Flow') || strcmpi(c.model,'laminar')
    y = mesh.yc(:)/max(c.Ly,1e-12);
    uNum = s.u(:,end);
    if max(abs(uNum)) > 0
        uNum = uNum / max(uNum);
    end
    uAna = 4*y.*(1-y);
    v.laminarL2Error = norm(uNum-uAna,2)/max(norm(uAna,2),1e-12);
else
    v.laminarL2Error = NaN;
end

v.massConservationWarning = ~isnan(v.massImbalanceFinal) && v.massImbalanceFinal > 1e-4;
end
