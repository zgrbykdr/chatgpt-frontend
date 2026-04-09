function s = updateTurbulenceViscosity(s, c, mesh)
% Update turbulent viscosity based on selected model.
model = lower(strtrim(c.model));
rho = c.rho;

k = max(s.k, c.clip.kMin);
epsv = max(s.epsilon, c.clip.epsMin);
om = max(s.omega, c.clip.omMin);

switch model
    case 'laminar'
        mut = zeros(size(k));

    case 'standard k-epsilon'
        Cmu = 0.09;
        mut = Cmu * rho .* (k.^2) ./ epsv;

    case 'rng k-epsilon'
        Cmu = 0.0845;
        eta = sqrt(max(2*(gradientX(s.u,mesh).^2 + gradientY(s.v,mesh).^2),1e-16)) .* (k./epsv);
        fRng = 1 ./ (1 + eta.^3);
        mut = Cmu * fRng .* rho .* (k.^2) ./ epsv;

    case 'realizable k-epsilon'
        S = sqrt(2*(gradientX(s.u,mesh).^2 + gradientY(s.v,mesh).^2));
        A0 = 4.04;
        Us = sqrt(max(k,1e-12));
        Cmu = 1 ./ (A0 + S.*k./max(epsv,1e-10));
        Cmu = max(0.02, min(0.25, Cmu + 0.*Us));
        mut = rho .* Cmu .* (k.^2) ./ epsv;

    case 'standard k-omega'
        mut = rho .* k ./ om;

    case 'sst k-omega'
        d = max(mesh.wallDist, 1e-8);
        nu = c.mu/c.rho;
        CDkw = max(2*rho*0.856./max(om,1e-10).*gradientX(k,mesh).*gradientX(om,mesh),1e-20);
        arg1 = min(max(sqrt(k)./(0.09*om.*d), 500*nu./(d.^2.*om)), 4*rho*0.856*k./(CDkw.*d.^2));
        F1 = tanh(arg1.^4);
        a1 = 0.31;
        S = sqrt(2*(gradientX(s.u,mesh).^2 + gradientY(s.v,mesh).^2));
        mutRaw = rho*a1*k./max(a1*om, S.*F1 + 1e-12);
        mut = mutRaw;

    otherwise
        mut = zeros(size(k));
end

mut = max(0, min(mut, c.clip.mutMax));
if isfield(mesh,'fluidMask')
    mut(~mesh.fluidMask) = 0;
end
s.mut = mut;
end

function gx = gradientX(phi,mesh)
[Ny,Nx] = size(phi); gx = zeros(Ny,Nx);
for i=2:Nx-1
    gx(:,i) = (phi(:,i+1)-phi(:,i-1))./(mesh.xc(i+1)-mesh.xc(i-1));
end
gx(:,1)=gx(:,2); gx(:,Nx)=gx(:,Nx-1);
end

function gy = gradientY(phi,mesh)
[Ny,Nx] = size(phi); gy = zeros(Ny,Nx);
for j=2:Ny-1
    gy(j,:) = (phi(j+1,:)-phi(j-1,:))./(mesh.yc(j+1)-mesh.yc(j-1));
end
gy(1,:)=gy(2,:); gy(Ny,:)=gy(Ny-1,:);
end
