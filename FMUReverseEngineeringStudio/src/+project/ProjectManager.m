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
            try
                obj.Metadata = inspector.inspect(fmuPath);
            catch ME
                if contains(ME.message, 'Subscripted assignment between dissimilar structures')
                    obj.Logger.warn("Primary FMU inspector failed with struct mismatch. Falling back to robust parser.");
                    obj.Metadata = fallbackInspectFMU(fmuPath, obj.Logger);
                else
                    rethrow(ME);
                end
            end
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

function meta = fallbackInspectFMU(fmuPath, logger)
% Defensive fallback parser that does not rely on struct-array assignment.
meta = struct('path',fmuPath,'variables',[],'fmuType','Unknown','modelName','','capabilities',struct());
temp = tempname; mkdir(temp);
cleanup = onCleanup(@() rmdir(temp,'s'));
unzip(fmuPath,temp);
xmlPath = fullfile(temp,'modelDescription.xml');
if ~isfile(xmlPath)
    error('FMU missing modelDescription.xml');
end

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
n = nodes.getLength;
records = repmat(tpl, 0, 1);
for i = 0:n-1
    node = nodes.item(i);
    rec = tpl;
    rec.name = string(node.getAttribute('name'));
    rec.valueReference = str2double(char(node.getAttribute('valueReference')));
    rec.causality = string(node.getAttribute('causality'));
    rec.variability = string(node.getAttribute('variability'));
    rec.description = string(node.getAttribute('description'));

    kids = node.getChildNodes;
    for k = 0:kids.getLength-1
        child = kids.item(k);
        if child.getNodeType ~= 1, continue; end
        rec.dataType = lower(string(child.getNodeName));
        if child.hasAttributes
            attrs = child.getAttributes;
            for a = 0:attrs.getLength-1
                at = attrs.item(a);
                key = lower(string(at.getName));
                value = char(at.getValue);
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
logger.info("Fallback FMU parser inspected variables: " + n);
clear cleanup
end
