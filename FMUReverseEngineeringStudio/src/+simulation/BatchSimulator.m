classdef BatchSimulator
    properties, Logger, end
    methods
        function obj=BatchSimulator(logger), obj.Logger=logger; end
        function raw = runBatch(obj,fmuPath,runs,catalog)
            sim = simulation.FMUSimulator(obj.Logger);
            raw = table();
            for i=1:numel(runs)
                try
                    rr = sim.runSingle(fmuPath,runs(i),catalog);
                    rt = struct2table(rr,'AsArray',true);
                    raw = mergeTablesByVariableName(raw, rt);
                catch ME
                    obj.Logger.warn("Run failed " + i + ": " + ME.message);
                end
            end
        end
    end
end

function out = mergeTablesByVariableName(a,b)
if isempty(a), out = b; return; end
if isempty(b), out = a; return; end
allVars = union(a.Properties.VariableNames, b.Properties.VariableNames, 'stable');
for i = 1:numel(allVars)
    vn = allVars{i};
    if ~ismember(vn, a.Properties.VariableNames)
        a.(vn) = repmat(missing, height(a), 1);
    end
    if ~ismember(vn, b.Properties.VariableNames)
        b.(vn) = repmat(missing, height(b), 1);
    end
end
out = [a(:,allVars); b(:,allVars)];
end
