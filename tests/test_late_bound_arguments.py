from late_bound_arguments import __version__, delay
import pytest


def test_version():
    assert __version__ == '0.1.0'


def test_errors_on_unexpected_args():
    with pytest.raises(TypeError):
        @delay('a', 'x')
        def foo(a: int = "1"):
            ...


def test_errors_on_no_defaults():
    with pytest.raises(TypeError):
        @delay('a')
        def foo(a: int):
            ...


def test_inserts_new_mutable_defaults():
    @delay('my_list')
    def foo(my_list: list[int] = "[]"):
        my_list.append(1)
        return my_list

    assert foo() == foo() == [1]


def test_ignores_when_default_is_filled():
    @delay('my_list')
    def foo(my_list: list[int] = "[]"):
        my_list.append(2)
        return my_list

    assert foo([1]) == [1, 2]


def test_can_reference_prev_args():
    @delay("my_list", "n")
    def foo(my_list="[1, 2]", n: int = "len(my_list)"):
        return my_list, n

    assert foo() == ([1, 2], 2)
    assert foo([1, 2, 3]) == ([1, 2, 3], 3)


def test_errors_on_unbound_args():
    @delay('a', 'my_list')
    def foo(a: int = "len(my_list)", my_list: list[int] = "[]"):
        ...
    with pytest.raises(TypeError):
        foo()
