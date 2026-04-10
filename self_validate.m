function report = self_validate()
%SELF_VALIDATE Run geometry/mesh/solver/turbulence self-validation suite.

report = struct('geometry',false,'mesh',false,'solver',false,'turbulence',false,'errors',{{}});

try
    cfg = cfd.config.defaultConfig();
    cfg.geometry.mode = 'parametric';
    cfg.solver.time_mode = 'steady';
    cfg.solver.solver_type = 'SIMPLE';

    geomSrc = struct('points', [0 0; 3 0; 3 1; 0 1; 0 0]);
    g = cfd.geom.processGeometryPipeline(cfg, geomSrc, struct('attempt_recovery', true));
    report.geometry = ~isempty(g.poly) && g.quality.is_watertight;
catch ME
    report.errors{end+1} = ['geometry: ' ME.message];
end

try
    if ~exist('g','var')
        error('geometry_missing', 'Geometry state was not produced.');
    end
    m = cfd.mesh.processMeshPipeline(cfg, g, struct('workflow','watertight','auto_remesh',true));
    q = cfd.quality.MeshQualityGate(m, cfd.quality.defaultQualityThresholds());
    report.mesh = ~isempty(m.elements) && islogical(q.pass);
catch ME
    report.errors{end+1} = ['mesh: ' ME.message];
end

try
    if ~exist('m','var')
        error('mesh_missing', 'Mesh state was not produced.');
    end
    m = cfd.mesh.convertToFvTopology(m);
    s = cfd.solver.PressureBasedSolver(cfg, m, struct('max_iterations', 20));
    report.solver = isfield(s,'u') && isfield(s,'p') && numel(s.u) == size(m.fv.cell_centers,1);
catch ME
    report.errors{end+1} = ['solver: ' ME.message];
end

try
    if ~exist('s','var')
        error('solver_missing', 'Solver state was not produced.');
    end
    flow = struct('u',s.u,'v',s.v,'p',s.p);
    models = {'spalart_allmaras','k_epsilon_standard','k_epsilon_rng','k_epsilon_realizable','k_omega_standard','k_omega_sst'};
    ok = true;
    turb = struct();
    for i = 1:numel(models)
        cfg.turbulence.model = models{i};
        turb = cfd.turbulence.updateTurbulenceFields(cfg, m, flow, turb, 1e-3);
        [stable,~] = cfd.turbulence.validateTurbulenceState(turb);
        ok = ok && stable;
    end
    report.turbulence = ok;
catch ME
    report.errors{end+1} = ['turbulence: ' ME.message];
end

report.pass = report.geometry && report.mesh && report.solver && report.turbulence;
end
