import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ScenarioWizard } from '../components/ScenarioWizard';
import { useSimulationStore } from '../state/simulationStore';

beforeEach(() => {
  useSimulationStore.setState({
    activeScenario: 'EN14511',
  } as any);
});

test('scenario wizard lists EN14511 options', () => {
  render(<ScenarioWizard />);
  expect(screen.getByText('W10/W35')).toBeInTheDocument();
  expect(screen.getByText('B0/W35')).toBeInTheDocument();
});

test('scenario wizard close button toggles scenario', () => {
  render(<ScenarioWizard />);
  fireEvent.click(screen.getByText('Close'));
  expect(useSimulationStore.getState().activeScenario).toBeNull();
});
