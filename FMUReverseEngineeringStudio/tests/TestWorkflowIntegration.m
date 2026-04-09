classdef TestWorkflowIntegration < matlab.unittest.TestCase
    methods(Test)
        function testOrchestratorWithSyntheticDataset(tc)
            ds = array2table(randn(120,4),'VariableNames',{'u1','u2','u3','y'});
            logger = logging.Logger(tempdir);
            orch = appcore.ModelOrchestrator(logger);
            out = orch.fitAndRank(ds, struct(), "automatic");
            tc.verifyGreaterThan(numel(out.Candidates),0);
        end
    end
end
