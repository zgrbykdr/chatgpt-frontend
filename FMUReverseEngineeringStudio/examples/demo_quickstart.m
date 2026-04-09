% demo_quickstart
% Launches GUI.
root = fileparts(fileparts(mfilename('fullpath')));
addpath(genpath(fullfile(root,'app')));
addpath(genpath(fullfile(root,'src')));
app = FMUReverseEngineeringStudioApp(); %#ok<NASGU>
