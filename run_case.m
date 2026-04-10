function result = run_case(caseInput, options)
%RUN_CASE CLI-like entrypoint for full CFD workflow orchestration.
% Usage examples:
%   result = run_case('case_config.json');
%   result = run_case(struct('geometry',...));

if nargin < 1
    caseInput = struct();
end
if nargin < 2
    options = struct();
end

result = cfd.app.WorkflowController(caseInput, options);
end
