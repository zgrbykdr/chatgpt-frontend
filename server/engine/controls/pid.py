from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PIDController:
  kp: float
  ki: float
  kd: float
  setpoint: float
  u_min: float = 0.0
  u_max: float = 1.0
  integral: float = 0.0
  prev_error: float = 0.0

  def step(self, measurement: float, dt: float) -> float:
    error = self.setpoint - measurement
    self.integral += error * dt
    self.integral = max(self.u_min, min(self.u_max, self.integral))
    derivative = (error - self.prev_error) / max(dt, 1e-6)
    self.prev_error = error
    output = self.kp * error + self.ki * self.integral + self.kd * derivative
    return max(self.u_min, min(self.u_max, output))
