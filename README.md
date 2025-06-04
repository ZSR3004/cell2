# Mitchel Lab Cell Tracking Project

## Table of Contents

1. [Project Overview](#project-overview)

3. [Installation](#installation)

4. [How Files are Saved](#how-files-are-saved)

5. [Usage Examples](#usage-examples)

7. [Acknowledgments](#acknowledgments)

## Project Overview

This README is intended for people who want to _use_ this tool. I'm in the process for writing a manual for contributers who might go in an fix/update things I've written.
This README is inteded for people who want to contribute/maintain this code. I'm in the process of writing a manual for users who don't need to know the intricacies of how the object is setup. This README doesn't go into massive detail on the implementation (aside from the directory format).

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

## How Files are Saved

When you use this program, the `init_memory` function is ran. This creates a file labled "Optical Flow" on the current user's desktop. As of the time of creating this program, the Mithcel (roughly) formats their files in a `DATE_CELLTYPE` format. This file name is used to name the subdirectories of the "Optical Flow" folder. In general, the "Optical Flow" has the following structure.
```
Optical Flow/
  |-  types.json
  |-  DATE_CELLTYPE/
      |-  flow/
          |-  DATE_CELLTYPE_f0.np
          |-  DATE_CELLTYPE_f1.np
          |-  DATE_CELLTYPE_f2.np
      |-  trajectory/
          |-  DATE_CELLTYPE_t0.np
          |-  DATE_CELLTYPE_t1.np
      |-  video/
          |-  DATE_CELLTYPE_vf0.mp4
          |-  DATE_CELLTYPE_vt0.mp4
      |-  meta.json
      |-  arr.np
```

A `.json` file is a structured datafile. If you 'double-click' such a file, you can actually read it directly. This is the primary way someone in the lab is expected to use the json. For whoever is maintaining this program, this is a structured datafile that you can turn into a python dictionary.

A `.np` file is a giant array of numbers. If you're a lab member, this isn't super useful to you directly, but you can use programs to visualize whatever information is held in the file. If you're messing with the code, then you can use the very popular `numpy` library to load, save, and manipulate `.np` files. In fact, `.np` files are literally just how `numpy` saves an `np array`.

### types.json
When performing optical flow and trajectory tracking, we have to fine tune parameters to get an accurate result. That process takes a lot of time (upwards of hours). This `types.json` takes the `CELLTYPE` part of the file name and basically makes a dictionary and saves these parameters as the value. This allows the program to check if we've already seen this type of cell and pickup the parameters instead of repeated parameter tuning. Opening this file, isn't super helpful to lab members, but if you want, you can manuallly change the parmeters for a type of file.

### DATE_CELLTYPE/

This is the primary file for your TIFF stack. When you upload a file of the name `DATE_CELLTYPE` this is the first file created. It'll contain all the information for that TIFF file.

### flow/

This folder holds the optical flow outputs for your Tiff file. This information is stored in a `.np` file of shape `(frames, view, height, width, 2)`, where the 2 represents a `(dx, dy)` pair. Basically, this has multiple views, each with some amount of frames. For each one of these frames, you have `(dx, dy)` pairs that represent the velocity in the x and y direction. In effect, each view is a vector field.

The name scheme is just the orignal file's name, appended with '_fi' where is i is some integer. The f stands for 'flow' and the integer is to prevent the overriding of optical flow. The user can manually delete any unwated flows by navigating the directory on the desktop.

### trajectory/

This folder holds the trajectory information for the TIFF file. Information is stored in a `.np` file of shape `(frames, view, height, width, 2)`. This is exactly a vector field as described above in [flow](###flow/).

The name scheme is similar to that above as well, with the files's name being appended with '_ti', where t stands for 'trajectory' and i is an integer that increments to avoid file overwriting.

### video/

This folder holds any videos the user might have created. Users can either created videos of the optical flow or the trajectory. They're in an `.mp4` format, so you should be able to play it from really any device.

This name scheme is a little more complicated than the other files. Again, we have the file's orginal name tagged with something. Either this is '_vfi' which stands for "video flow" (the i being an integer to avoid overwriting videos) or it's '_vti' which stands for "video trajectory" (i being used for the same reason).

### meta.json

This file holds metadata about the orginal Tiff stack. In particular, `meta.json` has the following structure when loaded into Python.

```python
{
        "path": path,
        "stack_type": CELLTYPE,
        "name": DATE_CELLTYPE
    }
```

This is all information you could parse out from the "Optical Flow" folder, but I put it in its own json to make it easier to access.

### arr.np

This is an `.np` file that holds the original Tiff stack. It's in shape `(frames, channels, height, width)`.

## Usage Examples
For usage examples, please refer to the `example_notebooks` subdirectory.

## Acknowledgments
