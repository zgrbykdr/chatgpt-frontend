import React from 'react';
import { useSimulationStore } from '../state/simulationStore';

const scenarios = [
  {
    id: 'W10/W35',
    description: 'Water-to-water heat pump: source 10°C, sink 35°C',
  },
  {
    id: 'B0/W35',
    description: 'Brine-to-water heat pump: source 0°C, sink 35°C',
  },
];

export const ScenarioWizard: React.FC = () => {
  const toggleScenario = useSimulationStore((state) => state.toggleScenario);

  return (
    <div className="pointer-events-auto absolute inset-0 flex items-center justify-center bg-slate-900/60">
      <div className="w-[480px] rounded-lg border border-slate-700 bg-slate-900 p-6 text-sm text-slate-100 shadow-2xl">
        <h2 className="text-lg font-semibold">EN 14511 Scenarios</h2>
        <p className="mt-2 text-xs text-slate-400">Select a reference test point to populate boundary conditions.</p>
        <div className="mt-4 space-y-3">
          {scenarios.map((scenario) => (
            <div key={scenario.id} className="rounded border border-slate-700 bg-slate-800 p-3">
              <p className="text-sm font-medium">{scenario.id}</p>
              <p className="text-xs text-slate-400">{scenario.description}</p>
              <button className="mt-2" onClick={() => toggleScenario(scenario.id)}>
                Load Scenario
              </button>
            </div>
          ))}
        </div>
        <button className="mt-4 w-full bg-slate-700" onClick={() => toggleScenario(null)}>
          Close
        </button>
      </div>
    </div>
  );
};
