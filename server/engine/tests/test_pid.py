from ..controls import PIDController


def test_pid_converges_toward_setpoint():
  pid = PIDController(kp=0.5, ki=0.1, kd=0.0, setpoint=10.0, u_min=0.0, u_max=1.0)
  measurement = 0.0
  for _ in range(50):
    control = pid.step(measurement, dt=0.1)
    measurement += control * 0.2
  assert abs(measurement - pid.setpoint) < 1.0


def test_pid_respects_bounds():
  pid = PIDController(kp=10.0, ki=5.0, kd=0.0, setpoint=100.0, u_min=0.0, u_max=0.5)
  control = pid.step(0.0, 0.1)
  assert 0.0 <= control <= 0.5
