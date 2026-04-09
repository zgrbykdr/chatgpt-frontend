classdef LUTModeler < models.base.CandidateModel
    properties, Logger, Grid, Values, end
    methods
        function obj=LUTModeler(logger)
            obj.Logger=logger; obj.Name="LUT"; obj.Family="lut";
        end
        function out=fit(obj,dataset)
            [X,y] = localXY(dataset);
            [~,ord]=sortrows(X,1);
            obj.Grid = X(ord,:); obj.Values = y(ord);
            out=obj;
        end
        function yhat=predict(obj,X)
            yhat = knnsearch(obj.Grid,obj.Values,'K',1); %#ok<KNNST>
        end
    end
end
function [X,y]=localXY(dataset), n=varfun(@isnumeric,dataset,'OutputFormat','uniform'); d=dataset{:,n}; X=d(:,1:end-1); y=d(:,end); end
