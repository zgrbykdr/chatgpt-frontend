from fmu_reverse_engineering.core.registry import Registry


def test_registry_create() -> None:
    reg = Registry()
    reg.register('x', lambda value=1: {'value': value})
    created = reg.create('x', value=2)
    assert created['value'] == 2
