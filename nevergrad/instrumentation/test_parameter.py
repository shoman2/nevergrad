import pytest
import numpy as np
from .core3 import Parameter
from . import parameter as par


def test_array_basics() -> None:
    var1 = par.Array((1,))
    var2 = par.Array((2, 2))
    d = par.ParametersDict(var1=var1, var2=var2, var3=12)
    data = d.to_std_data()
    assert data.size == 5
    d.with_std_data(np.array([1, 2, 3, 4, 5]))
    assert var1.value[0] == 1
    np.testing.assert_array_equal(d.value["var2"], np.array([[2, 3], [4, 5]]))
    # setting value on arrays
    with pytest.raises(ValueError):
        var1.value = np.array([1, 2])
    with pytest.raises(TypeError):
        var1.value = 4  # type: ignore
    var1.value = np.array([2])
    representation = repr(d)
    assert "ParametersDict{var1" in representation
    d.with_name("blublu")
    representation = repr(d)
    assert "blublu:{'var1" in representation


@pytest.mark.parametrize("param", [par.Array(2, 2),  # type: ignore
                                   par.ParametersDict(blublu=par.Array((2, 3)), truc=12)])
def test_parameters_basic_features(param: Parameter) -> None:
    assert isinstance(param.name, str)
    assert param._random_state is None
    child = param.spawn_child()
    assert param._random_state is not None
    child.mutate()
    assert child.name == param.name
    assert child.random_state is param.random_state
    assert child.compute_data_hash() != param.compute_data_hash()
    assert child.uid != param.uid
    assert child.parents_uids == [param.uid]
    assert child.compute_data_hash() != param.compute_data_hash()
    param.value = child.value
    assert param.compute_value_hash() == child.compute_value_hash()
    # constraints
    param.register_cheap_constraint(lambda x: False)
    child2 = param.spawn_child()
    assert child.complies_with_constraint()
    assert not param.complies_with_constraint()
    assert not child2.complies_with_constraint()