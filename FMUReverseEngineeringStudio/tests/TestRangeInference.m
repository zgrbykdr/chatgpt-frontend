classdef TestRangeInference < matlab.unittest.TestCase
    methods(Test)
        function testInferFromMissingBounds(tc)
            logger = logging.Logger(tempdir);
            t = table("u1","input","0",nan,nan,'VariableNames',{'name','role','startValue','minValue','maxValue'});
            t.causality="input"; t.variability="continuous"; t.unit=""; t.description=""; t.dataType="real";
            t.dimension="1"; t.nominalValue="1"; t.defaultValue="0"; t.inferredRange=""; t.userRange="";
            t.activeFlag="true"; t.fixedConstantFlag="false"; t.confidence="0.5"; t.notes=""; t.valueReference="1";
            r = ranges.RangeInferenceEngine(logger).inferInitialRanges(t,struct());
            tc.verifyLessThan(r.low(1), r.high(1));
        end
    end
end
