classdef ReportExporter
    methods (Static)
        function writeComparison(modelResult,outDir)
            t = struct2table(modelResult.Scoreboard);
            writetable(t, fullfile(outDir,'model_comparison.csv'));
        end
    end
end
