# Late-Bound Arguments

This package tries to emulate the behaviour of syntax proposed in [PEP 671](https://www.python.org/dev/peps/pep-0671/) via a decorator.

## Usage
Mention the names of the arguments which are to be late-bound in the arguments of the `delay` decorator, and their default values as strings in the function signature.

Mutable default arguments:
```python
from late_bound_arguments import delay

@delay("my_list")
def foo(my_list="[]"):
    my_list.append(1)
    return my_list

print(foo()) # [1]
print(foo()) # [1]
print(foo([1, 2, 3])) # [1, 2, 3, 1]
```

Referencing previous arguments:
```python
from late_bound_arguments import delay

@delay("my_list", "n")
def foo(my_list="[1, 2]", n: int = "len(my_list)"):
    return my_list, n


print(foo()) # ([1, 2], 2)
print(foo([1, 2, 3])) # ([1, 2, 3], 3)
```
Additionally, the function signature is not overwritten, so `help(foo)` will provide the original signature retaining the default values.


## Reasoning

Mutable defaults are often tricky to work with, and may not do what one might naively expect.

For example, consider the following function:
```python
def foo(my_list=[]):
    my_list.append(1)
    return my_list

    
print(foo())
print(foo())
```

One might expect that this prints `[1]` twice, but it doesn't. Instead, it prints `[1]` and `[1, 1]`. 
A new list object is *not* created every time `foo` is called without providing the `b` argument: the list is only created once - when the function is defined - and the same list object is used for every call. As a result, if it is mutated in any call, the change is reflected in subsequent calls.


A common workaround for this is using `None` as a placeholder for the default value, and replacing it inside the function body.
```python
def foo(my_list=None):
    if my_list is None: 
        my_list = []
    ...
```
In case `None` is a valid value for the argument, a sentinel object is created beforehand and used as the default instead.
```python
_SENTINEL = object()
def foo(my_list=_SENTINEL):
    if my_list is _SENTINEL: 
        my_list = []
    ...
```
However, this solution, apart from being unnecessarily verbose, has an additional drawback: `help(foo)` in a REPL will fail to inform of the default values, and one would have to go through the source code to find the true signature.