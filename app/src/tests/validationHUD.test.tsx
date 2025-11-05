import React from 'react';
import { render, screen } from '@testing-library/react';
import { ValidationHUD } from '../components/ValidationHUD';

const validation = {
  energyResidual: 1.2,
  jacobianCondition: 2.5,
  warnings: ['Cavitation risk'],
};

test('validation HUD displays metrics and warnings', () => {
  render(<ValidationHUD validation={validation} />);
  expect(screen.getByText(/Energy residual/)).toBeInTheDocument();
  expect(screen.getByText(/Jacobian/)).toBeInTheDocument();
  expect(screen.getByText('Cavitation risk')).toBeInTheDocument();
});
