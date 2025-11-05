from ..components.sensor import Sensor


def test_sensor_temperature_default():
  sensor = Sensor('s1', 'Sensor', 'LUMPED', {'quantity': 'temperature', 'temperature': 285.0})
  sensor.initialize()
  out = sensor.step({}, 1.0)
  assert out['measurement'] == 285.0


def test_sensor_pressure_default():
  sensor = Sensor('s2', 'Sensor', 'LUMPED', {'quantity': 'pressure', 'pressure': 500000})
  sensor.initialize()
  out = sensor.step({}, 1.0)
  assert out['measurement'] == 500000


def test_sensor_massflow_default():
  sensor = Sensor('s3', 'Sensor', 'LUMPED', {'quantity': 'massFlow', 'massFlow': 0.25})
  sensor.initialize()
  out = sensor.step({}, 1.0)
  assert out['measurement'] == 0.25
