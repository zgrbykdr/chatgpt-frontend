classdef ProjectManager < handle
    properties
        RootPath string
        Logger
        Config struct
        FMUPath string = ""
        Metadata struct = struct()
        VariableCatalog table = table()
        RangeState table = table()
        DatasetRepo datahub.DatasetRepository
    end

    methods
        function obj = ProjectManager(rootPath, logger)
            obj.RootPath = string(rootPath);
            obj.Logger = logger;
            obj.Config = config.ConfigManager.defaultConfig();
            obj.DatasetRepo = datahub.DatasetRepository();
        end

        function loadFMU(obj, fmuPath)
            arguments, obj, fmuPath (1,1) string, end
            obj.FMUPath = fmuPath;
            inspector = fmu.FMUInspector(obj.Logger);
            obj.Metadata = inspector.inspect(fmuPath);
            builder = metadata.VariableCatalogBuilder(obj.Logger);
            obj.VariableCatalog = builder.build(obj.Metadata);
            infer = ranges.RangeInferenceEngine(obj.Logger);
            obj.RangeState = infer.inferInitialRanges(obj.VariableCatalog, obj.Metadata);
        end

        function t = getVariableCatalogTable(obj)
            if isempty(obj.VariableCatalog), t = table(); return; end
            t = obj.VariableCatalog(:, intersect(obj.VariableCatalog.Properties.VariableNames, ...
                {'name','causality','variability','unit','dataType','inferredRange','userRange','activeFlag'}));
        end

        function saveProject(obj, filePath)
            state = struct('Config',obj.Config,'FMUPath',obj.FMUPath, ...
                'Metadata',obj.Metadata,'VariableCatalog',obj.VariableCatalog,'RangeState',obj.RangeState);
            save(filePath, '-struct', 'state');
            obj.Logger.info("Project state saved: " + filePath);
        end
    end
end
