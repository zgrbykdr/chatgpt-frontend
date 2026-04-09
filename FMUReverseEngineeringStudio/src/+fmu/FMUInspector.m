classdef FMUInspector
    properties
        Logger
    end

    methods
        function obj = FMUInspector(logger), obj.Logger = logger; end

        function meta = inspect(obj, fmuPath)
            arguments, obj, fmuPath (1,1) string, end
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
            v = repmat(struct(), n, 1);
            for i=0:n-1
                node = vars.item(i);
                rec = struct();
                rec.name = string(node.getAttribute('name'));
                rec.valueReference = str2double(char(node.getAttribute('valueReference')));
                rec.causality = string(node.getAttribute('causality'));
                rec.variability = string(node.getAttribute('variability'));
                rec.description = string(node.getAttribute('description'));
                rec.startValue = NaN; rec.minValue = NaN; rec.maxValue = NaN; rec.nominalValue = NaN; rec.unit = ""; rec.dataType="real";
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
                v(i+1)=rec;
            end
            meta.variables = v;
            obj.Logger.info("FMU inspected. Variables: " + n);
        end
    end
end
