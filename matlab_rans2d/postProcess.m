function post = postProcess(s, c, mesh)
% Post-processing quantities and derived metrics.
U = hypot(s.u, s.v);
post.Umag = U;
post.maxU = max(U(:));
post.maxMut = max(s.mut(:));

Nx = mesh.Nx;
outMask = mesh.fluidMask(:,Nx);
if any(outMask)
    post.avgOutletVelocity = mean(s.u(outMask,Nx));
else
    post.avgOutletVelocity = NaN;
end

post.pressureDrop = mean(s.p(mesh.fluidMask(:,1),1)) - mean(s.p(outMask,Nx));

if ~isempty(s.massImbalanceHistory)
    post.massImbalance = s.massImbalanceHistory(end);
else
    post.massImbalance = NaN;
end

rho = c.rho; mu = c.mu;
if mesh.Ny > 1
    duDyBottom = abs((s.u(2,:)-s.u(1,:))/max(mesh.yc(2)-mesh.yc(1),1e-12));
    tauwBottom = mu*duDyBottom;
    uTauBottom = sqrt(max(tauwBottom/rho,0));
    y1 = mesh.wallDist(1,:);
    yPlusBottom = rho*uTauBottom.*y1/mu;

    duDyTop = abs((s.u(end,:)-s.u(end-1,:))/max(mesh.yc(end)-mesh.yc(end-1),1e-12));
    tauwTop = mu*duDyTop;
    uTauTop = sqrt(max(tauwTop/rho,0));
    yN = mesh.wallDist(end,:);
    yPlusTop = rho*uTauTop.*yN/mu;

    post.yPlus = [yPlusBottom(:); yPlusTop(:)];
    post.tauWall = [tauwBottom(:); tauwTop(:)];
else
    post.yPlus = NaN;
    post.tauWall = NaN;
end

post.yPlusMin = min(post.yPlus);
post.yPlusMax = max(post.yPlus);
post.yPlusMean = mean(post.yPlus);

jc = max(1, round(mesh.Ny/2));
post.centerline.x = mesh.xc;
post.centerline.u = s.u(jc,:);
post.centerline.p = s.p(jc,:);

ic = max(1, round(mesh.Nx/2));
post.vertical.y = mesh.yc;
post.vertical.u = s.u(:,ic);
end
