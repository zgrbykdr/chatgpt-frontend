function tin = computeTurbulenceInlet(c)
% Convert inlet turbulence specification into k/epsilon/omega.
U = hypot(c.bc.inlet.Ux, c.bc.inlet.Uy);
I = max(1e-4, c.bc.inlet.intensity);

if strcmpi(c.bc.inlet.turbulenceInput, 'I-Dh')
    L = 0.07*max(1e-8, c.bc.inlet.Dh);
else
    L = max(1e-8, c.bc.inlet.lengthScale);
end

k = 1.5*(U*I)^2;
Cmu = 0.09;
epsilon = Cmu^(3/4) * k^(3/2) / L;
omega = sqrt(k)/(0.09^(1/4)*L);

tin.k = max(k, c.clip.kMin);
tin.epsilon = max(epsilon, c.clip.epsMin);
tin.omega = max(omega, c.clip.omMin);
end
