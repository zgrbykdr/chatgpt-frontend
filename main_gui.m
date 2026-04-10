function main_gui()
%MAIN_GUI CFD desktop GUI (Fluent-like control hub) for MATLAB R2022b.
% Provides access to configuration, geometry, meshing, quality, solver,
% turbulence, orchestration, self-validation, and logs.

app = struct();
app.state = struct();
app.state.cfg = cfd.config.defaultConfig();
app.state.geometry = [];
app.state.mesh = [];
app.state.quality = [];
app.state.solution = [];
app.state.post = [];
app.state.last_result = [];

fig = uifigure('Name','MATLAB CFD Workbench','Position',[50 50 1400 860]);
app.fig = fig;

grid = uigridlayout(fig,[3 5]);
grid.RowHeight = {36, '1x', 220};
grid.ColumnWidth = {'1x','1x','1x','1x','1x'};

% Top controls
app.casePath = uieditfield(grid,'text','Placeholder','Path to case_config.json or leave empty for default');
app.casePath.Layout.Row = 1; app.casePath.Layout.Column = [1 3];

app.loadCfgBtn = uibutton(grid,'Text','Load Config','ButtonPushedFcn',@onLoadConfig);
app.loadCfgBtn.Layout.Row = 1; app.loadCfgBtn.Layout.Column = 4;

app.runCaseBtn = uibutton(grid,'Text','Run Full Case','ButtonPushedFcn',@onRunCase);
app.runCaseBtn.Layout.Row = 1; app.runCaseBtn.Layout.Column = 5;

% Tabs
tabs = uitabgroup(grid);
tabs.Layout.Row = 2; tabs.Layout.Column = [1 5];

cfgTab = uitab(tabs,'Title','Config');
geomTab = uitab(tabs,'Title','Geometry');
meshTab = uitab(tabs,'Title','Meshing');
qualityTab = uitab(tabs,'Title','Quality');
solverTab = uitab(tabs,'Title','Solver');
turbTab = uitab(tabs,'Title','Turbulence');
orchTab = uitab(tabs,'Title','Orchestrator');

app.logArea = uitextarea(grid,'Editable','off');
app.logArea.Layout.Row = 3; app.logArea.Layout.Column = [1 5];
app.logArea.Value = {sprintf('[%s] GUI started.', iNow())};

% Config tab
cfgGrid = uigridlayout(cfgTab,[5 4]);
cfgGrid.RowHeight = {30,30,30,30,'1x'};
cfgGrid.ColumnWidth = {150,200,150,200};

uilabel(cfgGrid,'Text','Solver Type').Layout.Row=1; 
app.cfgSolverType = uidropdown(cfgGrid,'Items',{'SIMPLE','SIMPLEC','PISO'},'Value',app.state.cfg.solver.solver_type);
app.cfgSolverType.Layout.Row=1; app.cfgSolverType.Layout.Column=2;

uilabel(cfgGrid,'Text','Time Mode').Layout.Row=1; uilabel(cfgGrid,'Text','Time Mode').Layout.Column=3;
app.cfgTimeMode = uidropdown(cfgGrid,'Items',{'steady','transient'},'Value',app.state.cfg.solver.time_mode);
app.cfgTimeMode.Layout.Row=1; app.cfgTimeMode.Layout.Column=4;

uilabel(cfgGrid,'Text','Turbulence').Layout.Row=2;
app.cfgTurb = uidropdown(cfgGrid,'Items',{'spalart_allmaras','k_epsilon_standard','k_epsilon_rng','k_epsilon_realizable','k_omega_standard','k_omega_sst'}, ...
    'Value',app.state.cfg.turbulence.model);
app.cfgTurb.Layout.Row=2; app.cfgTurb.Layout.Column=2;

uilabel(cfgGrid,'Text','Global Size').Layout.Row=2; uilabel(cfgGrid,'Text','Global Size').Layout.Column=3;
app.cfgGlobalSize = uieditfield(cfgGrid,'numeric','Value',app.state.cfg.meshing.global_size);
app.cfgGlobalSize.Layout.Row=2; app.cfgGlobalSize.Layout.Column=4;

app.applyCfgBtn = uibutton(cfgGrid,'Text','Apply Config Changes','ButtonPushedFcn',@onApplyConfig);
app.applyCfgBtn.Layout.Row=3; app.applyCfgBtn.Layout.Column=[1 2];
app.saveCfgBtn = uibutton(cfgGrid,'Text','Save Config JSON','ButtonPushedFcn',@onSaveConfig);
app.saveCfgBtn.Layout.Row=3; app.saveCfgBtn.Layout.Column=[3 4];

