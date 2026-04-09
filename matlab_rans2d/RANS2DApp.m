function RANS2DApp
% Programmatic MATLAB 2022b GUI for 2D incompressible steady RANS.

app = struct();
app.case = defaultCase();
app.state = [];
app.report = [];
app.stopFlag = false;

app.fig = uifigure('Name','RANS2D Solver (MATLAB 2022b)','Position',[40 40 1500 860]);
mainGL = uigridlayout(app.fig,[1 2]);
mainGL.ColumnWidth = {420,'1x'};

left = uipanel(mainGL,'Title','Setup and Controls');
left.Layout.Column = 1;
leftGL = uigridlayout(left,[28 2]);
leftGL.RowHeight = [repmat({24},1,26),{28},{28}];
leftGL.ColumnWidth = {170,'1x'};

    function edt = addNum(r, label, val)
        uilabel(leftGL,'Text',label,'Layout',struct('Row',r,'Column',1));
        edt = uieditfield(leftGL,'numeric','Value',val,'Layout',struct('Row',r,'Column',2));
    end

app.ui.Lx = addNum(1,'Domain length Lx',app.case.Lx);
app.ui.Ly = addNum(2,'Domain height Ly',app.case.Ly);
app.ui.Nx = addNum(3,'Cells Nx',app.case.Nx);
app.ui.Ny = addNum(4,'Cells Ny',app.case.Ny);
app.ui.rho = addNum(5,'Density rho',app.case.rho);
app.ui.mu = addNum(6,'Dynamic viscosity mu',app.case.mu);
app.ui.Ux = addNum(7,'Inlet Ux',app.case.bc.inlet.Ux);
app.ui.Uy = addNum(8,'Inlet Uy',app.case.bc.inlet.Uy);
app.ui.pout = addNum(9,'Outlet pressure',app.case.bc.outlet.p);

uilabel(leftGL,'Text','Turbulence model','Layout',struct('Row',10,'Column',1));
app.ui.model = uidropdown(leftGL,'Items',{'Laminar','Standard k-epsilon','RNG k-epsilon','Realizable k-epsilon','Standard k-omega','SST k-omega'},...
    'Value',app.case.model,'Layout',struct('Row',10,'Column',2));

app.ui.I = addNum(11,'Turbulence intensity',app.case.bc.inlet.intensity);
app.ui.Lt = addNum(12,'Length scale',app.case.bc.inlet.lengthScale);
app.ui.Dh = addNum(13,'Hydraulic diameter',app.case.bc.inlet.Dh);

uilabel(leftGL,'Text','Turbulence input','Layout',struct('Row',14,'Column',1));
app.ui.turbIn = uidropdown(leftGL,'Items',{'I-L','I-Dh'},'Value',app.case.bc.inlet.turbulenceInput,...
    'Layout',struct('Row',14,'Column',2));

uilabel(leftGL,'Text','Discretization','Layout',struct('Row',15,'Column',1));
app.ui.scheme = uidropdown(leftGL,'Items',{'First-order upwind','Second-order upwind'},'Value',app.case.scheme,...
    'Layout',struct('Row',15,'Column',2));

uilabel(leftGL,'Text','Pressure-velocity','Layout',struct('Row',16,'Column',1));
app.ui.pv = uidropdown(leftGL,'Items',{'SIMPLE','SIMPLEC'},'Value',app.case.pvCoupling,...
    'Layout',struct('Row',16,'Column',2));

app.ui.urfU = addNum(17,'URF u',app.case.urf.u);
app.ui.urfV = addNum(18,'URF v',app.case.urf.v);
app.ui.urfP = addNum(19,'URF p',app.case.urf.p);
app.ui.urfK = addNum(20,'URF k',app.case.urf.k);
app.ui.urfE = addNum(21,'URF epsilon',app.case.urf.epsilon);
app.ui.urfO = addNum(22,'URF omega',app.case.urf.omega);
app.ui.maxIter = addNum(23,'Max iteration',app.case.maxIter);
app.ui.tol = addNum(24,'Residual tolerance',app.case.tol);

uilabel(leftGL,'Text','Top BC','Layout',struct('Row',25,'Column',1));
app.ui.topBC = uidropdown(leftGL,'Items',{'wall','symmetry'},'Value',app.case.bc.top.type,'Layout',struct('Row',25,'Column',2));
uilabel(leftGL,'Text','Bottom BC','Layout',struct('Row',26,'Column',1));
app.ui.botBC = uidropdown(leftGL,'Items',{'wall','symmetry'},'Value',app.case.bc.bottom.type,'Layout',struct('Row',26,'Column',2));

