classdef PiecewiseModeler < models.base.CandidateModel
    properties, Logger, KmeansModel, LocalModels cell, end
    methods
        function obj=PiecewiseModeler(logger)
            obj.Logger=logger; obj.Name="Piecewise"; obj.Family="piecewise";
        end
        function out=fit(obj,dataset)
            [X,y] = localXY(dataset);
            k = min(3,max(2,round(size(X,1)/40)));
            idx = kmeans(X,k,'Replicates',3);
            obj.LocalModels = cell(1,k);
            for i=1:k
                obj.LocalModels{i} = fitlm(X(idx==i,:), y(idx==i));
            end
            obj.KmeansModel = fitcknn(X,idx,'NumNeighbors',3);
            out=obj;
        end
        function yhat=predict(obj,X)
            c = predict(obj.KmeansModel,X);
            yhat = zeros(size(X,1),1);
            for i=1:numel(obj.LocalModels)
                m = c==i; if any(m), yhat(m)=predict(obj.LocalModels{i},X(m,:)); end
            end
        end
    end
end
function [X,y]=localXY(dataset), n=varfun(@isnumeric,dataset,'OutputFormat','uniform'); d=dataset{:,n}; X=d(:,1:end-1); y=d(:,end); end
