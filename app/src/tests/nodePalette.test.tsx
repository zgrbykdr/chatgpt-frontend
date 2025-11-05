import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { NodePalette } from '../components/NodePalette';
import { useSimulationStore } from '../state/simulationStore';
import { resetStore } from './utils';

beforeEach(() => {
  resetStore();
});

test('adding component from palette creates node', () => {
  render(<NodePalette />);
  const button = screen.getByText('Evaporator');
  fireEvent.click(button);
  const nodes = useSimulationStore.getState().nodes;
  expect(nodes.some((node) => node.type === 'Evaporator')).toBe(true);
});

test('palette shows modeling badges', () => {
  render(<NodePalette />);
  expect(screen.getByText('MB')).toBeInTheDocument();
  expect(screen.getByText('LUMPED')).toBeInTheDocument();
});