app.cfgPreview = uitextarea(cfgGrid,'Editable','off');
app.cfgPreview.Layout.Row=[4 5]; app.cfgPreview.Layout.Column=[1 4];
refreshConfigPreview();

% Geometry tab
geomGrid = uigridlayout(geomTab,[4 4]);
geomGrid.RowHeight = {30,30,30,'1x'};
geomGrid.ColumnWidth = {'1x','1x','1x','1x'};
app.geomImportBtn = uibutton(geomGrid,'Text','Process Geometry','ButtonPushedFcn',@onProcessGeometry);
app.geomImportBtn.Layout.Row=1; app.geomImportBtn.Layout.Column=1;
app.geomPlotBtn = uibutton(geomGrid,'Text','Debug Plot Geometry','ButtonPushedFcn',@onPlotGeometry);
app.geomPlotBtn.Layout.Row=1; app.geomPlotBtn.Layout.Column=2;
app.geomRepairBtn = uibutton(geomGrid,'Text','Repair Topology','ButtonPushedFcn',@onRepairGeometry);
app.geomRepairBtn.Layout.Row=1; app.geomRepairBtn.Layout.Column=3;
app.geomWrapBtn = uibutton(geomGrid,'Text','Wrap Geometry','ButtonPushedFcn',@onWrapGeometry);
app.geomWrapBtn.Layout.Row=1; app.geomWrapBtn.Layout.Column=4;
app.geomInfo = uitextarea(geomGrid,'Editable','off');
app.geomInfo.Layout.Row=[2 4]; app.geomInfo.Layout.Column=[1 4];

% Mesh tab
meshGrid = uigridlayout(meshTab,[4 4]);
meshGrid.RowHeight = {30,30,30,'1x'};
meshGrid.ColumnWidth = {'1x','1x','1x','1x'};
app.meshGenBtn = uibutton(meshGrid,'Text','Generate Mesh','ButtonPushedFcn',@onGenerateMesh);
app.meshGenBtn.Layout.Row=1; app.meshGenBtn.Layout.Column=1;
app.meshSmoothBtn = uibutton(meshGrid,'Text','Smooth Mesh','ButtonPushedFcn',@onSmoothMesh);
app.meshSmoothBtn.Layout.Row=1; app.meshSmoothBtn.Layout.Column=2;
app.meshRepairBtn = uibutton(meshGrid,'Text','Repair Mesh','ButtonPushedFcn',@onRepairMesh);
app.meshRepairBtn.Layout.Row=1; app.meshRepairBtn.Layout.Column=3;
app.meshFvBtn = uibutton(meshGrid,'Text','Build FV Topology','ButtonPushedFcn',@onBuildFv);
app.meshFvBtn.Layout.Row=1; app.meshFvBtn.Layout.Column=4;
app.meshInfo = uitextarea(meshGrid,'Editable','off');
app.meshInfo.Layout.Row=[2 4]; app.meshInfo.Layout.Column=[1 4];

% Quality tab
qGrid = uigridlayout(qualityTab,[4 4]);
qGrid.RowHeight={30,30,30,'1x'};
qGrid.ColumnWidth={'1x','1x','1x','1x'};
app.qualityAnalyzeBtn = uibutton(qGrid,'Text','Analyze Quality','ButtonPushedFcn',@onAnalyzeQuality);
app.qualityAnalyzeBtn.Layout.Row=1; app.qualityAnalyzeBtn.Layout.Column=1;
app.qualityGateBtn = uibutton(qGrid,'Text','Quality Gate','ButtonPushedFcn',@onQualityGate);
app.qualityGateBtn.Layout.Row=1; app.qualityGateBtn.Layout.Column=2;
app.qualityRepairBtn = uibutton(qGrid,'Text','Repair Engine','ButtonPushedFcn',@onQualityRepair);
app.qualityRepairBtn.Layout.Row=1; app.qualityRepairBtn.Layout.Column=3;
app.qualityInfo = uitextarea(qGrid,'Editable','off');
app.qualityInfo.Layout.Row=[2 4]; app.qualityInfo.Layout.Column=[1 4];

