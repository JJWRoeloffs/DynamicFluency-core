# DynamicFluency-core

The base python package for DynamicFluency: track a l2 speaker's ability trough time. 

This package is effectivly a wrapper around a meriad of other projects to allow for smooth intergration

## Code style

For code formatting, [Black](https://github.com/psf/black) is used with default settings. Some of the naming from [praatio](https://github.com/timmahrt/praatIO) (e.g. `entryList`) is taken over, but, generally, `snake_case` is used for everything but classes, which are in `PascalCase`, as is python convention.

Also, I, (JJWRoeloffs,) am dyslectic, so there might be some spelling errors in the variable names and docstrings. If you find some, pull requests are welcome!

## Tests

Running the development tests can be done with the following command:
```
pytest --cov=dynamicfluency tests/
```
Please note that this requires pytest and pytest-cov to be installed. Additionally, `dynamicfluency` has to be installed, either with `pip install -e .` or trough other means if you want to compare versions. The code itself, as it is in `src/`, isn't recognised.  