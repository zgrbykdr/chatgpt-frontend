classdef FMUReverseEngineeringStudioApp < matlab.apps.AppBase
    % FMU Reverse Engineering Studio main App Designer style app.

    properties (Access = public)
        UIFigure matlab.ui.Figure
        Grid matlab.ui.container.GridLayout
        LeftPanel matlab.ui.container.Panel
        RightPanel matlab.ui.container.Panel
        ImportButton matlab.ui.control.Button
        RunButton matlab.ui.control.Button
        ModeDropDown matlab.ui.control.DropDown
        LogArea matlab.ui.control.TextArea
        VarTable matlab.ui.control.Table
        ScoreTable matlab.ui.control.Table
        StatusLabel matlab.ui.control.Label
    end

    properties (Access = private)
        ProjectManager
        WorkflowManager
        Logger
    end

    methods (Access = private)
        function startup(app)
            root = fileparts(fileparts(mfilename('fullpath')));
            % Put project sources at the beginning to avoid package shadowing
            % by other similarly named folders already on the MATLAB path.
            addpath(genpath(fullfile(root,'src')),'-begin');
            app.Logger = logging.Logger(fullfile(root,'logs'));
            app.log("Log file: " + app.Logger.LogFile);
            app.ProjectManager = project.ProjectManager(root, app.Logger);
            app.WorkflowManager = appcore.WorkflowManager(app.ProjectManager, app.Logger);
            app.log("Resolved project.ProjectManager: " + string(which('project.ProjectManager')));
            app.log("Resolved fmu.FMUInspector: " + string(which('fmu.FMUInspector')));
            app.StatusLabel.Text = 'Ready';
            app.log('FMU Reverse Engineering Studio initialized.');
        end

        function log(app,msg)
            app.Logger.info(msg);
            app.LogArea.Value = [app.LogArea.Value; string(msg)];
            drawnow limitrate
        end

        function onImport(app,varargin)
            %#ok<INUSD> % varargin absorbs src/event callback args across MATLAB releases.
            [f,p] = uigetfile({'*.fmu','FMU Files (*.fmu)'}, 'Select FMU');
            if isequal(f,0), return; end
            fmuPath = fullfile(p,f);
            app.log("Import requested. FMU path: " + string(fmuPath));
            app.log("Resolved project.ProjectManager at import: " + string(which('project.ProjectManager')));
            app.log("Resolved fmu.FMUInspector at import: " + string(which('fmu.FMUInspector')));
            try
                app.ProjectManager.loadFMU(fmuPath);
            catch ME
                app.log("Primary loadFMU failed: " + string(ME.message));
                app.log("Error stack trace:");
                app.log(string(getReport(ME, 'extended', 'hyperlinks', 'off')));
                if contains(string(ME.message), "Subscripted assignment between dissimilar structures")
                    app.log("Applying GUI-level fallback FMU metadata parsing.");
                    app.applyImportFallback(fmuPath);
                else
                    rethrow(ME);
                end
            end
            tbl = app.ProjectManager.getVariableCatalogTable();
            app.VarTable.Data = tbl;
            app.StatusLabel.Text = sprintf('Loaded: %s',f);
            app.log(['FMU imported: ' fmuPath]);
        end

        function onRun(app,varargin)
            %#ok<INUSD> % varargin absorbs src/event callback args across MATLAB releases.
            mode = lower(app.ModeDropDown.Value);
            app.StatusLabel.Text = 'Running workflow...';
            app.log(['Starting workflow mode: ' mode]);
            result = app.WorkflowManager.run(mode);
            app.ScoreTable.Data = struct2table(result.Scoreboard);
            app.StatusLabel.Text = 'Workflow complete';
            app.log('Workflow completed successfully.');
        end
    end

    methods (Access = private)
        function createComponents(app)
            app.UIFigure = uifigure('Name','FMU Reverse Engineering Studio',...
                'Position',[100 100 1400 820]);
            app.Grid = uigridlayout(app.UIFigure,[2 2]);
            app.Grid.RowHeight = {42, '1x'};
            app.Grid.ColumnWidth = {260, '1x'};

            toolbar = uigridlayout(app.Grid,[1 6]);
            toolbar.Layout.Row = 1; toolbar.Layout.Column = [1 2];
            toolbar.ColumnWidth = {120,120,140,140,'1x',180};

            % NOTE: Bind callbacks through anonymous functions so the
            % AppBase method handle does not receive extra UI callback
            % arguments that can trigger "Too many input arguments".
            app.ImportButton = uibutton(toolbar,'Text','Import FMU',...
                'ButtonPushedFcn',@(src,event)app.onImport(src,event));
            app.RunButton = uibutton(toolbar,'Text','Run Workflow',...
                'ButtonPushedFcn',@(src,event)app.onRun(src,event));
            app.ModeDropDown = uidropdown(toolbar,'Items',{'automatic','semi','manual'},...
                'Value','automatic');
            app.StatusLabel = uilabel(toolbar,'Text','Ready','HorizontalAlignment','right');
            app.StatusLabel.Layout.Column = 6;

            app.LeftPanel = uipanel(app.Grid,'Title','Variables');
            app.LeftPanel.Layout.Row = 2; app.LeftPanel.Layout.Column = 1;
            app.VarTable = uitable(app.LeftPanel,'Position',[10 10 240 730]);

            app.RightPanel = uipanel(app.Grid,'Title','Campaign & Models');
            app.RightPanel.Layout.Row = 2; app.RightPanel.Layout.Column = 2;
            rg = uigridlayout(app.RightPanel,[2 1]);
            rg.RowHeight = {'1x', 240};
            app.ScoreTable = uitable(rg);
            app.LogArea = uitextarea(rg,'Editable','off');
        end

        function applyImportFallback(app, fmuPath)
            app.ProjectManager.FMUPath = string(fmuPath);
            app.ProjectManager.Metadata = localFallbackInspectFMU(string(fmuPath));
            builder = metadata.VariableCatalogBuilder(app.Logger);
            app.ProjectManager.VariableCatalog = builder.build(app.ProjectManager.Metadata);
            infer = ranges.RangeInferenceEngine(app.Logger);
            app.ProjectManager.RangeState = infer.inferInitialRanges( ...
                app.ProjectManager.VariableCatalog, app.ProjectManager.Metadata);
        end
    end

    methods (Access = public)
        function app = FMUReverseEngineeringStudioApp
            createComponents(app);
            startup(app);
        end

        function delete(app)
            if isvalid(app.UIFigure), delete(app.UIFigure); end
        end
    end
