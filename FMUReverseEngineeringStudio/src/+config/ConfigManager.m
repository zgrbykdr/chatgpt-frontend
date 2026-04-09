classdef ConfigManager
    methods (Static)
        function c = defaultConfig()
            c = struct();
            c.mode = 'automatic';
            c.parallel = true;
            c.maxRuns = 200;
            c.weights = struct('accuracy',0.45,'interpretability',0.25,'runtime',0.15,'robustness',0.15);
        end

        function saveJSON(cfg,path)
            txt = jsonencode(cfg,PrettyPrint=true);
            fid=fopen(path,'w'); fwrite(fid,txt); fclose(fid);
        end

        function cfg = loadJSON(path)
            cfg = jsondecode(fileread(path));
        end
    end
end
