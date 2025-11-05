import { act } from 'react-dom/test-utils';
import { useSimulationStore } from '../state/simulationStore';

export const resetStore = () => {
  const { nodes, edges } = useSimulationStore.getState();
  if (nodes.length || edges.length) {
    act(() => {
      useSimulationStore.setState({
        nodes: [],
        edges: [],
        selection: [],
        validation: { energyResidual: 0, jacobianCondition: 1, warnings: [] },
        activeScenario: null,
        graphVersion: 0,
      });
    });
  }
};
