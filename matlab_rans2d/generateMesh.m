function mesh = generateMesh(c)
% Structured orthogonal mesh for rectangular domain.
Nx = c.Nx; Ny = c.Ny;
mesh.Nx = Nx; mesh.Ny = Ny;
mesh.Lx = c.Lx; mesh.Ly = c.Ly;

xFaces = linspace(0, c.Lx, Nx+1);
yFaces = linspace(0, c.Ly, Ny+1);

mesh.xf = xFaces;
mesh.yf = yFaces;
mesh.xc = 0.5*(xFaces(1:end-1)+xFaces(2:end));
mesh.yc = 0.5*(yFaces(1:end-1)+yFaces(2:end));

mesh.dx = diff(xFaces);
mesh.dy = diff(yFaces);
mesh.DX = repmat(mesh.dx, Ny, 1);
mesh.DY = repmat(mesh.dy(:), 1, Nx);
mesh.vol = mesh.DX .* mesh.DY;

% Wall distance approximation (to nearest horizontal wall)
ycCol = mesh.yc(:);
wd = min(ycCol, c.Ly-ycCol);
mesh.wallDist = repmat(wd, 1, Nx);

% Solid mask for BFS geometry
mesh.fluidMask = true(Ny, Nx);
if isfield(c,'geometry') && strcmpi(c.geometry, 'bfs')
    yStep = c.stepHeight;
    xStepEnd = 0.15*c.Lx;
    for i = 1:Nx
        if mesh.xc(i) < xStepEnd
            for j = 1:Ny
                if mesh.yc(j) < yStep
                    mesh.fluidMask(j,i) = false;
                end
            end
        end
    end
end
end