app.ui.sample = uidropdown(leftGL,'Items',{'Laminar channel flow','Turbulent channel flow (k-epsilon)','Turbulent channel flow (k-omega)','Backward-facing step','Flat plate boundary layer'},...
    'Value','Laminar channel flow','Layout',struct('Row',27,'Column',[1 2]));

btnGL = uigridlayout(leftGL,[1 6]); btnGL.Layout.Row = 28; btnGL.Layout.Column = [1 2];
btnGL.ColumnWidth = {'1x','1x','1x','1x','1x','1x'};
uibutton(btnGL,'Text','Load sample','ButtonPushedFcn',@onLoadSample);
uibutton(btnGL,'Text','Save case','ButtonPushedFcn',@onSaveCase);
uibutton(btnGL,'Text','Load case','ButtonPushedFcn',@onLoadCase);
uibutton(btnGL,'Text','Reset','ButtonPushedFcn',@onReset);
uibutton(btnGL,'Text','Start','BackgroundColor',[0.75 0.95 0.75],'ButtonPushedFcn',@onStart);
uibutton(btnGL,'Text','Stop','BackgroundColor',[0.95 0.75 0.75],'ButtonPushedFcn',@onStop);

rightTab = uitabgroup(mainGL); rightTab.Layout.Column = 2;

tabRuntime = uitab(rightTab,'Title','Runtime');
runGL = uigridlayout(tabRuntime,[2 2]); runGL.RowHeight = {260,'1x'};
app.ui.status = uitextarea(runGL,'Editable','off'); app.ui.status.Layout.Row = 1; app.ui.status.Layout.Column = 1;
app.ui.summary = uitextarea(runGL,'Editable','off'); app.ui.summary.Layout.Row = 1; app.ui.summary.Layout.Column = 2;
app.ui.resAx = uiaxes(runGL); app.ui.resAx.Layout.Row = 2; app.ui.resAx.Layout.Column = [1 2];
set(app.ui.resAx,'YScale','log'); grid(app.ui.resAx,'on'); title(app.ui.resAx,'Residual History');

app.ui.status.Value = {'Ready.'};
app.ui.summary.Value = {'Iteration: 0';'Mass imbalance: -';'Converged: 0';'Diverged: 0'};

fields = {'Velocity Magnitude','u','v','pressure','k','epsilon','omega','mut'};
for n = 1:numel(fields)
    t = uitab(rightTab,'Title',fields{n});
    app.ui.fieldAxes.(matlab.lang.makeValidName(fields{n})) = uiaxes(t,'Position',[10 10 1020 740]);
end

tabSP = uitab(rightTab,'Title','Streamlines/Profile');
spGL = uigridlayout(tabSP,[1 2]);
app.ui.streamAx = uiaxes(spGL); app.ui.profileAx = uiaxes(spGL);

tabWall = uitab(rightTab,'Title','y+ / Wall Shear');
wallGL = uigridlayout(tabWall,[1 2]);
app.ui.yplusAx = uiaxes(wallGL); app.ui.tauwAx = uiaxes(wallGL);

uibutton(tabRuntime,'Text','Export Results','Position',[10 10 120 26],'ButtonPushedFcn',@onExport);

