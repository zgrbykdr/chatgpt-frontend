classdef FMUInspector
    properties
        Logger
    end

    methods
        function obj = FMUInspector(logger), obj.Logger = logger; end

        function meta = inspect(obj, fmuPath)
            arguments, obj, fmuPath (1,1) string, end
            obj.Logger.info("FMUInspector implementation: " + string(mfilename('fullpath')));
            meta = struct('path',fmuPath,'variables',[],'fmuType','Unknown','modelName','','capabilities',struct());
            temp = tempname; mkdir(temp);
            c = onCleanup(@() rmdir(temp,'s'));
            unzip(fmuPath,temp);
            xmlPath = fullfile(temp,'modelDescription.xml');
            if ~isfile(xmlPath)
                error('FMU missing modelDescription.xml');
            end
            d = xmlread(xmlPath);
            root = d.getDocumentElement;
            meta.modelName = string(root.getAttribute('modelName'));
            co = root.getElementsByTagName('CoSimulation');
            me = root.getElementsByTagName('ModelExchange');
            if co.getLength>0, meta.fmuType='CoSimulation'; elseif me.getLength>0, meta.fmuType='ModelExchange'; end

            vars = root.getElementsByTagName('ScalarVariable');
            n = vars.getLength;
            template = struct( ...
                'name',"", ...
                'valueReference',NaN, ...
                'causality',"", ...
                'variability',"", ...
                'description',"", ...
                'startValue',NaN, ...
                'minValue',NaN, ...
                'maxValue',NaN, ...
                'nominalValue',NaN, ...
                'unit',"", ...
                'dataType',"real");
            records = cell(n,1);
            for i=0:n-1
                node = vars.item(i);
                rec = template;
                rec.name = string(node.getAttribute('name'));
                rec.valueReference = str2double(char(node.getAttribute('valueReference')));
                rec.causality = string(node.getAttribute('causality'));
                rec.variability = string(node.getAttribute('variability'));
                rec.description = string(node.getAttribute('description'));
                for cidx=0:node.getChildNodes.getLength-1
                    child = node.getChildNodes.item(cidx);
                    if child.getNodeType~=1, continue; end
                    rec.dataType = lower(string(child.getNodeName));
                    if child.hasAttributes
                        attrs = child.getAttributes;
                        for a=0:attrs.getLength-1
                            at = attrs.item(a); k = char(at.getName); val = char(at.getValue);
                            switch lower(k)
                                case 'start', rec.startValue = str2double(val);
                                case 'min', rec.minValue = str2double(val);
                                case 'max', rec.maxValue = str2double(val);
                                case 'nominal', rec.nominalValue = str2double(val);
                                case 'unit', rec.unit = string(val);
                            end
                        end
                    end
                end
                records{i+1} = normalizeRecord(template, rec);
            end
            if isempty(records)
                meta.variables = repmat(template, 0, 1);
            else
                meta.variables = vertcat(records{:});
            end
            obj.Logger.info("FMU inspected. Variables: " + n);
        end
    end
end

function out = normalizeRecord(template, rec)
% Normalize any partially-populated record to an exact template shape.
out = template;
tplFields = fieldnames(template);
for i = 1:numel(tplFields)
    f = tplFields{i};
    if isfield(rec, f)
        out.(f) = rec.(f);
    end
end
end
