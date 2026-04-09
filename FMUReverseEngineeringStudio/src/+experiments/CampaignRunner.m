classdef CampaignRunner
    properties, Logger, end
    methods
        function obj=CampaignRunner(logger), obj.Logger=logger; end
        function runs = materializeRuns(~,plan)
            nr = height(plan.matrix);
            runs = repmat(struct('id',0,'inputs',struct(),'timeoutSec',10),nr,1);
            for i=1:nr
                runs(i).id = i;
                runs(i).inputs = table2struct(plan.matrix(i,:));
            end
        end
    end
end
