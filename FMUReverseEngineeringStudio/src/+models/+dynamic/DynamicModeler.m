classdef DynamicModeler < models.base.CandidateModel
    properties, Logger, end
    methods
        function obj=DynamicModeler(logger)
            obj.Logger=logger; obj.Name="DynamicARX"; obj.Family="dynamic";
        end
        function out=fit(obj,dataset)
            [X,y] = localXY(dataset);
            z = iddata(y,X,1);
            obj.TrainedModel = arx(z,[2 2 1]);
            out=obj;
        end
        function yhat=predict(obj,X)
            z = iddata([],X,1);
            yp = sim(obj.TrainedModel,z);
            yhat = yp.y;
        end
    end
end
function [X,y]=localXY(dataset), n=varfun(@isnumeric,dataset,'OutputFormat','uniform'); d=dataset{:,n}; X=d(:,1:end-1); y=d(:,end); end