end

function meta = localFallbackInspectFMU(fmuPath)
% GUI-level import fallback for environments resolving stale inspector code.
meta = struct('path',fmuPath,'variables',[],'fmuType','Unknown','modelName','','capabilities',struct());
temp = tempname; mkdir(temp);
cleanup = onCleanup(@() rmdir(temp,'s'));
unzip(fmuPath,temp);
xmlPath = fullfile(temp,'modelDescription.xml');
if ~isfile(xmlPath), error('FMU missing modelDescription.xml'); end
d = xmlread(xmlPath);
root = d.getDocumentElement;
meta.modelName = string(root.getAttribute('modelName'));
if root.getElementsByTagName('CoSimulation').getLength > 0
    meta.fmuType = 'CoSimulation';
elseif root.getElementsByTagName('ModelExchange').getLength > 0
    meta.fmuType = 'ModelExchange';
end
tpl = struct('name',"",'valueReference',NaN,'causality',"",'variability',"", ...
    'description',"",'startValue',NaN,'minValue',NaN,'maxValue',NaN, ...
    'nominalValue',NaN,'unit',"",'dataType',"real");
nodes = root.getElementsByTagName('ScalarVariable');
records = repmat(tpl,0,1);
for i=0:nodes.getLength-1
    node = nodes.item(i); rec = tpl;
    rec.name = string(node.getAttribute('name'));
    rec.valueReference = str2double(char(node.getAttribute('valueReference')));
    rec.causality = string(node.getAttribute('causality'));
    rec.variability = string(node.getAttribute('variability'));
    rec.description = string(node.getAttribute('description'));
    kids = node.getChildNodes;
    for k=0:kids.getLength-1
        child = kids.item(k);
        if child.getNodeType~=1, continue; end
        rec.dataType = lower(string(child.getNodeName));
        if child.hasAttributes
            attrs = child.getAttributes;
            for a=0:attrs.getLength-1
                at = attrs.item(a);
                key = lower(string(at.getName)); value = char(at.getValue);
                switch key
                    case "start", rec.startValue = str2double(value);
                    case "min", rec.minValue = str2double(value);
                    case "max", rec.maxValue = str2double(value);
                    case "nominal", rec.nominalValue = str2double(value);
                    case "unit", rec.unit = string(value);
                end
            end
        end
    end
    records(end+1,1) = rec; %#ok<AGROW>
end
meta.variables = records;
clear cleanup
end
