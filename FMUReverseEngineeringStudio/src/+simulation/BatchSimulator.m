classdef BatchSimulator
    properties, Logger, end
    methods
        function obj=BatchSimulator(logger), obj.Logger=logger; end
        function raw = runBatch(obj,fmuPath,runs,catalog)
            sim = simulation.FMUSimulator(obj.Logger);
            rows = [];
            for i=1:numel(runs)
                try
                    rr = sim.runSingle(fmuPath,runs(i),catalog);
                    rows = [rows; rr]; %#ok<AGROW>
                catch ME
                    obj.Logger.warn("Run failed " + i + ": " + ME.message);
                end
            end
            raw = struct2table(rows);
        end
    end
end
