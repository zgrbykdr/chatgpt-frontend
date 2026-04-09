classdef ValidationRunner
    methods
        function metrics = evaluate(~, model, dataset)
            [X,y] = localXY(dataset);
            yhat = model.predict(X);
            metrics = validation.MetricCalculator.compute(y,yhat);
        end
    end
end
function [X,y]=localXY(dataset), n=varfun(@isnumeric,dataset,'OutputFormat','uniform'); d=dataset{:,n}; X=d(:,1:end-1); y=d(:,end); end