% Solver tab
sGrid = uigridlayout(solverTab,[4 4]);
sGrid.RowHeight={30,30,30,'1x'};
sGrid.ColumnWidth={'1x','1x','1x','1x'};
app.solveBtn = uibutton(sGrid,'Text','Run Solver','ButtonPushedFcn',@onSolve);
app.solveBtn.Layout.Row=1; app.solveBtn.Layout.Column=1;
app.postBtn = uibutton(sGrid,'Text','Postprocess','ButtonPushedFcn',@onPostprocess);
app.postBtn.Layout.Row=1; app.postBtn.Layout.Column=2;
app.selfValBtn = uibutton(sGrid,'Text','Self Validate','ButtonPushedFcn',@onSelfValidate);
app.selfValBtn.Layout.Row=1; app.selfValBtn.Layout.Column=3;
app.solverInfo = uitextarea(sGrid,'Editable','off');
app.solverInfo.Layout.Row=[2 4]; app.solverInfo.Layout.Column=[1 4];

% Turbulence tab
tGrid = uigridlayout(turbTab,[4 4]);
tGrid.RowHeight={30,30,30,'1x'};
tGrid.ColumnWidth={'1x','1x','1x','1x'};
app.turbRunBtn = uibutton(tGrid,'Text','Update Turbulence Once','ButtonPushedFcn',@onUpdateTurbulence);
app.turbRunBtn.Layout.Row=1; app.turbRunBtn.Layout.Column=1;
app.turbInfo = uitextarea(tGrid,'Editable','off');
app.turbInfo.Layout.Row=[2 4]; app.turbInfo.Layout.Column=[1 4];

% Orchestrator tab
oGrid = uigridlayout(orchTab,[4 4]);
oGrid.RowHeight={30,30,30,'1x'};
oGrid.ColumnWidth={'1x','1x','1x','1x'};
app.resumeChk = uicheckbox(oGrid,'Text','Resume from Checkpoint','Value',false);
app.resumeChk.Layout.Row=1; app.resumeChk.Layout.Column=1;
app.safeTermChk = uicheckbox(oGrid,'Text','Safe Termination','Value',true);
app.safeTermChk.Layout.Row=1; app.safeTermChk.Layout.Column=2;
app.orchRunBtn = uibutton(oGrid,'Text','Run Orchestrator','ButtonPushedFcn',@onRunCase);
app.orchRunBtn.Layout.Row=1; app.orchRunBtn.Layout.Column=3;
app.orchInfo = uitextarea(oGrid,'Editable','off');
app.orchInfo.Layout.Row=[2 4]; app.orchInfo.Layout.Column=[1 4];

