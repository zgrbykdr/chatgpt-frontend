classdef VariableCatalogBuilder
    properties, Logger, end
    methods
        function obj=VariableCatalogBuilder(logger), obj.Logger=logger; end

        function catalog = build(obj, meta)
            vars = meta.variables;
            n=numel(vars);
            catalog = table('Size',[n 20], ...
                'VariableTypes',repmat("string",1,20), ...
                'VariableNames',{'name','valueReference','role','causality','variability','unit','description','dataType','dimension','startValue','nominalValue','minValue','maxValue','defaultValue','inferredRange','userRange','activeFlag','fixedConstantFlag','confidence','notes'});
            for i=1:n
                v=vars(i);
                role = "state";
                if any(strcmpi(v.causality, ["input","independent"])), role="input"; end
                if any(strcmpi(v.causality, ["output","calculatedParameter"])), role="output"; end
                catalog.name(i)=string(v.name);
                catalog.valueReference(i)=string(v.valueReference);
                catalog.role(i)=role;
                catalog.causality(i)=string(v.causality);
                catalog.variability(i)=string(v.variability);
                catalog.unit(i)=string(v.unit);
                catalog.description(i)=string(v.description);
                catalog.dataType(i)=string(v.dataType);
                catalog.dimension(i)="1";
                catalog.startValue(i)=string(v.startValue);
                catalog.nominalValue(i)=string(v.nominalValue);
                catalog.minValue(i)=string(v.minValue);
                catalog.maxValue(i)=string(v.maxValue);
                catalog.defaultValue(i)=string(v.startValue);
                catalog.inferredRange(i)="[]";
                catalog.userRange(i)="";
                catalog.activeFlag(i)="true";
                catalog.fixedConstantFlag(i)="false";
                catalog.confidence(i)="0.5";
                catalog.notes(i)="";
            end
            obj.Logger.info("Variable catalog built.");
        end
    end
end
