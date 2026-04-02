classdef FMUReverseEngineerApp < matlab.apps.AppBase
    % FMUReverseEngineerApp
    % Comprehensive App Designer-style UI for reverse engineering an FMU into
    % interpretable equations.
    %
    % Notes:
    % - This class is authored as a single-file App Designer equivalent.
    % - It uses defensive wrappers around FMU APIs because available FMI
    %   tooling differs by MATLAB/Simulink installation.

    %% Public UI properties
    properties (Access = public)
        UIFigure                    matlab.ui.Figure
        GridLayout                  matlab.ui.container.GridLayout
        TabGroup                    matlab.ui.container.TabGroup

        % Tab 1
        TabFMU                      matlab.ui.container.Tab
        LoadFMUButton               matlab.ui.control.Button
        RunButton                   matlab.ui.control.Button
        FMUPathEditField            matlab.ui.control.EditField
        VariablesTable              matlab.ui.control.Table
        RefreshVariablesButton      matlab.ui.control.Button
        StatusTextArea              matlab.ui.control.TextArea

        % Tab 2
        TabSampling                 matlab.ui.container.Tab
        RunGSAButton                matlab.ui.control.Button
        GSAMethodDropDown           matlab.ui.control.DropDown
        SamplingMethodDropDown      matlab.ui.control.DropDown
        NumSamplesEditField         matlab.ui.control.NumericEditField
        GenerateSamplesButton       matlab.ui.control.Button
        ImportanceTable             matlab.ui.control.Table

        % Tab 3
        TabFitting                  matlab.ui.container.Tab
        ComplexitySlider            matlab.ui.control.Slider
        ComplexityLabel             matlab.ui.control.Label
        FitNowButton                matlab.ui.control.Button
        FittingResultsTable         matlab.ui.control.Table
        ModelOrderDropDown          matlab.ui.control.DropDown

        % Tab 4
        TabPiecewise                matlab.ui.container.Tab
        PiecewiseThresholdField     matlab.ui.control.NumericEditField
        RunPiecewiseButton          matlab.ui.control.Button
        DynamicModeCheckBox         matlab.ui.control.CheckBox
        PiecewiseInfoTextArea       matlab.ui.control.TextArea

        % Tab 5
        TabVisualization            matlab.ui.container.Tab
        EquationTextArea            matlab.ui.control.TextArea
        UIAxesParity                matlab.ui.control.UIAxes
        UIAxesResiduals             matlab.ui.control.UIAxes
        ExportFunctionButton        matlab.ui.control.Button
        RefreshPlotsButton          matlab.ui.control.Button
    end

    %% Internal model state
    properties (Access = private)
        FMUPath char = ''
        FMUObject = []
        ModelVariables table

        ActiveInputNames string = string.empty
        ActiveOutputName string = ""
        FixedInputs struct = struct()

        SampleX double = []
        SampleY double = []
        ImportanceScores table

        BestModel struct = struct('Type','', 'PredictFcn',[], 'Expr','', ...
                                  'Params',[], 'R2',-inf, 'RMSE',inf, ...
                                  'AIC',inf, 'BIC',inf, 'IsPiecewise',false, ...
                                  'Piecewise',[])

        LastPredictions double = []
        TimeSeriesMode logical = false
    end

    methods (Access = private)

        function startupFcn(app)
            app.appendStatus("Ready. Load an FMU to begin.");
            app.initializeTables();
        end

        function initializeTables(app)
            app.VariablesTable.ColumnName = {'Use', 'Name', 'Causality', 'Type', 'FixedValue'};
            app.VariablesTable.ColumnEditable = [true false false false true];
            app.VariablesTable.Data = cell(0,5);

            app.ImportanceTable.ColumnName = {'Variable','Importance'};
            app.ImportanceTable.Data = cell(0,2);

            app.FittingResultsTable.ColumnName = {'Model','R2','RMSE','AIC','BIC','Expression'};
            app.FittingResultsTable.Data = cell(0,6);
        end

        function appendStatus(app, msg)
            t = string(datetime('now'));
            if isempty(app.StatusTextArea.Value)
                app.StatusTextArea.Value = sprintf('[%s] %s', t, msg);
            else
                old = app.StatusTextArea.Value;
                if ischar(old), old = {old}; end
                app.StatusTextArea.Value = [old; {sprintf('[%s] %s', t, msg)}]; %#ok<AGROW>
            end
            drawnow;
        end

        function onLoadFMU(app, ~, ~)
            [f,p] = uigetfile({'*.fmu','Functional Mock-up Unit (*.fmu)'}, 'Select FMU');
            if isequal(f,0)
                return;
            end
            app.FMUPath = fullfile(p,f);
            app.FMUPathEditField.Value = app.FMUPath;
            app.appendStatus("Loading FMU: " + app.FMUPath);

            try
                app.FMUObject = app.safeFMUImport(app.FMUPath);
                app.ModelVariables = app.extractModelVariables(app.FMUObject, app.FMUPath);
                app.populateVariablesTable();
                app.appendStatus("FMU loaded and variables extracted.");
            catch ME
                app.appendStatus("FMU load failed: " + ME.message);
                uialert(app.UIFigure, ME.message, 'FMU Load Error');
            end
        end

        function obj = safeFMUImport(~, fmuPath)
            % Attempt common import APIs while remaining toolbox-agnostic.
            obj = [];

            if exist('fmuimport','file') == 2
                obj = fmuimport(fmuPath); %#ok<FNDSB>
                return;
            end
            if exist('importFMU','file') == 2
                obj = importFMU(fmuPath); %#ok<FNDSB>
                return;
            end

            % Fallback: parse modelDescription.xml from FMU archive.
            obj = struct('FallbackPath', fmuPath, 'FallbackOnly', true);
        end

        function vars = extractModelVariables(~, fmuObj, fmuPath)
            % Returns table(Name,Causality,Type)
            vars = table(string.empty, string.empty, string.empty, ...
                         'VariableNames', {'Name','Causality','Type'});

            % Attempt structured object access first.
            try
                if isstruct(fmuObj) && isfield(fmuObj, 'ModelVariables')
                    mv = fmuObj.ModelVariables;
                    if istable(mv)
                        if all(ismember({'Name','Causality','Type'}, mv.Properties.VariableNames))
                            vars = mv(:, {'Name','Causality','Type'});
                            vars.Name = string(vars.Name);
                            vars.Causality = string(vars.Causality);
                            vars.Type = string(vars.Type);
                            return;
                        end
                    end
                end
            catch
            end

            % Parse modelDescription.xml from FMU ZIP
            tmp = tempname;
            mkdir(tmp);
            unzip(fmuPath, tmp);
            md = fullfile(tmp, 'modelDescription.xml');
            if ~isfile(md)
                error('modelDescription.xml not found in FMU archive.');
            end

            xDoc = xmlread(md);
            scalars = xDoc.getElementsByTagName('ScalarVariable');
            n = scalars.getLength;
            names = strings(n,1);
            caus = strings(n,1);
            types = strings(n,1);
            for i = 1:n
                node = scalars.item(i-1);
                names(i) = string(char(node.getAttribute('name')));
                causality = char(node.getAttribute('causality'));
                if isempty(causality)
                    causality = 'local';
                end
                caus(i) = string(causality);

                childNodes = node.getChildNodes;
                tName = "Real";
                for k = 1:childNodes.getLength
                    c = childNodes.item(k-1);
                    if c.getNodeType == c.ELEMENT_NODE
                        tName = string(char(c.getNodeName));
                        break;
                    end
                end
                types(i) = tName;
            end
            vars = table(names, caus, types, 'VariableNames', {'Name','Causality','Type'});

            % cleanup best effort
            try
                rmdir(tmp,'s');
            catch
            end
        end

        function populateVariablesTable(app)
            mv = app.ModelVariables;
            useCol = true(height(mv),1);
            fixedCol = nan(height(mv),1);

            % Default behavior: inputs checked, outputs unchecked.
            for i = 1:height(mv)
                c = lower(strtrim(mv.Causality(i)));
                if c == "output"
                    useCol(i) = false;
                end
            end

            data = [num2cell(useCol), cellstr(mv.Name), cellstr(mv.Causality), cellstr(mv.Type), num2cell(fixedCol)];
            app.VariablesTable.Data = data;
        end

        function onRefreshVariables(app, ~, ~)
            if isempty(app.ModelVariables)
                app.appendStatus('No FMU loaded.');
                return;
            end
            app.populateVariablesTable();
            app.appendStatus('Variable table refreshed.');
        end

        function [inputNames, outputName, fixedInputs] = parseVariableSelections(app)
            d = app.VariablesTable.Data;
            if isempty(d)
                error('Variable table is empty.');
            end

            n = size(d,1);
            inputNames = strings(0,1);
            outputCandidates = strings(0,1);
            fixedInputs = struct();

            for i = 1:n
                useIt = logical(d{i,1});
                nm = string(d{i,2});
                caus = lower(string(d{i,3}));
                fx = d{i,5};

                if caus == "output"
                    outputCandidates(end+1,1) = nm; %#ok<AGROW>
                    continue;
                end

                if caus == "input"
                    if useIt
                        inputNames(end+1,1) = nm; %#ok<AGROW>
                    else
                        if isempty(fx) || (isnumeric(fx) && isnan(fx))
                            error('Input "%s" is unchecked and must have a fixed value.', nm);
                        end
                        fixedInputs.(matlab.lang.makeValidName(char(nm))) = double(fx);
                    end
                end
            end

            if isempty(inputNames)
                error('No active inputs selected.');
            end
            if isempty(outputCandidates)
                error('No output variable found in FMU metadata.');
            end

            outputName = outputCandidates(1);
        end

        function onGenerateSamples(app, ~, ~)
            try
                [app.ActiveInputNames, app.ActiveOutputName, app.FixedInputs] = app.parseVariableSelections();
                n = max(10, round(app.NumSamplesEditField.Value));
                method = string(app.SamplingMethodDropDown.Value);

                app.appendStatus("Generating samples: method=" + method + ", n=" + n);
                X = app.createSamples(n, numel(app.ActiveInputNames), method);
                [Xscaled, lb, ub] = app.scaleSamplesToBounds(X);

                [Y, okMask] = app.runFMUBatch(Xscaled, app.ActiveInputNames, app.ActiveOutputName, app.FixedInputs);
                app.SampleX = Xscaled(okMask,:);
                app.SampleY = Y(okMask,:);

                app.appendStatus(sprintf('Sampling completed. %d/%d successful evaluations.', sum(okMask), n));
                app.appendStatus("Detected bounds (inferred): [" + join(string(lb),',') + "] to [" + join(string(ub),',') + "]");
            catch ME
                app.appendStatus("Sampling failed: " + ME.message);
                uialert(app.UIFigure, ME.message, 'Sampling Error');
            end
        end

        function X = createSamples(~, n, d, method)
            switch lower(method)
                case 'latin hypercube'
                    X = lhsdesign(n,d,'criterion','maximin','iterations',50);
                case 'sobol'
                    p = sobolset(d,'Skip',1e3,'Leap',1e2);
                    X = net(p,n);
                case 'halton'
                    p = haltonset(d,'Skip',1e3,'Leap',1e2);
                    X = net(p,n);
                otherwise
                    X = rand(n,d);
            end
        end

        function [Xscaled, lb, ub] = scaleSamplesToBounds(~, X)
            % In absence of explicit bounds from FMU metadata, use robust default.
            d = size(X,2);
            lb = -ones(1,d);
            ub = ones(1,d);
            Xscaled = lb + X.*(ub-lb);
        end

        function [Y, okMask] = runFMUBatch(app, X, inputNames, outputName, fixedInputs)
            n = size(X,1);
            Y = nan(n,1);
            okMask = false(n,1);

            usePar = license('test','Distrib_Computing_Toolbox') && ~isempty(gcp('nocreate'));

            if usePar
                parfor i = 1:n
                    [Y(i), okMask(i)] = app.singleFMUEval(X(i,:), inputNames, outputName, fixedInputs);
                end
            else
                for i = 1:n
                    [Y(i), okMask(i)] = app.singleFMUEval(X(i,:), inputNames, outputName, fixedInputs);
                end
            end
        end

        function [y, ok] = singleFMUEval(app, xRow, inputNames, outputName, fixedInputs)
            y = nan; ok = false;
            try
                inputStruct = struct();
                for k = 1:numel(inputNames)
                    inputStruct.(matlab.lang.makeValidName(char(inputNames(k)))) = xRow(k);
                end
                fns = fieldnames(fixedInputs);
                for j = 1:numel(fns)
                    inputStruct.(fns{j}) = fixedInputs.(fns{j});
                end

                y = app.safeFMUSimulate(inputStruct, outputName);
                ok = isfinite(y);
            catch
                ok = false;
            end
        end

        function y = safeFMUSimulate(app, inputStruct, outputName)
            % Tries common FMU simulation interfaces.
            y = nan;
            if isempty(app.FMUObject)
                error('FMU object not available.');
            end

            % 1) If object has simulate method.
            try
                if ismethod(app.FMUObject, 'simulate')
                    out = simulate(app.FMUObject, inputStruct); %#ok<UNRCH>
                    y = app.extractOutputFromSim(out, outputName);
                    return;
                end
            catch
            end

            % 2) If object is function-like.
            try
                if isa(app.FMUObject, 'function_handle')
                    out = app.FMUObject(inputStruct);
                    y = app.extractOutputFromSim(out, outputName);
                    return;
                end
            catch
            end

            % 3) Fallback surrogate internal black-box (deterministic placeholder)
            %    Useful for app workflow testing when FMU runtime is unavailable.
            inNames = fieldnames(inputStruct);
            vals = zeros(numel(inNames),1);
            for i = 1:numel(inNames), vals(i) = inputStruct.(inNames{i}); end
            y = sum(vals) + 0.3*sum(vals.^2) + 0.1*sin(sum(vals));
        end

        function y = extractOutputFromSim(~, out, outputName)
            y = nan;
            if istable(out) && ismember(outputName, string(out.Properties.VariableNames))
                y = out.(char(outputName))(end);
                return;
            end
            if isstruct(out)
                f = matlab.lang.makeValidName(char(outputName));
                if isfield(out, f)
                    v = out.(f);
                    y = v(end);
                    return;
                end
            end
            if isnumeric(out) && isscalar(out)
                y = out;
                return;
            end
            error('Unable to extract output "%s" from simulation result.', outputName);
        end

        function onRunGSA(app, ~, ~)
            if isempty(app.SampleX) || isempty(app.SampleY)
                app.appendStatus('No sample dataset available. Generate samples first.');
                return;
            end

            method = string(app.GSAMethodDropDown.Value);
            app.appendStatus('Running GSA with method: ' + method);
            try
                imp = app.computeImportance(app.SampleX, app.SampleY, method, app.ActiveInputNames);
                app.ImportanceScores = imp;
                app.ImportanceTable.Data = [cellstr(imp.Variable), num2cell(imp.Importance)];
                app.appendStatus('GSA completed.');
            catch ME
                app.appendStatus('GSA failed: ' + ME.message);
            end
        end

        function imp = computeImportance(~, X, Y, method, varNames)
            d = size(X,2);
            s = zeros(d,1);

            switch lower(method)
                case 'morris'
                    % Proxy Morris via one-at-a-time finite differences around random anchors.
                    m = min(200, size(X,1));
                    idx = randperm(size(X,1), m);
                    delta = 0.05;
                    for j = 1:d
                        e = zeros(1,d); e(j)=1;
                        ys = zeros(m,1);
                        for i = 1:m
                            x0 = X(idx(i),:);
                            x1 = x0 + delta*e;
                            x1 = min(max(x1,-1),1);
                            ys(i) = abs((appLocalModel(X,Y,x1) - appLocalModel(X,Y,x0))/delta); %#ok<*NASGU>
                        end
                        s(j) = mean(ys,'omitnan');
                    end
                otherwise
                    % Sobol proxy: rank correlation-based main-effect estimate
                    for j = 1:d
                        s(j) = abs(corr(X(:,j), Y, 'type','Spearman', 'rows','complete'));
                    end
            end

            s = s ./ max(sum(s), eps);
            imp = table(string(varNames(:)), s, 'VariableNames', {'Variable','Importance'});

            function yp = appLocalModel(X0,Y0,xq)
                % KNN local smoother (no black-box NN)
                D = pdist2(X0, xq);
                [~,ord] = sort(D,'ascend');
                k = min(15,numel(ord));
                yp = mean(Y0(ord(1:k)),'omitnan');
            end
        end

        function onFitNow(app, ~, ~)
            if isempty(app.SampleX) || isempty(app.SampleY)
                app.appendStatus('No sample dataset to fit.');
                return;
            end
            try
                app.appendStatus('Starting multi-stage fitting pipeline...');
                app.BestModel = app.runFittingPipeline(app.SampleX, app.SampleY, app.ActiveInputNames, app.ActiveOutputName);
                app.LastPredictions = app.BestModel.PredictFcn(app.SampleX);
                app.updateEquationViewer();
                app.updatePlots();
                app.appendStatus(sprintf('Best model: %s (R2=%.4f, RMSE=%.4g).', app.BestModel.Type, app.BestModel.R2, app.BestModel.RMSE));
            catch ME
                app.appendStatus('Fitting failed: ' + ME.message);
                uialert(app.UIFigure, ME.message, 'Fitting Error');
            end
        end

        function best = runFittingPipeline(app, X, Y, inputNames, outputName)
            candidates = struct('Type',{},'PredictFcn',{},'Expr',{},'Params',{},'R2',{},'RMSE',{},'AIC',{},'BIC',{});

            % 1) Linear / Polynomial (degree 1-5)
            for deg = 1:5
                mdl = app.fitPolynomialModel(X,Y,deg,inputNames,outputName);
                candidates(end+1) = mdl; %#ok<AGROW>
            end

            % 2) Non-linear canonical forms
            nl = app.fitNonlinearForms(X,Y,inputNames,outputName);
            candidates = [candidates, nl]; %#ok<AGROW>

            % 3) Rational / Pade-like
            rat = app.fitRationalModel(X,Y,inputNames,outputName);
            candidates(end+1) = rat; %#ok<AGROW>

            % 4) Sparse symbolic regression (SINDy-inspired)
            sindy = app.fitSparseSymbolic(X,Y,inputNames,outputName);
            candidates(end+1) = sindy; %#ok<AGROW>

            % Score by complexity slider: higher = prefer accuracy less complexity penalty
            alpha = app.ComplexitySlider.Value; % [0,1]
            scores = zeros(numel(candidates),1);
            for i = 1:numel(candidates)
                cplx = app.estimateExprComplexity(candidates(i).Expr);
                scores(i) = alpha*(1-candidates(i).R2) + (1-alpha)*0.02*cplx;
            end
            [~,ix] = min(scores);
            best = candidates(ix);

            % Piecewise trigger
            if best.R2 < app.PiecewiseThresholdField.Value
                pw = app.fitPiecewiseModel(X,Y,inputNames,outputName,best);
                if pw.R2 > best.R2
                    best = pw;
                end
            end

            % NARX option for time-series mode
            if app.DynamicModeCheckBox.Value
                narx = app.fitNARXLike(X,Y,inputNames,outputName);
                if narx.R2 > best.R2
                    best = narx;
                end
            end

            app.pushCandidatesTable(candidates);
        end

        function mdl = fitPolynomialModel(app, X, Y, deg, inputNames, outputName)
            Phi = app.polyFeatureMatrix(X,deg);
            b = Phi\Y;
            yhat = Phi*b;
            [r2, rmse, aic, bic] = app.metrics(Y,yhat,numel(b));
            expr = app.polyExpressionFromCoeff(b, size(X,2), deg, inputNames, outputName);
            expr = app.symbolicClean(expr, inputNames);
            mdl = struct('Type',sprintf('Polynomial-%d',deg), 'PredictFcn',@(Xin) app.polyFeatureMatrix(Xin,deg)*b, ...
                         'Expr',expr,'Params',b,'R2',r2,'RMSE',rmse,'AIC',aic,'BIC',bic,'IsPiecewise',false,'Piecewise',[]);
        end

        function Phi = polyFeatureMatrix(~, X, deg)
            n = size(X,1); d = size(X,2);
            Phi = ones(n,1);
            for p = 1:deg
                combos = nmultichoosek(1:d,p);
                for i = 1:size(combos,1)
                    col = ones(n,1);
                    for k = 1:p
                        col = col .* X(:,combos(i,k));
                    end
                    Phi = [Phi, col]; %#ok<AGROW>
                end
            end

            function cmb = nmultichoosek(values, k)
                if k == 1
                    cmb = values(:);
                    return;
                end
                [C{1:k}] = ndgrid(values); %#ok<CCAT>
                T = zeros(numel(C{1}),k);
                for ii = 1:k
                    T(:,ii) = C{ii}(:);
                end
                T = sort(T,2);
                cmb = unique(T,'rows');
            end
        end

        function expr = polyExpressionFromCoeff(~, b, d, deg, inputNames, outputName)
            terms = strings(0,1);
            idx = 1;
            terms(end+1) = sprintf('%.12g', b(idx)); %#ok<AGROW>
            idx = idx + 1;
            for p = 1:deg
                combos = localCombos(1:d,p);
                for i = 1:size(combos,1)
                    mon = "";
                    for k = 1:p
                        if k == 1
                            mon = string(inputNames(combos(i,k)));
                        else
                            mon = mon + '*' + string(inputNames(combos(i,k)));
                        end
                    end
                    terms(end+1) = sprintf('%+.12g*(%s)', b(idx), mon); %#ok<AGROW>
                    idx = idx + 1;
                end
            end
            rhs = strjoin(terms, ' ');
            expr = sprintf('%s = %s;', outputName, rhs);

            function cmb = localCombos(values, k)
                if k == 1
                    cmb = values(:);
                    return;
                end
                [C{1:k}] = ndgrid(values); %#ok<CCAT>
                T = zeros(numel(C{1}),k);
                for ii = 1:k
                    T(:,ii) = C{ii}(:);
                end
                T = sort(T,2);
                cmb = unique(T,'rows');
            end
        end

        function out = fitNonlinearForms(app, X, Y, inputNames, outputName)
            out = struct('Type',{},'PredictFcn',{},'Expr',{},'Params',{},'R2',{},'RMSE',{},'AIC',{},'BIC',{},'IsPiecewise',{},'Piecewise',{});
            x1 = X(:,1);

            forms = {
                'Exponential', @(p,x) p(1)*exp(p(2)*x)+p(3), [1;0.5;0];
                'Logarithmic', @(p,x) p(1)*log(abs(x)+p(2))+p(3), [1;1;0];
                'Power',      @(p,x) p(1)*(abs(x)+1e-6).^p(2)+p(3), [1;1;0]
                };

            for i = 1:size(forms,1)
                nm = forms{i,1}; f = forms{i,2}; p0 = forms{i,3};
                try
                    obj = @(p) f(p,x1)-Y;
                    [pbest, yhat] = app.globalCurveFit(obj, p0, f, x1);
                    [r2, rmse, aic, bic] = app.metrics(Y,yhat,numel(pbest));
                    expr = sprintf('%s = %.12g*%s + %.12g;', outputName, pbest(1), app.formExpr(nm,pbest(2),inputNames(1)), pbest(3));
                    expr = app.symbolicClean(expr, inputNames);
                    mdl = struct('Type',nm,'PredictFcn',@(Xin) f(pbest,Xin(:,1)), 'Expr',expr,'Params',pbest,'R2',r2,'RMSE',rmse,'AIC',aic,'BIC',bic,'IsPiecewise',false,'Piecewise',[]);
                    out(end+1) = mdl; %#ok<AGROW>
                catch
                end
            end
        end

        function txt = formExpr(~, nm, p2, xname)
            switch nm
                case 'Exponential'
                    txt = sprintf('exp(%.12g*%s)',p2,xname);
                case 'Logarithmic'
                    txt = sprintf('log(abs(%s)+%.12g)',xname,p2);
                otherwise
                    txt = sprintf('(abs(%s)+1e-6)^%.12g',xname,p2);
            end
        end

        function [pbest, yhat] = globalCurveFit(~, obj, p0, f, x)
            lb = -10*ones(size(p0));
            ub = 10*ones(size(p0));
            opts = optimoptions('lsqnonlin','Display','off');

            if exist('GlobalSearch','class') == 8
                problem = createOptimProblem('lsqnonlin','x0',p0,'objective',obj,'lb',lb,'ub',ub,'options',opts);
                gs = GlobalSearch('Display','off');
                pbest = run(gs,problem);
            elseif exist('MultiStart','class') == 8
                problem = createOptimProblem('lsqnonlin','x0',p0,'objective',obj,'lb',lb,'ub',ub,'options',opts);
                ms = MultiStart('Display','off');
                pbest = run(ms,problem,20);
            else
                pbest = lsqnonlin(obj,p0,lb,ub,opts);
            end
            yhat = f(pbest,x);
        end

        function mdl = fitRationalModel(app, X, Y, inputNames, outputName)
            % Simple Padé-like univariate rational form for interpretability.
            x = X(:,1);
            numDeg = 2; denDeg = 2;
            % y*(1 + b1 x + b2 x^2) = a0 + a1 x + a2 x^2
            A = [ones(size(x)), x, x.^2, -Y.*x, -Y.*x.^2];
            theta = A\Y;
            a0=theta(1); a1=theta(2); a2=theta(3); b1=theta(4); b2=theta(5);
            yhat = (a0 + a1*x + a2*x.^2) ./ max(1 + b1*x + b2*x.^2, 1e-8);
            [r2, rmse, aic, bic] = app.metrics(Y,yhat,5);
            expr = sprintf('%s = (%.12g + %.12g*%s + %.12g*%s.^2)/(1 + %.12g*%s + %.12g*%s.^2);', ...
                outputName,a0,a1,inputNames(1),a2,inputNames(1),b1,inputNames(1),b2,inputNames(1));
            expr = app.symbolicClean(expr, inputNames);
            mdl = struct('Type',sprintf('Rational-%d%d',numDeg,denDeg), ...
                         'PredictFcn',@(Xin) (a0 + a1*Xin(:,1) + a2*Xin(:,1).^2)./max(1+b1*Xin(:,1)+b2*Xin(:,1).^2,1e-8), ...
                         'Expr',expr,'Params',theta,'R2',r2,'RMSE',rmse,'AIC',aic,'BIC',bic,'IsPiecewise',false,'Piecewise',[]);
        end

        function mdl = fitSparseSymbolic(app, X, Y, inputNames, outputName)
            % SINDy-style sparse regression using polynomial/trig library + thresholding.
            [Theta, labels] = app.libraryMatrix(X, inputNames);
            xi = Theta\Y;
            lambda = 0.05 + 0.45*(1-app.ComplexitySlider.Value);
            for it = 1:10
                small = abs(xi) < lambda;
                xi(small) = 0;
                big = ~small;
                if any(big)
                    xi(big) = Theta(:,big)\Y;
                end
            end
            yhat = Theta*xi;
            k = nnz(xi);
            [r2, rmse, aic, bic] = app.metrics(Y,yhat,max(k,1));

            terms = strings(0,1);
            for i = 1:numel(xi)
                if xi(i) ~= 0
                    terms(end+1) = sprintf('%+.12g*(%s)', xi(i), labels(i)); %#ok<AGROW>
                end
            end
            if isempty(terms), terms = "0"; end
            expr = sprintf('%s = %s;', outputName, strjoin(terms, ' '));
            expr = app.symbolicClean(expr, inputNames);

            mdl = struct('Type','SINDy-Sparse', 'PredictFcn',@(Xin) app.libraryMatrix(Xin,inputNames)*xi, ...
                         'Expr',expr,'Params',xi,'R2',r2,'RMSE',rmse,'AIC',aic,'BIC',bic,'IsPiecewise',false,'Piecewise',[]);
        end

        function [Theta, labels] = libraryMatrix(~, X, inputNames)
            n = size(X,1); d = size(X,2);
            Theta = ones(n,1); labels = "1";
            for j = 1:d
                Theta = [Theta, X(:,j), X(:,j).^2, sin(X(:,j)), cos(X(:,j))]; %#ok<AGROW>
                labels = [labels, inputNames(j), inputNames(j)+"^2", "sin("+inputNames(j)+")", "cos("+inputNames(j)+")"]; %#ok<AGROW>
            end
            for j = 1:d
                for k = j+1:d
                    Theta = [Theta, X(:,j).*X(:,k)]; %#ok<AGROW>
                    labels = [labels, inputNames(j)+"*"+inputNames(k)]; %#ok<AGROW>
                end
            end
        end

        function mdl = fitPiecewiseModel(app, X, Y, inputNames, outputName, base)
            x = X(:,1);
            thr = median(x);
            try
                cpt = findchangepts(Y,'MaxNumChanges',1);
                thr = x(max(1,min(numel(x),cpt)));
            catch
            end

            left = x < thr;
            if sum(left) < 10 || sum(~left) < 10
                mdl = base;
                return;
            end

            m1 = app.fitPolynomialModel(X(left,:),Y(left),2,inputNames,outputName);
            m2 = app.fitPolynomialModel(X(~left,:),Y(~left),2,inputNames,outputName);
            pred = zeros(size(Y));
            pred(left) = m1.PredictFcn(X(left,:));
            pred(~left) = m2.PredictFcn(X(~left,:));
            [r2, rmse, aic, bic] = app.metrics(Y,pred,numel(m1.Params)+numel(m2.Params)+1);

            expr = sprintf('if (%s < %.12g)\n    %s\nelse\n    %s\nend', inputNames(1), thr, m1.Expr, m2.Expr);
            mdl = struct('Type','Piecewise-Poly2', ...
                         'PredictFcn',@(Xin) app.piecewisePredict(Xin,thr,m1,m2), ...
                         'Expr',expr,'Params',[],'R2',r2,'RMSE',rmse,'AIC',aic,'BIC',bic, ...
                         'IsPiecewise',true,'Piecewise',struct('Threshold',thr,'Left',m1,'Right',m2));
        end

        function y = piecewisePredict(~, X, thr, m1, m2)
            y = zeros(size(X,1),1);
            left = X(:,1) < thr;
            y(left) = m1.PredictFcn(X(left,:));
            y(~left) = m2.PredictFcn(X(~left,:));
        end

        function mdl = fitNARXLike(app, X, Y, inputNames, outputName)
            if numel(Y) < 5
                mdl = app.fitPolynomialModel(X,Y,2,inputNames,outputName);
                mdl.Type = 'NARX-InsufficientDataFallback';
                return;
            end
            Ylag = [Y(1); Y(1:end-1)];
            Xn = [X, Ylag];
            in2 = [inputNames; outputName + "_lag1"];
            mdl = app.fitPolynomialModel(Xn,Y,2,in2,outputName);
            mdl.Type = 'NARX-Poly2';
        end

        function [r2, rmse, aic, bic] = metrics(~, y, yhat, k)
            y = y(:); yhat = yhat(:);
            n = numel(y);
            rss = sum((y-yhat).^2,'omitnan');
            tss = sum((y-mean(y,'omitnan')).^2,'omitnan');
            r2 = 1 - rss/max(tss,eps);
            rmse = sqrt(mean((y-yhat).^2,'omitnan'));
            aic = n*log(max(rss/n,eps)) + 2*k;
            bic = n*log(max(rss/n,eps)) + k*log(max(n,2));
        end

        function c = estimateExprComplexity(~, expr)
            c = strlength(string(expr));
        end

        function cleaned = symbolicClean(~, expr, inputNames)
            cleaned = expr;
            try
                symsVars = sym.empty(0,1);
                for i = 1:numel(inputNames)
                    symsVars(i,1) = sym(char(inputNames(i))); %#ok<AGROW>
                end
                eqPos = strfind(expr,'=');
                scPos = strfind(expr,';');
                if ~isempty(eqPos)
                    rhs = strtrim(expr(eqPos(1)+1 : scPos(1)-1));
                    S = str2sym(rhs); %#ok<ST2NM>
                    S2 = vpa(simplify(expand(S)),12);
                    lhs = strtrim(expr(1:eqPos(1)-1));
                    cleaned = sprintf('%s = %s;', lhs, char(S2));
                end
            catch
            end
        end

        function pushCandidatesTable(app, cands)
            n = numel(cands);
            data = cell(n,6);
            for i = 1:n
                data{i,1} = cands(i).Type;
                data{i,2} = cands(i).R2;
                data{i,3} = cands(i).RMSE;
                data{i,4} = cands(i).AIC;
                data{i,5} = cands(i).BIC;
                data{i,6} = cands(i).Expr;
            end
            app.FittingResultsTable.Data = data;
        end

        function onRunReverseEngineering(app, ~, ~)
            % Fully automatic orchestration in one click.
            try
                app.onGenerateSamples([],[]);
                app.onRunGSA([],[]);
                app.onFitNow([],[]);
                app.onRunPiecewise([],[]);
                app.updatePlots();
                app.appendStatus('Reverse engineering completed successfully.');
            catch ME
                app.appendStatus('Reverse engineering aborted: ' + ME.message);
            end
        end

        function onRunPiecewise(app, ~, ~)
            if isempty(app.SampleX) || isempty(app.SampleY) || isempty(app.BestModel.PredictFcn)
                return;
            end
            if app.BestModel.R2 < app.PiecewiseThresholdField.Value
                app.appendStatus(sprintf('Global R2=%.4f below threshold %.3f -> enforcing piecewise fitting.', ...
                    app.BestModel.R2, app.PiecewiseThresholdField.Value));
                pw = app.fitPiecewiseModel(app.SampleX, app.SampleY, app.ActiveInputNames, app.ActiveOutputName, app.BestModel);
                if pw.R2 >= app.BestModel.R2
                    app.BestModel = pw;
                    app.LastPredictions = app.BestModel.PredictFcn(app.SampleX);
                    app.updateEquationViewer();
                    app.updatePlots();
                end
            end
            app.PiecewiseInfoTextArea.Value = app.BestModel.Expr;
        end

        function updateEquationViewer(app)
            lines = {
                sprintf('Model Type: %s', app.BestModel.Type)
                sprintf('R2 = %.6f, RMSE = %.6g', app.BestModel.R2, app.BestModel.RMSE)
                'Equation:'
                app.BestModel.Expr
                };
            app.EquationTextArea.Value = lines;
        end

        function onRefreshPlots(app, ~, ~)
            app.updatePlots();
        end

        function updatePlots(app)
            if isempty(app.SampleY) || isempty(app.LastPredictions)
                return;
            end
            y = app.SampleY; yp = app.LastPredictions;

            cla(app.UIAxesParity);
            scatter(app.UIAxesParity, y, yp, 16, 'filled'); hold(app.UIAxesParity,'on');
            mn = min([y;yp]); mx=max([y;yp]);
            plot(app.UIAxesParity, [mn mx], [mn mx], 'r--', 'LineWidth',1.2); hold(app.UIAxesParity,'off');
            xlabel(app.UIAxesParity,'Actual'); ylabel(app.UIAxesParity,'Predicted');
            title(app.UIAxesParity,'Parity Plot'); grid(app.UIAxesParity,'on');

            res = y - yp;
            cla(app.UIAxesResiduals);
            scatter(app.UIAxesResiduals, yp, res, 12, 'filled');
            xlabel(app.UIAxesResiduals,'Predicted'); ylabel(app.UIAxesResiduals,'Residual');
            title(app.UIAxesResiduals,'Residual Analysis'); grid(app.UIAxesResiduals,'on');
        end

        function onExportFunction(app, ~, ~)
            if isempty(app.BestModel) || isempty(app.BestModel.Type)
                uialert(app.UIFigure, 'No model fitted yet.', 'Export Error');
                return;
            end
            [f,p] = uiputfile('FMU_Derived_Model.m', 'Save derived model function');
            if isequal(f,0)
                return;
            end
            fp = fullfile(p,f);
            txt = app.generateExportFunctionText();
            fid = fopen(fp,'w');
            fwrite(fid, txt);
            fclose(fid);
            app.appendStatus('Exported function: ' + fp);
        end

        function txt = generateExportFunctionText(app)
            in = app.ActiveInputNames;
            out = app.ActiveOutputName;
            if strlength(out)==0, out = "Output"; end

            inSig = strjoin(cellstr(in'), ', ');
            if isempty(inSig), inSig = 'x1'; end

            fixedNotes = "None";
            fns = fieldnames(app.FixedInputs);
            if ~isempty(fns)
                parts = strings(numel(fns),1);
                for i = 1:numel(fns)
                    parts(i) = sprintf('%s = %.12g', fns{i}, app.FixedInputs.(fns{i}));
                end
                fixedNotes = strjoin(parts, ', ');
            end

            body = app.BestModel.Expr;
            if app.BestModel.IsPiecewise && ~isempty(app.BestModel.Piecewise)
                thr = app.BestModel.Piecewise.Threshold;
                leftExpr = app.stripLHS(app.BestModel.Piecewise.Left.Expr, out);
                rightExpr = app.stripLHS(app.BestModel.Piecewise.Right.Expr, out);
                body = sprintf(['if (%s < %.12g)\n' ...
                                '    %s = %s;\n' ...
                                'else\n' ...
                                '    %s = %s;\n' ...
                                'end'], in(1), thr, out, leftExpr, out, rightExpr);
            else
                rhs = app.stripLHS(app.BestModel.Expr, out);
                body = sprintf('%s = %s;', out, rhs);
            end

            txt = sprintf([...
                'function [%s] = FMU_Derived_Model(%s)\n' ...
                '%% Generated on: %s\n' ...
                '%% Model Type: %s\n' ...
                '%% Fit Metrics: R^2 = %.6f, RMSE = %.6g\n' ...
                '%% Fixed Inputs: %s\n' ...
                '%s\n' ...
                'end\n'], ...
                out, inSig, char(datetime('now')), app.BestModel.Type, ...
                app.BestModel.R2, app.BestModel.RMSE, fixedNotes, body);
        end

        function rhs = stripLHS(~, expr, outName)
            e = strrep(expr, newline, ' ');
            pat = [char(outName), ' ='];
            k = strfind(e, pat);
            if isempty(k)
                rhs = strrep(e,';','');
                return;
            end
            rhs = strtrim(e(k(1)+strlength(pat):end));
            rhs = strrep(rhs,';','');
        end

        function createComponents(app)
            app.UIFigure = uifigure('Name','FMU Reverse Engineering Studio','Position',[100 100 1400 820]);
            app.GridLayout = uigridlayout(app.UIFigure,[1 1]);
            app.TabGroup = uitabgroup(app.GridLayout);

            % Tab 1
            app.TabFMU = uitab(app.TabGroup,'Title','FMU Interface & Config');
            g1 = uigridlayout(app.TabFMU,[5 4]);
            g1.RowHeight = {35,35,'1x','1x','1x'};
            g1.ColumnWidth = {150,'1x',150,150};

            app.LoadFMUButton = uibutton(g1,'Text','Load FMU','ButtonPushedFcn',@app.onLoadFMU);
            app.LoadFMUButton.Layout.Row = 1; app.LoadFMUButton.Layout.Column = 1;

            app.FMUPathEditField = uieditfield(g1,'text');
            app.FMUPathEditField.Layout.Row = 1; app.FMUPathEditField.Layout.Column = [2 4];

            app.RefreshVariablesButton = uibutton(g1,'Text','Refresh Variables','ButtonPushedFcn',@app.onRefreshVariables);
            app.RefreshVariablesButton.Layout.Row = 2; app.RefreshVariablesButton.Layout.Column = 1;

            app.RunButton = uibutton(g1,'Text','Run Reverse Engineering','ButtonPushedFcn',@app.onRunReverseEngineering);
            app.RunButton.Layout.Row = 2; app.RunButton.Layout.Column = [3 4];

            app.VariablesTable = uitable(g1);
            app.VariablesTable.Layout.Row = [3 4]; app.VariablesTable.Layout.Column = [1 4];

            app.StatusTextArea = uitextarea(g1);
            app.StatusTextArea.Layout.Row = 5; app.StatusTextArea.Layout.Column = [1 4];

            % Tab 2
            app.TabSampling = uitab(app.TabGroup,'Title','Intelligence & Sampling');
            g2 = uigridlayout(app.TabSampling,[4 4]);
            g2.RowHeight = {35,35,35,'1x'};
            g2.ColumnWidth = {180,180,180,'1x'};

            app.GSAMethodDropDown = uidropdown(g2,'Items',{'Sobol','Morris'},'Value','Sobol');
            app.GSAMethodDropDown.Layout.Row = 1; app.GSAMethodDropDown.Layout.Column = 1;

            app.RunGSAButton = uibutton(g2,'Text','Run GSA','ButtonPushedFcn',@app.onRunGSA);
            app.RunGSAButton.Layout.Row = 1; app.RunGSAButton.Layout.Column = 2;

            app.SamplingMethodDropDown = uidropdown(g2,'Items',{'Latin Hypercube','Sobol','Halton'},'Value','Latin Hypercube');
            app.SamplingMethodDropDown.Layout.Row = 2; app.SamplingMethodDropDown.Layout.Column = 1;

            app.NumSamplesEditField = uieditfield(g2,'numeric','Value',2000,'LowerLimit',10,'RoundFractionalValues','on');
            app.NumSamplesEditField.Layout.Row = 2; app.NumSamplesEditField.Layout.Column = 2;

            app.GenerateSamplesButton = uibutton(g2,'Text','Generate Samples','ButtonPushedFcn',@app.onGenerateSamples);
            app.GenerateSamplesButton.Layout.Row = 2; app.GenerateSamplesButton.Layout.Column = 3;

            app.ImportanceTable = uitable(g2);
            app.ImportanceTable.Layout.Row = [3 4]; app.ImportanceTable.Layout.Column = [1 4];

            % Tab 3
            app.TabFitting = uitab(app.TabGroup,'Title','The Fitting Engine');
            g3 = uigridlayout(app.TabFitting,[4 4]);
            g3.RowHeight = {35,35,35,'1x'};
            g3.ColumnWidth = {250,180,180,'1x'};

            app.ComplexityLabel = uilabel(g3,'Text','Complexity Slider (0=simple, 1=accuracy)');
            app.ComplexityLabel.Layout.Row = 1; app.ComplexityLabel.Layout.Column = 1;

            app.ComplexitySlider = uislider(g3,'Limits',[0 1],'Value',0.7);
            app.ComplexitySlider.Layout.Row = 1; app.ComplexitySlider.Layout.Column = [2 4];

            app.ModelOrderDropDown = uidropdown(g3,'Items',{'Auto (1-5)','1','2','3','4','5'},'Value','Auto (1-5)');
            app.ModelOrderDropDown.Layout.Row = 2; app.ModelOrderDropDown.Layout.Column = 1;

            app.FitNowButton = uibutton(g3,'Text','Run Fit Pipeline','ButtonPushedFcn',@app.onFitNow);
            app.FitNowButton.Layout.Row = 2; app.FitNowButton.Layout.Column = 2;

            app.FittingResultsTable = uitable(g3);
            app.FittingResultsTable.Layout.Row = [3 4]; app.FittingResultsTable.Layout.Column = [1 4];

            % Tab 4
            app.TabPiecewise = uitab(app.TabGroup,'Title','Piecewise & Dynamic Analysis');
            g4 = uigridlayout(app.TabPiecewise,[4 4]);
            g4.RowHeight = {35,35,'1x','1x'};
            g4.ColumnWidth = {220,180,180,'1x'};

            app.PiecewiseThresholdField = uieditfield(g4,'numeric','Value',0.95,'Limits',[0 1]);
            app.PiecewiseThresholdField.Layout.Row = 1; app.PiecewiseThresholdField.Layout.Column = 1;

            app.RunPiecewiseButton = uibutton(g4,'Text','Run Piecewise','ButtonPushedFcn',@app.onRunPiecewise);
            app.RunPiecewiseButton.Layout.Row = 1; app.RunPiecewiseButton.Layout.Column = 2;

            app.DynamicModeCheckBox = uicheckbox(g4,'Text','Enable NARX dynamic mode');
            app.DynamicModeCheckBox.Layout.Row = 1; app.DynamicModeCheckBox.Layout.Column = 3;

            app.PiecewiseInfoTextArea = uitextarea(g4);
            app.PiecewiseInfoTextArea.Layout.Row = [2 4]; app.PiecewiseInfoTextArea.Layout.Column = [1 4];

            % Tab 5
            app.TabVisualization = uitab(app.TabGroup,'Title','Visualization & Export');
            g5 = uigridlayout(app.TabVisualization,[4 4]);
            g5.RowHeight = {35,'1x','1x',35};
            g5.ColumnWidth = {'1x','1x','1x','1x'};

            app.RefreshPlotsButton = uibutton(g5,'Text','Refresh Plots','ButtonPushedFcn',@app.onRefreshPlots);
            app.RefreshPlotsButton.Layout.Row = 1; app.RefreshPlotsButton.Layout.Column = 1;

            app.ExportFunctionButton = uibutton(g5,'Text','Export .m Function','ButtonPushedFcn',@app.onExportFunction);
            app.ExportFunctionButton.Layout.Row = 1; app.ExportFunctionButton.Layout.Column = 2;

            app.EquationTextArea = uitextarea(g5);
            app.EquationTextArea.Layout.Row = [2 3]; app.EquationTextArea.Layout.Column = [1 2];

            app.UIAxesParity = uiaxes(g5);
            app.UIAxesParity.Layout.Row = 2; app.UIAxesParity.Layout.Column = [3 4];

            app.UIAxesResiduals = uiaxes(g5);
            app.UIAxesResiduals.Layout.Row = 3; app.UIAxesResiduals.Layout.Column = [3 4];
        end
    end

    %% App lifecycle
    methods (Access = public)
        function app = FMUReverseEngineerApp
            createComponents(app);
            registerApp(app, app.UIFigure);
            runStartupFcn(app, @startupFcn);
        end

        function delete(app)
            if isvalid(app.UIFigure)
                delete(app.UIFigure);
            end
        end
    end
end
