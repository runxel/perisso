# Perisso
> Short for "perissodactyla" /pəˌrɪsoʊˈdæktɪlə/ – the zoological order Tapiridae reside in.
> It's an experimental [Tapir](https://github.com/ENZYME-APD/tapir-archicad-automation) utility.  


## Overview
_Tapir_ provides a collection of tooling to assist the usage of the JSON API of Archicad.  
_Perisso_ is a Python package based on this fantastic work and aims to make it even easier to interact with and manipulate digital architectural model elements, by employing a fluent interface. This includes offering an efficient way to filter elements based on various criteria.

> [!WARNING]  
> Perisso is under development. Please expect breaking changes between versions.

## Usage

Here is a basic example of how to use the `perisso` package:

```python
from perisso import perisso, Filter, ElType

elements = perisso()
filtered_elements = elements.filterBy(Filter.ELEMENT_TYPE).equals(ElType.COLUMN).get()
print(filtered_elements)
```

## License

Perisso is licensed under the MIT License.
```

