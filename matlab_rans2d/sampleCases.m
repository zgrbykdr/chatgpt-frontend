function c = sampleCases(caseName)
% Built-in sample cases.
c = defaultCase();

switch lower(strtrim(caseName))
    case 'laminar channel flow'
        c.name = 'Laminar Channel Flow';
        c.model = 'Laminar';
        c.geometry = 'channel';
        c.Lx = 4; c.Ly = 1; c.Nx = 80; c.Ny = 40;
        c.rho = 1.0; c.mu = 0.01;
        c.bc.inlet.Ux = 1.0; c.bc.inlet.Uy = 0.0;
        c.bc.inlet.intensity = 0.01;
        c.bc.inlet.lengthScale = 0.07*c.Ly;
        c.bc.top.type = 'wall'; c.bc.bottom.type = 'wall';
        c.maxIter = 1200; c.tol = 1e-6;
        c.urf.u = 0.7; c.urf.v = 0.7; c.urf.p = 0.3;

    case 'turbulent channel flow (k-epsilon)'
        c.name = 'Turbulent Channel k-epsilon';
        c.model = 'Standard k-epsilon';
        c.geometry = 'channel';
        c.Lx = 8; c.Ly = 1; c.Nx = 120; c.Ny = 60;
        c.rho = 1.225; c.mu = 1.8e-5;
        c.bc.inlet.Ux = 20.0; c.bc.inlet.Uy = 0.0;
        c.bc.inlet.intensity = 0.05; c.bc.inlet.lengthScale = 0.05*c.Ly;
        c.bc.top.type = 'wall'; c.bc.bottom.type = 'wall';
        c.maxIter = 2000; c.tol = 5e-5;

    case 'turbulent channel flow (k-omega)'
        c.name = 'Turbulent Channel k-omega';
        c.model = 'Standard k-omega';
        c.geometry = 'channel';
        c.Lx = 8; c.Ly = 1; c.Nx = 120; c.Ny = 60;
        c.rho = 1.225; c.mu = 1.8e-5;
        c.bc.inlet.Ux = 20.0; c.bc.inlet.Uy = 0.0;
        c.bc.inlet.intensity = 0.05; c.bc.inlet.lengthScale = 0.05*c.Ly;
        c.bc.top.type = 'wall'; c.bc.bottom.type = 'wall';
        c.maxIter = 2200; c.tol = 5e-5;

    case 'backward-facing step'
        c.name = 'Backward Facing Step';
        c.model = 'SST k-omega';
        c.geometry = 'bfs';
        c.Lx = 12; c.Ly = 1.5; c.Nx = 160; c.Ny = 60;
        c.stepHeight = 0.5;
        c.rho = 1.225; c.mu = 1.8e-5;
        c.bc.inlet.Ux = 15.0; c.bc.inlet.Uy = 0.0;
        c.bc.inlet.intensity = 0.05; c.bc.inlet.lengthScale = 0.05*c.Ly;
        c.bc.top.type = 'symmetry'; c.bc.bottom.type = 'wall';
        c.maxIter = 2500; c.tol = 1e-4;

    case 'flat plate boundary layer'
        c.name = 'Flat Plate Boundary Layer';
        c.model = 'Realizable k-epsilon';
        c.geometry = 'flatplate';
        c.Lx = 6; c.Ly = 1; c.Nx = 140; c.Ny = 60;
        c.rho = 1.225; c.mu = 1.8e-5;
        c.bc.inlet.Ux = 30.0; c.bc.inlet.Uy = 0.0;
        c.bc.inlet.intensity = 0.02; c.bc.inlet.lengthScale = 0.03*c.Ly;
        c.bc.top.type = 'symmetry'; c.bc.bottom.type = 'wall';
        c.maxIter = 2000; c.tol = 1e-4;

    otherwise
        % keep default
end

c.bc.inlet.Dh = 2*c.Ly;
end
