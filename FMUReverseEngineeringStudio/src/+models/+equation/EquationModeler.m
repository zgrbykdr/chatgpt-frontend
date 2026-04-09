classdef EquationModeler < models.base.CandidateModel
    properties, Logger, Variant string = "equation.simple", end
    methods
        function obj=EquationModeler(logger,variant)
            obj.Logger=logger; obj.Variant=variant; obj.Name="Equation"; obj.Family="equation";
        end
        function out = fit(obj,dataset)
            [X,y,names] = localXY(dataset);
            if isempty(X), error('No dataset.'); end
            switch obj.Variant
                case "equation.simple"
                    mdl = fitlm(X,y,'linear','VarNames',[names "y"]);
                otherwise
                    mdl = fitlm(X,y,'quadratic','VarNames',[names "y"]);
            end
            obj.TrainedModel = mdl;
            out = obj;
        end
        function y = predict(obj,X), y = predict(obj.TrainedModel,X); end
    end
end

function [X,y,names]=localXY(dataset)
    num = varfun(@isnumeric,dataset,'OutputFormat','uniform');
    t = dataset(:,num);
    names = string(t.Properties.VariableNames);
    y = t{:,end}; X = t{:,1:end-1}; names = names(1:end-1);
end
