import React from 'react';
import { render, screen } from '@testing-library/react';
import { LiveProbe } from '../components/LiveProbe';
import { useSimulationStore } from '../state/simulationStore';
import { resetStore } from './utils';

beforeEach(() => {
  resetStore();
  const id = useSimulationStore.getState().addNode({
    type: 'Evaporator',
    params: { modeling: 'MB', pressure: 5, temperature: 10 },
    ports: [],
    position: { x: 0, y: 0 },
  });
  useSimulationStore.getState().select([id]);
});

test('live probe renders for node', () => {
  render(<LiveProbe probe={{ type: 'node', id: useSimulationStore.getState().nodes[0].id }} />);
  expect(screen.getByText(/Live Probe/)).toBeInTheDocument();
});

test('live probe returns null when no probe', () => {
  const { container } = render(<LiveProbe probe={null} />);
  expect(container.firstChild).toBeNull();
});
