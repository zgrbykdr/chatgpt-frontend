import React from 'react';
import { render, screen } from '@testing-library/react';
import { InspectorOverlay } from '../components/InspectorOverlay';
import { useSimulationStore } from '../state/simulationStore';
import { resetStore } from './utils';

beforeEach(() => {
  resetStore();
  const addNode = useSimulationStore.getState().addNode;
  addNode({ type: 'Compressor', params: { modeling: 'LUMPED' }, ports: [], position: { x: 10, y: 10 } });
  useSimulationStore.getState().addEdge({ id: 'e1', from: { id: useSimulationStore.getState().nodes[0].id, port: 'out' }, to: { id: useSimulationStore.getState().nodes[0].id, port: 'in' }, type: 'fluid' });
});

test('inspector overlay lists nodes and edges', () => {
  render(<InspectorOverlay />);
  expect(screen.getByText('Compressor')).toBeInTheDocument();
  expect(screen.getByText(/→/)).toBeInTheDocument();
});
