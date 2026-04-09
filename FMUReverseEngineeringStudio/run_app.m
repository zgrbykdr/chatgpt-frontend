root = fileparts(mfilename('fullpath'));
addpath(genpath(fullfile(root,'app')),'-begin');
addpath(genpath(fullfile(root,'src')),'-begin');
FMUReverseEngineeringStudioApp;
