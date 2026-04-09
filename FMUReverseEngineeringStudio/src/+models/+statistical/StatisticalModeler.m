classdef StatisticalModeler < models.base.CandidateModel
    properties, Logger, end
    methods
        function obj=StatisticalModeler(logger)
            obj.Logger=logger; obj.Name="GPR"; obj.Family="statistical";
        end
        function out=fit(obj,dataset)
            [X,y] = localXY(dataset);
            obj.TrainedModel = fitrgp(X,y,'KernelFunction','ardsquaredexponential', ...
                'Standardize',true);
            out=obj;
        end
        function yhat=predict(obj,X), yhat = predict(obj.TrainedModel,X); end
    end
end
function [X,y]=localXY(dataset), n=varfun(@isnumeric,dataset,'OutputFormat','uniform'); d=dataset{:,n}; X=d(:,1:end-1); y=d(:,end); end
