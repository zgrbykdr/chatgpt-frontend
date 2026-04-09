% demo_quickstart
% Launches GUI.
root = fileparts(fileparts(mfilename('fullpath')));
addpath(genpath(fullfile(root,'app')),'-begin');
addpath(genpath(fullfile(root,'src')),'-begin');
app = FMUReverseEngineeringStudioApp(); %#ok<NASGU>
