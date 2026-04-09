classdef MatlabExporter
    methods (Static)
        function exportModel(best, outDir)
            fid = fopen(fullfile(outDir,'best_model_summary.txt'),'w');
            fprintf(fid,'Best Model: %s\nFamily: %s\nScore: %.4f\n', best.Name, best.Family, best.Score);
            fclose(fid);
            save(fullfile(outDir,'best_model.mat'),'best');
        end
    end
end
