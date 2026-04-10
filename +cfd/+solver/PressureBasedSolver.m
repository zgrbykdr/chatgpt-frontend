function solution = PressureBasedSolver(cfg, mesh_state, options)
%PRESSUREBASEDSOLVER 2D incompressible pressure-based collocated FVM solver.
% Supports SIMPLE / SIMPLEC / PISO, steady/transient, upwind schemes,
% sparse assembly, GMRES/BiCGSTAB, under-relaxation, convergence monitoring.

if nargin < 3
    options = struct();
end
cfg = cfd.config.validateConfig(cfg);
mesh_state = iValidateMeshState(mesh_state);
opts = iNormalizeOptions(options);

nCells = size(mesh_state.fv.cell_centers,1);
if nCells < 1
    error('cfd:solver:NoCells', 'Mesh must contain FV cells.');
end

u = zeros(nCells,1);
v = zeros(nCells,1);
p = zeros(nCells,1);

if isfield(cfg.boundaries,'inlet') && isfield(cfg.boundaries.inlet,'velocity')
    vel = cfg.boundaries.inlet.velocity;
    if numel(vel)==2
        u(:) = vel(1);
        v(:) = vel(2);
    end
end

monitor = cfd.solver.ResidualMonitor(opts.max_iterations);
state = struct('mesh', mesh_state);
turb = struct();

time = 0;
step = 0;
maxSteps = 1;
if strcmp(cfg.solver.time_mode, 'transient')
    maxSteps = max(1, ceil(opts.t_end / opts.dt));
end

for tstep = 1:maxSteps
    step = tstep;
    if strcmp(cfg.solver.time_mode, 'transient')
        time = (tstep-1)*opts.dt;
    end

    for iter = 1:opts.max_iterations
        urf = cfd.solver.UnderRelaxationController(cfg, iter, monitor);
        fields = struct('u',u,'v',v,'p',p,'dt',opts.dt,'urf',urf, ...
            'convection_scheme', opts.convection_scheme, ...
            'linear_solver', opts.linear_solver, ...
            'lin_tol', opts.linear_tolerance, ...
            'lin_maxit', opts.linear_max_iterations);
        if isfield(turb,'nut')
            fields.muEff = cfg.materials.viscosity + cfg.materials.density*turb.nut;
        else
            fields.muEff = cfg.materials.viscosity;
        end

        switch upper(cfg.solver.solver_type)
            case 'SIMPLE'
                [uNew,vNew,pNew,res] = cfd.solver.CouplingSchemeSIMPLE(state,cfg,fields);
            case 'SIMPLEC'
                [uNew,vNew,pNew,res] = cfd.solver.CouplingSchemeSIMPLEC(state,cfg,fields);
            case 'PISO'
                [uNew,vNew,pNew,res] = cfd.solver.CouplingSchemePISO(state,cfg,fields);
            otherwise
                error('cfd:solver:UnknownSolverType', 'Unknown solver type: %s', cfg.solver.solver_type);
        end

        u = urf.u*uNew + (1-urf.u)*u;
        v = urf.v*vNew + (1-urf.v)*v;
        p = urf.p*pNew + (1-urf.p)*p;

        flow = struct('u',u,'v',v,'p',p);
        turb = cfd.turbulence.updateTurbulenceFields(cfg, mesh_state, flow, turb, opts.dt);

        monitor = cfd.solver.updateResidualMonitor(monitor, iter, res.u, res.v, res.p, res.continuity);
        [isConv, ~] = cfd.solver.ConvergenceController(monitor, opts.residual_tolerances, opts.min_iterations);
        if isConv
            break;
        end
    end

    if strcmp(cfg.solver.time_mode,'steady')
        break;
    end
end

solution = struct();
solution.u = u;
solution.v = v;
solution.p = p;
solution.time = time;
solution.time_step = step;
solution.iterations = monitor.iteration;
solution.residual_monitor = monitor;
solution.converged = cfd.solver.ConvergenceController(monitor, opts.residual_tolerances, opts.min_iterations);
solution.turbulence = turb;
solution.settings = opts;
end

function mesh_state = iValidateMeshState(mesh_state)
if ~isstruct(mesh_state) || ~isscalar(mesh_state)
    error('cfd:solver:InvalidMeshState', 'mesh_state must be scalar struct.');
end
req = {'nodes','elements','fv'};
for i = 1:numel(req)
    if ~isfield(mesh_state, req{i})
        error('cfd:solver:MissingMeshField', 'mesh_state missing field %s', req{i});
    end
end
if ~isfield(mesh_state.fv,'cell_centers') || ~isfield(mesh_state.fv,'cell_areas')
    mesh_state = cfd.mesh.convertToFvTopology(mesh_state);
end
end

function opts = iNormalizeOptions(options)
def = struct();
def.max_iterations = 500;
def.min_iterations = 5;
def.dt = 1e-3;
def.t_end = 0.1;
def.convection_scheme = 'first_order_upwind';
def.linear_solver = 'gmres';
def.linear_tolerance = 1e-8;
def.linear_max_iterations = 200;
def.residual_tolerances = struct('u',1e-6,'v',1e-6,'p',1e-5,'continuity',1e-6);
opts = cfd.config.mergeConfig(def, options);

validScheme = {'first_order_upwind','second_order_upwind'};
if ~any(strcmpi(opts.convection_scheme, validScheme))
    error('cfd:solver:InvalidConvectionScheme', 'Unsupported convection scheme.');
end
if ~(isnumeric(opts.max_iterations)&&isscalar(opts.max_iterations)&&opts.max_iterations>=1)
    error('cfd:solver:InvalidMaxIterations', 'max_iterations must be >= 1');
end
end
