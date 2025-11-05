import React from 'react';
import { GraphCanvas } from './components/GraphCanvas';
import { NodePalette } from './components/NodePalette';
import { PropertyPanel } from './components/PropertyPanel';
import { RunControls } from './components/RunControls';
import { ValidationHUD } from './components/ValidationHUD';
import { InspectorOverlay } from './components/InspectorOverlay';
import { ScenarioWizard } from './components/ScenarioWizard';
import { useSimulationStore } from './state/simulationStore';
import { useSimulationSocket } from './hooks/useSimulationSocket';

const App: React.FC = () => {
  const { validation, activeScenario } = useSimulationStore((state) => ({
    validation: state.validation,
    activeScenario: state.activeScenario,
  }));
  useSimulationSocket();

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-background">
      <NodePalette />
      <div className="relative flex flex-1 flex-col">
        <RunControls />
        <GraphCanvas />
        <ValidationHUD validation={validation} />
        <InspectorOverlay />
        {activeScenario ? <ScenarioWizard /> : null}
      </div>
      <PropertyPanel />
    </div>
  );
};

export default App;
