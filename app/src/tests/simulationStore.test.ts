import { useSimulationStore } from '../state/simulationStore';
import type { ProjectGraph } from '../lib/schemas';

test('store can add and remove nodes', () => {
  const id = useSimulationStore.getState().addNode({
    type: 'Pump',
    params: { modeling: 'LUMPED' },
    ports: [],
    position: { x: 0, y: 0 },
  });
  expect(useSimulationStore.getState().nodes.some((node) => node.id === id)).toBe(true);
  useSimulationStore.getState().removeNode(id);
  expect(useSimulationStore.getState().nodes.length).toBe(0);
});

test('store export produces valid project', () => {
  const id = useSimulationStore.getState().addNode({
    type: 'Compressor',
    params: { modeling: 'LUMPED' },
    ports: [],
    position: { x: 0, y: 0 },
  });
  const project = useSimulationStore.getState().exportProject();
  expect((project as ProjectGraph).components.length).toBeGreaterThan(0);
  useSimulationStore.getState().removeNode(id);
});
