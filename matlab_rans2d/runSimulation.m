function [state, report] = runSimulation(c, callbacks)
% Main SIMPLE/SIMPLEC steady-state loop.
if nargin < 2, callbacks = struct(); end
if ~isfield(callbacks,'onIter'), callbacks.onIter = @(varargin)[]; end
if ~isfield(callbacks,'isStopRequested'), callbacks.isStopRequested = @()false; end

mesh = generateMesh(c);
state = initFields(c, mesh);

report.mesh = mesh;
report.case = c;
report.messages = {};

for iter = 1:c.maxIter
    if callbacks.isStopRequested()
        report.messages{end+1} = 'Simulation stopped by user.';
        break;
    end

    prev = state;
    state.iter = iter;

    % Requested update sequence
    state = applyBoundaryConditions(state, c, mesh);
    state = updateTurbulenceViscosity(state, c, mesh);
    [state, mom] = solveMomentum(state, c, mesh);
    [state, massImb] = solvePressureCorrection(state, mom, c, mesh);
    state = applyBoundaryConditions(state, c, mesh);
    state = solveTurbulence(state, c, mesh);

    [res, sumres] = computeResiduals(prev, state, c, mesh, iter);
    state.residualHistory(iter,:) = [res.u,res.v,res.p,res.k,res.epsilon,res.omega,res.global,massImb];
    state.massImbalanceHistory(iter,1) = massImb;

    callbacks.onIter(iter, state, res, massImb);
    drawnow limitrate;

    if sumres.diverged || isnan(res.global) || isinf(res.global) || res.global > 1e6
        state.diverged = true;
        report.messages{end+1} = sprintf('Divergence at iteration %d', iter);
        break;
    end

    if res.global < c.tol && massImb < max(1e-8, 0.1*c.tol)
        state.converged = true;
        report.messages{end+1} = sprintf('Converged at iteration %d', iter);
        break;
    end
end

% Ensure histories are non-empty for GUI
if isempty(state.massImbalanceHistory)
    state.massImbalanceHistory = NaN;
end
if isempty(state.residualHistory)
    state.residualHistory = NaN(1,8);
end

report.validation = validationChecks(state, c, mesh);
report.post = postProcess(state, c, mesh);
end
