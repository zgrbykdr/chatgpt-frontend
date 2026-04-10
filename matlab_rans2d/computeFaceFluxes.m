function flux = computeFaceFluxes(s, c, mesh)
% Compute mass fluxes on cell faces for continuity and pressure correction.
Ny = mesh.Ny; Nx = mesh.Nx;
rho = c.rho;

flux.Fe = zeros(Ny, Nx);
flux.Fw = zeros(Ny, Nx);
flux.Fn = zeros(Ny, Nx);
flux.Fs = zeros(Ny, Nx);

for j = 1:Ny
    dy = mesh.dy(j);
    for i = 1:Nx
        if ~mesh.fluidMask(j,i)
            continue;
        end

        iW = max(1, i-1);
        iE = min(Nx, i+1);
        jS = max(1, j-1);
        jN = min(Ny, j+1);

        uW = 0.5*(s.u(j,iW) + s.u(j,i));
        uE = 0.5*(s.u(j,i) + s.u(j,iE));
        vS = 0.5*(s.v(jS,i) + s.v(j,i));
        vN = 0.5*(s.v(j,i) + s.v(jN,i));

        flux.Fw(j,i) = rho*uW*dy;
        flux.Fe(j,i) = rho*uE*dy;

        dx = mesh.dx(i);
        flux.Fs(j,i) = rho*vS*dx;
        flux.Fn(j,i) = rho*vN*dx;
    end
end
end
