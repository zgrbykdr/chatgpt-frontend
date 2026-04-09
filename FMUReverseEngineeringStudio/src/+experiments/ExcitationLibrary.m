classdef ExcitationLibrary
    methods (Static)
        function X = lhsSamples(inputs, rangeState, n)
            d = numel(inputs);
            if d==0, X = table(); return; end
            U = lhsdesign(n,d,'criterion','maximin','iterations',10);
            data = zeros(n,d);
            for j=1:d
                row = rangeState(strcmp(rangeState.name,inputs(j)),:);
                lo = row.low; hi = row.high;
                data(:,j) = lo + (hi-lo).*U(:,j);
            end
            X = array2table(data,'VariableNames',cellstr(inputs));
        end

        function y = prbs(n, amp)
            if nargin<2, amp=1; end
            y = amp*(2*(rand(n,1)>0.5)-1);
        end
    end
end
