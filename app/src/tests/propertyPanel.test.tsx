import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { PropertyPanel } from '../components/PropertyPanel';
import { useSimulationStore } from '../state/simulationStore';
import { resetStore } from './utils';

beforeEach(() => {
  resetStore();
  useSimulationStore.getState().addNode({
    type: 'Evaporator',
    params: { modeling: 'MB', area: 10 },
    ports: [],
    position: { x: 0, y: 0 },
  });
  useSimulationStore.getState().select([useSimulationStore.getState().nodes[0].id]);
});

test('property panel displays selected component info', () => {
  render(<PropertyPanel />);
  expect(screen.getByText('Evaporator')).toBeInTheDocument();
});

test('property panel updates parameter values', () => {
  render(<PropertyPanel />);
  const input = screen.getByDisplayValue('10');
  fireEvent.change(input, { target: { value: '15' } });
  expect(useSimulationStore.getState().nodes[0].params.area).toBe('15');
});
