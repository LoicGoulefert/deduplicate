# deduplicate

[`vpype`](https://github.com/abey79/vpype) plug-in to remove overlapping lines in SVG files.


## Usage

```
Usage: vpype deduplicate [OPTIONS]

  Remove duplicate lines.

  Args:     
    lines: LineCollection input
    tolerance: maximum tolerance to consider 2 lines equal
    progress_bar: flag, display a progress bar if set

  Returns:
    a LineCollection where duplicated lines were removed.

Options:
  -t, --tolerance LENGTH  Max distance between start and end point to consider
                          a path closed(default: 0.01mm)

  -p, --progress-bar      Display a progress bar
  -l, --layer LAYERS      Target layer(s) or 'all'.
  --help                  Show this message and exit.
```


## Examples

`vpype read file.svg deduplicate write output.svg`


## Installation

See the [installation instructions](https://vpype.readthedocs.io/en/stable/install.html) for information on how
to install `vpype`.


### Existing `vpype` installation

Use this method if you have an existing `vpype` installation (typically in an existing virtual environment) and you
want to make this plug-in available. You must activate your virtual environment beforehand.

```bash
$ pip install git+https://github.com/LoicGoulefert/deduplicate.git#egg=deduplicate
```

Check that your install is successful:

```
$ vpype --help
Usage: vpype [OPTIONS] COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...

Options:
  -v, --verbose
  -I, --include PATH  Load commands from a command file.
  --help              Show this message and exit.

Commands:
[...]
  Plugins:
    deduplicate
[...]
```

### Stand-alone installation

Use this method if you need to edit this project. First, clone the project:

```bash
$ git clone https://github.com/LoicGoulefert/deduplicate.git
$ cd deduplicate
```

Create a virtual environment:

```bash
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install --upgrade pip
```

Install `deduplicate` and its dependencies (including `vpype`):

```bash
$ pip install -e .
```

Check that your install is successful:

```
$ vpype --help
Usage: vpype [OPTIONS] COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...

Options:
  -v, --verbose
  -I, --include PATH  Load commands from a command file.
  --help              Show this message and exit.

Commands:
[...]
  Plugins:
    deduplicate
[...]
```


## License

See the [LICENSE](LICENSE) file for details.
