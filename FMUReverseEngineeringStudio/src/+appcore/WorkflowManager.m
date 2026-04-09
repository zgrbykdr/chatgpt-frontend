classdef WorkflowManager < handle
    properties
        PM project.ProjectManager
        Logger
    end

    methods
        function obj = WorkflowManager(projectManager, logger)
            obj.PM = projectManager;
            obj.Logger = logger;
        end

        function result = run(obj, mode)
            mode = string(mode);
            planner = experiments.ExperimentPlanner(obj.Logger);
            plan = planner.buildPlan(obj.PM.VariableCatalog, obj.PM.RangeState, mode);
            camp = experiments.CampaignRunner(obj.Logger);
            sim = simulation.BatchSimulator(obj.Logger);
            runs = camp.materializeRuns(plan);
            raw = sim.runBatch(obj.PM.FMUPath, runs, obj.PM.VariableCatalog);

            prep = datahub.Preprocessor();
            ds = prep.clean(raw);
            analyzer = analysis.BehaviorAnalyzer(obj.Logger);
            diag = analyzer.analyze(ds);

            orch = appcore.ModelOrchestrator(obj.Logger);
            modelResult = orch.fitAndRank(ds, diag, mode);

            exporter = exporter.ExportManager(obj.Logger);
            exporter.exportAll(modelResult, obj.PM.RootPath + "/exports");

            result = struct('Scoreboard', modelResult.Scoreboard, 'Diagnostics', diag, 'Plan', plan);
        end
    end
end
