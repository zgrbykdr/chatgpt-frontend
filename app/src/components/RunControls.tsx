import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useSimulationStore } from '../state/simulationStore';
import { apiClient } from '../lib/apiClient';

export const RunControls: React.FC = () => {
  const { exportProject, toggleScenario, activeScenario } = useSimulationStore((state) => ({
    exportProject: state.exportProject,
    toggleScenario: state.toggleScenario,
    activeScenario: state.activeScenario,
  }));
  const [isRunning, setRunning] = React.useState(false);

  const fluidsQuery = useQuery({
    queryKey: ['fluids'],
    queryFn: () => apiClient.getFluids(),
    staleTime: 60000,
  });

  const handleRun = async () => {
    const payload = exportProject();
    await apiClient.loadGraph(payload);
    await apiClient.runSimulation({ mode: 'continuous' });
    setRunning(true);
  };

  const handlePause = async () => {
    await apiClient.pauseSimulation();
    setRunning(false);
  };

  const handleReset = async () => {
    await apiClient.resetSimulation();
    setRunning(false);
  };

  const handleScenario = () => {
    toggleScenario(activeScenario ? null : 'EN14511');
  };

  return (
    <div className="flex items-center justify-between border-b border-slate-800 bg-slate-900/70 px-4 py-2 text-sm">
      <div className="flex items-center space-x-2">
        <button onClick={handleRun} disabled={isRunning}>
          Run
        </button>
        <button onClick={handlePause} disabled={!isRunning}>
          Pause
        </button>
        <button onClick={handleReset}>Reset</button>
        <button onClick={handleScenario} className={activeScenario ? 'bg-emerald-600 hover:bg-emerald-500' : ''}>
          {activeScenario ? 'Scenario: EN14511' : 'Load EN14511'}
        </button>
      </div>
      <div className="flex items-center space-x-4 text-xs text-slate-400">
        <span>
          Fluids: {fluidsQuery.isSuccess ? fluidsQuery.data.join(', ') : fluidsQuery.isLoading ? 'Loading…' : 'Unavailable'}
        </span>
      </div>
    </div>
  );
};