logMsg('GUI ready.');

    function onLoadConfig(~,~)
        try
            path = strtrim(app.casePath.Value);
            if isempty(path)
                app.state.cfg = cfd.config.defaultConfig();
            else
                app.state.cfg = cfd.config.loadConfig(path, struct(), true);
            end
            refreshConfigWidgets();
            refreshConfigPreview();
            logMsg('Config loaded successfully.');
        catch ME
            logError(ME);
        end
    end

    function onApplyConfig(~,~)
        try
            app.state.cfg.solver.solver_type = app.cfgSolverType.Value;
            app.state.cfg.solver.time_mode = app.cfgTimeMode.Value;
            app.state.cfg.turbulence.model = app.cfgTurb.Value;
            app.state.cfg.meshing.global_size = app.cfgGlobalSize.Value;
            app.state.cfg = cfd.config.validateConfig(app.state.cfg);
            refreshConfigPreview();
            logMsg('Config changes applied.');
        catch ME
            logError(ME);
        end
    end

    function onSaveConfig(~,~)
        try
            [f,p] = uiputfile('*.json','Save Config As');
            if isequal(f,0); return; end
            cfd.config.saveConfig(app.state.cfg, fullfile(p,f));
            logMsg(['Config saved: ' fullfile(p,f)]);
        catch ME
            logError(ME);
        end
    end

    function onProcessGeometry(~,~)
        try
            src = iCurrentGeometrySource();
            app.state.geometry = cfd.geom.processGeometryPipeline(app.state.cfg, src, struct('attempt_recovery', true));
            app.geomInfo.Value = {sprintf('Status: %s', app.state.geometry.status), sprintf('Area: %.6g', app.state.geometry.metrics.area)};
            logMsg('Geometry stage completed.');
        catch ME
            logError(ME);
        end
    end

    function onPlotGeometry(~,~)
        try
            ensureGeometry();
            cfd.geom.debugVisualizeGeometry(app.state.geometry,'GUI Geometry Debug');
            logMsg('Geometry debug figure opened.');
        catch ME
            logError(ME);
        end
    end

    function onRepairGeometry(~,~)
        try
            ensureGeometry();
            app.state.geometry = cfd.geom.repairTopology(app.state.geometry);
            app.state.geometry = cfd.geom.validateWatertight(app.state.geometry,1e-8);
            logMsg('Geometry repaired and watertight check updated.');
        catch ME
            logError(ME);
        end
    end

    function onWrapGeometry(~,~)
        try
            ensureGeometry();
            app.state.geometry = cfd.geom.wrapSkinGeometry(app.state.geometry, NaN);
            logMsg('Geometry wrapping completed.');
        catch ME
            logError(ME);
        end
    end

    function onGenerateMesh(~,~)
        try
            ensureGeometry();
            app.state.mesh = cfd.mesh.processMeshPipeline(app.state.cfg, app.state.geometry, struct('workflow','watertight','auto_remesh',true));
            app.meshInfo.Value = {sprintf('Nodes: %d', size(app.state.mesh.nodes,1)), sprintf('Elements: %d', size(app.state.mesh.elements,1))};
            logMsg('Meshing completed.');
        catch ME
            logError(ME);
        end
    end

    function onSmoothMesh(~,~)
        try
            ensureMesh();
            app.state.mesh = cfd.mesh.smoothMesh(app.state.mesh, 8);
            logMsg('Mesh smoothing completed.');
        catch ME
            logError(ME);
        end
    end

    function onRepairMesh(~,~)
        try
            ensureMesh(); ensureGeometry();
            app.state.mesh = cfd.mesh.repairBadElements(app.state.mesh, app.state.cfg, app.state.geometry, struct('quality_repair_iterations',3,'use_parallel',false,'auto_remesh',true));
            logMsg('Mesh repair completed.');
        catch ME
            logError(ME);
        end
    end

    function onBuildFv(~,~)
        try
            ensureMesh();
            app.state.mesh = cfd.mesh.convertToFvTopology(app.state.mesh);
            logMsg('FV topology created.');
        catch ME
            logError(ME);
        end
    end

    function onAnalyzeQuality(~,~)
        try
            ensureMesh();
            q = cfd.quality.analyzeMeshQuality(app.state.mesh);
            app.state.quality = q;
            app.qualityInfo.Value = {sprintf('Max skewness: %.6g', q.summary.max_skewness_equiangular), ...
                                     sprintf('Min orth quality: %.6g', q.summary.min_orthogonal_quality), ...
                                     sprintf('Max aspect: %.6g', q.summary.max_aspect_ratio)};
            logMsg('Quality analysis completed.');
        catch ME
            logError(ME);
        end
    end

    function onQualityGate(~,~)
        try
            ensureMesh();
            gate = cfd.quality.MeshQualityGate(app.state.mesh, cfd.quality.defaultQualityThresholds());
            app.state.quality_gate = gate;
            app.qualityInfo.Value = strsplit(gate.report, newline)';
            logMsg(sprintf('Quality gate pass=%d.', gate.pass));
        catch ME
            logError(ME);
        end
    end

    function onQualityRepair(~,~)
        try
            ensureMesh(); ensureGeometry();
            rr = cfd.quality.MeshRepairEngine(app.state.mesh, app.state.cfg, app.state.geometry, struct());
            app.state.mesh = rr.mesh_state;
            app.state.quality_gate = rr.final_gate;
            app.qualityInfo.Value = strsplit(rr.final_gate.report, newline)';
            logMsg(sprintf('Quality repair complete. pass=%d', rr.pass));
        catch ME
            logError(ME);
        end
    end

    function onSolve(~,~)
        try
            ensureMesh();
            app.state.mesh = cfd.mesh.convertToFvTopology(app.state.mesh);
            app.state.solution = cfd.solver.PressureBasedSolver(app.state.cfg, app.state.mesh, struct('max_iterations',200));
            app.solverInfo.Value = {sprintf('Converged: %d', app.state.solution.converged(1)), ...
                                    sprintf('Iterations: %d', app.state.solution.iterations)};
            logMsg('Solver completed.');
        catch ME
            logError(ME);
        end
    end

    function onPostprocess(~,~)
        try
            ensureSolution(); ensureMesh();
            app.state.post = cfd.post.PostProcessor(app.state.cfg, app.state.mesh, app.state.solution, fullfile(pwd,'outputs'));
            app.solverInfo.Value = {['CSV: ' app.state.post.cell_csv], ['Summary: ' app.state.post.summary_json]};
            logMsg('Postprocess completed.');
        catch ME
            logError(ME);
        end
    end

    function onUpdateTurbulence(~,~)
        try
            ensureMesh(); ensureSolution();
            flow = struct('u',app.state.solution.u,'v',app.state.solution.v,'p',app.state.solution.p);
            if ~isfield(app.state,'turb') || isempty(app.state.turb)
                app.state.turb = struct();
            end
            app.state.turb = cfd.turbulence.updateTurbulenceFields(app.state.cfg, app.state.mesh, flow, app.state.turb, 1e-3);
            [ok,details] = cfd.turbulence.validateTurbulenceState(app.state.turb);
            app.turbInfo.Value = {sprintf('Stable: %d',ok), sprintf('Invalid: %d',details.invalid_count), sprintf('Negative: %d',details.negative_count)};
            logMsg('Turbulence update executed.');
        catch ME
            logError(ME);
        end
    end

    function onSelfValidate(~,~)
        try
            rep = self_validate();
            app.solverInfo.Value = strsplit(jsonencode(rep, 'PrettyPrint', true), newline)';
            logMsg(sprintf('Self validation pass=%d', rep.pass));
        catch ME
            logError(ME);
        end
    end

    function onRunCase(~,~)
        try
            path = strtrim(app.casePath.Value);
            if isempty(path)
                inp = app.state.cfg;
            else
                inp = path;
            end
            opts = struct('resume', app.resumeChk.Value, 'safe_termination', app.safeTermChk.Value);
            res = run_case(inp, opts);
            app.state.last_result = res;
            app.orchInfo.Value = strsplit(jsonencode(struct('status',res.status,'stage',res.stage,'error',res.error), 'PrettyPrint', true), newline)';
            logMsg(['Orchestrator completed with status=' res.status]);
        catch ME
            logError(ME);
        end
    end

    function src = iCurrentGeometrySource()
        p = strtrim(app.casePath.Value);
        if ~isempty(p) && endsWith(lower(p), '.json')
            cfg = cfd.config.loadConfig(p, struct(), true);
            app.state.cfg = cfg;
            if strcmp(cfg.geometry.mode,'import') && ~isempty(cfg.geometry.file_path)
                src = cfg.geometry.file_path;
                return;
            end
        end
        if strcmp(app.state.cfg.geometry.mode,'import') && ~isempty(app.state.cfg.geometry.file_path)
            src = app.state.cfg.geometry.file_path;
        else
            src = struct('points',[0 0; 4 0; 4 1; 0 1; 0 0]);
        end
    end

    function ensureGeometry()
        if isempty(app.state.geometry)
            error('GUI:GeometryMissing', 'Geometry not available. Run geometry stage first.');
        end
    end

    function ensureMesh()
        if isempty(app.state.mesh)
            error('GUI:MeshMissing', 'Mesh not available. Run meshing stage first.');
        end
    end

    function ensureSolution()
        if isempty(app.state.solution)
            error('GUI:SolutionMissing', 'Solution not available. Run solver first.');
        end
    end

    function refreshConfigWidgets()
        app.cfgSolverType.Value = app.state.cfg.solver.solver_type;
        app.cfgTimeMode.Value = app.state.cfg.solver.time_mode;
        app.cfgTurb.Value = app.state.cfg.turbulence.model;
        app.cfgGlobalSize.Value = app.state.cfg.meshing.global_size;
    end

    function refreshConfigPreview()
        app.cfgPreview.Value = strsplit(jsonencode(app.state.cfg, 'PrettyPrint', true), newline)';
    end

    function logMsg(msg)
        line = sprintf('[%s] %s', iNow(), msg);
        app.logArea.Value = [app.logArea.Value; {line}];
        drawnow limitrate;
    end

    function logError(ME)
        logMsg(['ERROR: ' ME.message]);
        uialert(app.fig, ME.message, 'Operation Failed', 'Icon', 'error');
    end
end

function t = iNow()
t = char(datetime('now','Format','yyyy-MM-dd HH:mm:ss'));
end
