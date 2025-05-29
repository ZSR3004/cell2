# Mitchel Lab Cell Tracking Project

## Table of Contents

1. [Project Overview](#project-overview)

2. [Installation](#installation)

3. [Usage Examples](#usage-examples)

4. [Future Additions](#future-additions)

5. [Acknowledgments](#acknowledgments)

## Project Overview

## Installation

I've created a toml file to make downloading dependencies easy. If you have a virtual environment, activate that, but otherwise just run the following in the terminal.

```bash
pip install poetry
poetry install
```

That'll download all the required libraries. If you want to manually do it, you can take a look at the `pyproject.toml` file, and that will have the libraries and their versions. I'll also list the dependencies below with a brief explanation of what they're used for.

- numpy: Used to manipulate Tiff files and store data.
- scipy: Mostly just used for its gaussian laplace function during preprocessing.
- tifffile: To extract numpy arrays from Tiff files.
- matplotlib: Graphing frames, stacks, and optical flows.
- opencv-python: Preprocessing and core optical flow functions.
- optuna: Tuning parameters for optical flow and preprocessing.

## Usage Examples

## Future Additions

## Acknowledgments
