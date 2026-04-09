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
            addpath(genpath(fullfile(root,'src')));
            app.Logger = logging.Logger(fullfile(root,'logs'));
            app.ProjectManager = project.ProjectManager(root, app.Logger);
            app.WorkflowManager = appcore.WorkflowManager(app.ProjectManager, app.Logger);
            app.StatusLabel.Text = 'Ready';
            app.log('FMU Reverse Engineering Studio initialized.');
        end

        function log(app,msg)
            app.Logger.info(msg);
            app.LogArea.Value = [app.LogArea.Value; string(msg)];
            drawnow limitrate
        end

        function onImport(app,~)
            [f,p] = uigetfile({'*.fmu','FMU Files (*.fmu)'}, 'Select FMU');
            if isequal(f,0), return; end
            fmuPath = fullfile(p,f);
            app.ProjectManager.loadFMU(fmuPath);
            tbl = app.ProjectManager.getVariableCatalogTable();
            app.VarTable.Data = tbl;
            app.StatusLabel.Text = sprintf('Loaded: %s',f);
            app.log(['FMU imported: ' fmuPath]);
        end

        function onRun(app,~)
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
