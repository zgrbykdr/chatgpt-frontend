classdef ExperimentPlanner
    properties, Logger, end
    methods
        function obj=ExperimentPlanner(logger), obj.Logger=logger; end

        function plan = buildPlan(obj, catalog, rangeState, mode)
            inIdx = catalog.role=="input" & catalog.activeFlag=="true";
            inputs = catalog.name(inIdx);
            runs = 80;
            if mode=="manual", runs = 200; elseif mode=="semi", runs = 120; end
            X = experiments.ExcitationLibrary.lhsSamples(inputs, rangeState, runs);
            plan = struct('mode',mode,'numRuns',runs,'inputs',inputs,'matrix',X,'strategies', ...
                ["lhs","step","prbs","sineSweep","sobol"]);
            obj.Logger.info("Experiment plan built: " + runs + " runs.");
        end
    end
end