setappdata(app.fig,'appData',app);

    function onLoadSample(~,~)
        app = getappdata(app.fig,'appData');
        app.case = sampleCases(app.ui.sample.Value);
        applyCaseToUI(app.case);
        appendStatus(['Loaded sample: ' app.case.name]);
        setappdata(app.fig,'appData',app);
    end

    function onSaveCase(~,~)
        app = getappdata(app.fig,'appData');
        app.case = readCaseFromUI();
        [f,p] = uiputfile('*.mat','Save case');
        if isequal(f,0), return; end
        caseData = app.case; %#ok<NASGU>
        save(fullfile(p,f),'caseData');
        appendStatus('Case saved.');
    end

    function onLoadCase(~,~)
        [f,p] = uigetfile('*.mat','Load case');
        if isequal(f,0), return; end
        S = load(fullfile(p,f));
        if isfield(S,'caseData')
            app = getappdata(app.fig,'appData');
            app.case = S.caseData;
            applyCaseToUI(app.case);
            appendStatus('Case loaded.');
            setappdata(app.fig,'appData',app);
        end
    end

    function onReset(~,~)
        app = getappdata(app.fig,'appData');
        app.case = defaultCase();
        applyCaseToUI(app.case);
        clearPlots();
        app.ui.status.Value = {'Reset to defaults.'};
        app.ui.summary.Value = {'Iteration: 0';'Mass imbalance: -';'Converged: 0';'Diverged: 0'};
        setappdata(app.fig,'appData',app);
    end

    function onStart(~,~)
        app = getappdata(app.fig,'appData');
        app.stopFlag = false;
        app.case = readCaseFromUI();
        clearPlots();
        appendStatus('Simulation started...');
        setappdata(app.fig,'appData',app);

        cb.onIter = @onIterUpdate;
        cb.isStopRequested = @()getStopFlag();
        [state, report] = runSimulation(app.case, cb);

        app = getappdata(app.fig,'appData');
        app.state = state;
        app.report = report;
        setappdata(app.fig,'appData',app);

        renderResults();

        if app.state.converged
            appendStatus('Converged successfully.');
        elseif app.state.diverged
            appendStatus('Diverged and stopped safely.');
        else
            appendStatus('Finished without strict convergence.');
        end

        m = lastMassImbalance(app.state);
        refreshSummary(app.state.iter, m, app.state.converged, app.state.diverged);
    end

    function onStop(~,~)
        app = getappdata(app.fig,'appData');
        app.stopFlag = true;
        setappdata(app.fig,'appData',app);
        appendStatus('Stop requested by user.');
    end

    function tf = getStopFlag()
        app = getappdata(app.fig,'appData');
        tf = app.stopFlag;
    end

    function onIterUpdate(iter, s, ~, massImb)
        app = getappdata(app.fig,'appData');
        if size(s.residualHistory,2) >= 8
            semilogy(app.ui.resAx, s.residualHistory(:,7),'k-','LineWidth',1.3); hold(app.ui.resAx,'on');
            semilogy(app.ui.resAx, s.residualHistory(:,1),'r-');
            semilogy(app.ui.resAx, s.residualHistory(:,2),'b-');
            semilogy(app.ui.resAx, s.residualHistory(:,3),'g-');
            semilogy(app.ui.resAx, s.residualHistory(:,8),'m-');
            hold(app.ui.resAx,'off');
            legend(app.ui.resAx,{'global','u','v','p','mass'},'Location','northeast');
        end
        refreshSummary(iter, massImb, s.converged, s.diverged);
        drawnow limitrate;
    end

    function onExport(~,~)
        app = getappdata(app.fig,'appData');
        if isempty(app.state)
            appendStatus('No simulation result to export.');
            return;
        end
        [f,p] = uiputfile('*.mat','Export base name',fullfile(pwd,'rans2d_result.mat'));
        if isequal(f,0), return; end
        [~,base] = fileparts(f);
        exportResults(fullfile(p,base), app.state, app.report);
        appendStatus('Export completed (MAT + CSV).');
    end

    function applyCaseToUI(c)
        app = getappdata(app.fig,'appData');
        app.ui.Lx.Value = c.Lx; app.ui.Ly.Value = c.Ly;
        app.ui.Nx.Value = c.Nx; app.ui.Ny.Value = c.Ny;
        app.ui.rho.Value = c.rho; app.ui.mu.Value = c.mu;
        app.ui.Ux.Value = c.bc.inlet.Ux; app.ui.Uy.Value = c.bc.inlet.Uy;
        app.ui.pout.Value = c.bc.outlet.p;
        app.ui.model.Value = c.model;
        app.ui.I.Value = c.bc.inlet.intensity;
        app.ui.Lt.Value = c.bc.inlet.lengthScale;
        app.ui.Dh.Value = c.bc.inlet.Dh;
        app.ui.turbIn.Value = c.bc.inlet.turbulenceInput;
        app.ui.scheme.Value = c.scheme;
        app.ui.pv.Value = c.pvCoupling;
        app.ui.urfU.Value = c.urf.u; app.ui.urfV.Value = c.urf.v; app.ui.urfP.Value = c.urf.p;
        app.ui.urfK.Value = c.urf.k; app.ui.urfE.Value = c.urf.epsilon; app.ui.urfO.Value = c.urf.omega;
        app.ui.maxIter.Value = c.maxIter; app.ui.tol.Value = c.tol;
        app.ui.topBC.Value = c.bc.top.type; app.ui.botBC.Value = c.bc.bottom.type;
        setappdata(app.fig,'appData',app);
    end

    function c = readCaseFromUI()
        app = getappdata(app.fig,'appData');
        c = app.case;
        c.Lx = app.ui.Lx.Value;
        c.Ly = app.ui.Ly.Value;
        c.Nx = max(8,round(app.ui.Nx.Value));
        c.Ny = max(6,round(app.ui.Ny.Value));
        c.rho = app.ui.rho.Value;
        c.mu = app.ui.mu.Value;
        c.bc.inlet.Ux = app.ui.Ux.Value;
        c.bc.inlet.Uy = app.ui.Uy.Value;
        c.bc.outlet.p = app.ui.pout.Value;
        c.model = app.ui.model.Value;
        c.bc.inlet.intensity = max(1e-4, app.ui.I.Value);
        c.bc.inlet.lengthScale = max(1e-8, app.ui.Lt.Value);
        c.bc.inlet.Dh = max(1e-8, app.ui.Dh.Value);
        c.bc.inlet.turbulenceInput = app.ui.turbIn.Value;
        c.scheme = app.ui.scheme.Value;
        c.pvCoupling = app.ui.pv.Value;
        c.urf.u = app.ui.urfU.Value; c.urf.v = app.ui.urfV.Value; c.urf.p = app.ui.urfP.Value;
        c.urf.k = app.ui.urfK.Value; c.urf.epsilon = app.ui.urfE.Value; c.urf.omega = app.ui.urfO.Value;
        c.maxIter = max(20, round(app.ui.maxIter.Value));
        c.tol = max(1e-10, app.ui.tol.Value);
        c.bc.top.type = app.ui.topBC.Value;
        c.bc.bottom.type = app.ui.botBC.Value;
    end

    function appendStatus(msg)
        app = getappdata(app.fig,'appData');
        stamp = datestr(now,'HH:MM:SS');
        app.ui.status.Value = [app.ui.status.Value; {[stamp '  ' msg]}];
    end

    function refreshSummary(iter, massImb, conv, div)
        app = getappdata(app.fig,'appData');
        app.ui.summary.Value = {
            sprintf('Iteration: %d',iter)
            sprintf('Mass imbalance: %.3e',massImb)
            sprintf('Converged: %d',conv)
            sprintf('Diverged: %d',div)
        };
    end

    function m = lastMassImbalance(state)
        if isempty(state.massImbalanceHistory)
            m = NaN;
        else
            m = state.massImbalanceHistory(end);
        end
    end

    function clearPlots()
        app = getappdata(app.fig,'appData');
        cla(app.ui.resAx);
        fn = fieldnames(app.ui.fieldAxes);
        for ii = 1:numel(fn)
            cla(app.ui.fieldAxes.(fn{ii}));
        end
        cla(app.ui.streamAx); cla(app.ui.profileAx); cla(app.ui.yplusAx); cla(app.ui.tauwAx);
    end

    function renderResults()
        app = getappdata(app.fig,'appData');
        if isempty(app.state), return; end
        s = app.state; mesh = app.report.mesh;
        [X,Y] = meshgrid(mesh.xc, mesh.yc);

        drawContour(app.ui.fieldAxes.VelocityMagnitude,X,Y,hypot(s.u,s.v),'Velocity Magnitude');
        drawContour(app.ui.fieldAxes.u,X,Y,s.u,'u');
        drawContour(app.ui.fieldAxes.v,X,Y,s.v,'v');
        drawContour(app.ui.fieldAxes.pressure,X,Y,s.p,'pressure');
        drawContour(app.ui.fieldAxes.k,X,Y,s.k,'k');
        drawContour(app.ui.fieldAxes.epsilon,X,Y,s.epsilon,'epsilon');
        drawContour(app.ui.fieldAxes.omega,X,Y,s.omega,'omega');
        drawContour(app.ui.fieldAxes.mut,X,Y,s.mut,'mut');

        try
            streamslice(app.ui.streamAx, X, Y, s.u, s.v, 2);
            title(app.ui.streamAx,'Streamlines'); xlabel(app.ui.streamAx,'x'); ylabel(app.ui.streamAx,'y');
        catch
            contourf(app.ui.streamAx, X, Y, hypot(s.u,s.v), 20, 'LineStyle','none');
            colorbar(app.ui.streamAx);
        end

        post = app.report.post;
        plot(app.ui.profileAx, post.centerline.x, post.centerline.u, 'b-', 'LineWidth',1.3);
        grid(app.ui.profileAx,'on');
        title(app.ui.profileAx,'Centerline u profile');

        plot(app.ui.yplusAx, post.yPlus, 'k-'); grid(app.ui.yplusAx,'on');
        title(app.ui.yplusAx, sprintf('y+ min %.2f mean %.2f max %.2f',post.yPlusMin,post.yPlusMean,post.yPlusMax));

        plot(app.ui.tauwAx, post.tauWall, 'r-'); grid(app.ui.tauwAx,'on');
        title(app.ui.tauwAx,'Wall shear stress');

        appendStatus(sprintf('Umax=%.3g, dP=%.3g, avg Uout=%.3g',post.maxU,post.pressureDrop,post.avgOutletVelocity));
        if app.report.validation.yPlusWarning
            appendStatus('Warning: y+ outside recommended band for selected model/wall treatment.');
        end
    end

    function drawContour(ax,X,Y,F,ttl)
        contourf(ax, X, Y, F, 24, 'LineStyle','none');
        colorbar(ax); title(ax,ttl); xlabel(ax,'x'); ylabel(ax,'y'); axis(ax,'tight');
    end
end
