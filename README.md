# Jupytercor

[![PyPI version](https://badge.fury.io/py/jupytercor.svg)](https://badge.fury.io/py/jupytercor)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
<!-- Add other badges here if applicable, e.g., build status, Python versions -->
<!-- Example: [![Python Versions](https://img.shields.io/pypi/pyversions/jupytercor)](https://pypi.org/project/jupytercor/) -->
<!-- Example: [![Build Status](https://img.shields.io/github/actions/workflow/status/YOUR_USER/jupytercor/main.yml?branch=main)](https://github.com/YOUR_USER/jupytercor/actions) -->

Jupytercor is a Python package that allows converting markdown cells of a Jupyter notebook using Pandoc.

## Installation and Usage

To install jupytercor, you need Python 3 and Pandoc installed on your machine. XeLaTeX is also required for PDF conversion.

You can then install jupytercor with pip:

```bash
pip install --upgrade jupytercor
```

To use jupytercor, execute the script with the following command:

```bash
jupytercor input.ipynb [-o output.ipynb] [--to FORMAT] [--template NAME] [--clean] [--images]
```

Where:

- `input.ipynb` is the name of the input notebook file to convert.
- `-o output.ipynb` or `--output-file output.ipynb` is an option to specify the name of the output file. This can be the processed `.ipynb` file or the final converted file (e.g., `mydoc.pdf`).
- `--to FORMAT` is an option to specify the output format.
    - `--to latex` to convert to LaTeX.
    - `--to pdf` to convert to PDF.
- `--template NAME` is an option to specify the LaTeX template to use (e.g., `cornouaille`, `eisvogel`). Defaults to `cornouaille`.
- `--clean` is an option to perform markdown cell cleaning with Pandoc (default is False).
- `--images` is an option to download remote images into an `images` folder and update links (default is False).

## Features and Options

Jupytercor offers the following features and options:

- Reads a notebook file in `.ipynb` format and extracts its markdown cells.
- Transforms each markdown cell to HTML with Pandoc using the `-f markdown -t html` option (with additional filters).
- Transforms each HTML cell back to markdown with Pandoc using the `-f html -t gfm-raw_html` option.
- Replaces the content of markdown cells with the transformed text.
- Writes a new notebook file in `.ipynb` format with the converted cells.
- Allows the user to choose the input and output notebook file names.
- Allows the user to enable or disable Pandoc conversions for cleaning with the `--clean` flag.
- Allows the user to download remote images using an URL with the `--images` flag.
- Supports conversion to LaTeX and PDF using specified Pandoc templates.

## License and Credits

Jupytercor is distributed under the MIT License.

Jupytercor uses the following libraries:
- `nbformat` to read and write notebook files.
- `subprocess` to execute Pandoc and XeLaTeX commands.
- `Typer` to parse command-line arguments.
- `requests` for downloading images.
- `Pillow` for image manipulation.
- `python-markdown` for parsing markdown during image extraction.
- `python-slugify` for creating safe filenames.
- `panflute` for Pandoc filters.

The image extraction logic is inspired by code found on this webpage: https://beautiful-soup-4.readthedocs.io/en/latest/#searching-the-tree (Note: This link refers to Beautiful Soup, which is not directly used, but the principle of tree traversal for extraction might be the inspiration).
