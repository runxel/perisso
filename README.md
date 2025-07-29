# Perisso
> Short for "perissodactyla" /pəˌrɪsoʊˈdæktɪlə/ – the zoological order Tapiridae reside in.
> It's an experimental [Tapir](https://github.com/ENZYME-APD/tapir-archicad-automation) utility.  


## Overview
_Tapir_ provides a collection of tooling to assist the usage of the JSON API of Archicad.  
_Perisso_ is a Python package based on this fantastic work and aims to make it even easier to interact with and manipulate digital architectural model elements, by employing a fluent interface. This includes offering an efficient way to filter elements based on various criteria.


## Installation

1. Make sure you have the Tapir plugin for Archicad installed.
2. Install `perisso`.  
My recommendation: Always use [uv](https://docs.astral.sh/uv/). Use it for everything.

```bash
uv venv
uv pip install perisso
```

Alternatively, you just download the source files. Oldschool.


> [!WARNING]  
> Perisso is under development. Please expect breaking changes between versions.


## Usage

The simplest way is to just call `perisso()`. This will select all elements by default. To limit the elements to the current selection in Archicad use the `selection` parameter:
```python
sel_elem = perisso(selection=True)
```

Here is a basic example of how to use `perisso`:

```python
from perisso import perisso, Filter, ElType

elements = perisso()
filtered_elements = elements.filterBy(Filter.ELEMENT_TYPE).equals(ElType.COLUMN).get()
print(filtered_elements)
```

> [!CAUTION]
> The resulting element list is compatible with Tapir, but _not_ with the native [Archicad-Python connection](https://pypi.org/project/archicad/).  
For that you need to call the `toNative()` function on the perisso collection. The result uses the classes of the AC-Py connection and can then be fed into it.


See the [examples](https://github.com/runxel/perisso/tree/main/examples) for more.


> [!NOTE]  
> If a filter does _not_ apply the element concerned is silently removed (not _included_ in the result, that is). Example: A Property is not used on it.


## Contributing

Please open an issue or submit a pull request for any enhancements or bug fixes. Contributions are welcome, but might not be accepted until `perisso` reached a somewhat stable state.


## License

Perisso is licensed under the MIT License.
