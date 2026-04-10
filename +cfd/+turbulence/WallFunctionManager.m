function turb = WallFunctionManager(turb, wall)
%WALLFUNCTIONMANAGER Apply logarithmic wall-function constraints.

if ~isstruct(turb) || ~isstruct(wall)
    error('cfd:turbulence:InvalidInputs', 'turb and wall must be structs.');
end
if ~isfield(wall,'wall_mask') || ~isfield(wall,'u_tau') || ~isfield(wall,'y_plus')
    error('cfd:turbulence:InvalidWallData', 'wall data missing required fields.');
end

kappa = 0.41;
E = 9.8;
idx = find(wall.wall_mask);
if isempty(idx)
    turb = cfd.turbulence.TurbulenceFieldLimiter(turb);
    return;
end

if isfield(turb,'k')
    turb.k(idx) = max(turb.k(idx), wall.u_tau(idx).^2 / sqrt(0.09));
end
if isfield(turb,'epsilon')
    y = max(wall.y(idx),1e-8);
    turb.epsilon(idx) = max(turb.epsilon(idx), wall.u_tau(idx).^3 ./ (kappa*y));
end
if isfield(turb,'omega')
    y = max(wall.y(idx),1e-8);
    turb.omega(idx) = max(turb.omega(idx), wall.u_tau(idx) ./ (kappa*y));
end
if isfield(turb,'nut')
    yp = max(wall.y_plus(idx),11.06);
    uplus = (1/kappa)*log(E*yp);
    turb.nut(idx) = max(turb.nut(idx), wall.nu(idx).*(yp./max(uplus,1e-6)-1));
end

turb = cfd.turbulence.TurbulenceFieldLimiter(turb);
end
