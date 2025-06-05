# Mitchel Lab Cell Tracking Project

## Table of Contents

1. [Project Overview](#project-overview)

2. [How Files are Saved](#how-files-are-saved)

3. [Basic Usage](#basic-usage)

4. [CellFlow as Code Example](#cellflow-as-code-example)

5. [Acknowledgments](#acknowledgments)

## Project Overview

This README is intended for people who want to _use_ this tool. I'm in the process for writing a manual for contributers who might go in an fix/update things I've written, which you can find under the Wiki tab of Github.

CellFlow (CF) is a command line interface that allows you to analyze tiff stacks of cells. It primarily calculates optical flow and trajectories of cell movement. CF allows users to automatically fine-tune parameters if they wish and output videos of the optical flow/trajectory vector fields. Note that CellFlow was primarily created with Windows in mind. It should work on MacOs, but I'm not optimizing anything for that.

You can use this as a Python library instead, and while I won't discuss how to use CellFlow as a library in this README, I've included example of Jupyter notebooks which you can find in `example_notebooks`.

The rest of this README will walk through the basics of CF, explaining the directory setup, commands you'll need to know, and example uses.

## How Files are Saved

When you use this program, the `init_memory` function is ran. This creates a file labeled "Optical Flow" on the current user's desktop. As of the time of creating this program, the Mitchel formats their files in a `DATE_CELLTYPE` format. This file name is used to name the subdirectories of the "Optical Flow" folder. In general, the "Optical Flow" has the following structure.
```
Optical Flow/
  |-  types.json
  |-  in/
      |-  DATE_CELLTYPE.tiff
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
```

A `.tiff` is what we call a tiff stack file. This might be one you're familiar with because it's the file type CellFlow analyzes. This basically contains a video of cell moving.

A `.json` file is a structured datafile. If you 'double-click' such a file, you can actually read it directly. This is the primary way someone in the lab is expected to use the json. For whoever is maintaining this program, this is a structured datafile that you can turn into a python dictionary.

A `.np` file is a giant array of numbers. If you're a lab member, this isn't super useful to you directly, but you can use programs to visualize whatever information is held in the file. If you're messing with the code, then you can use the very popular `numpy` library to load, save, and manipulate `.np` files. In fact, `.np` files are literally just how `numpy` saves an `np array`.

### types.json

When performing optical flow and trajectory tracking, we have to fine tune parameters to get an accurate result. That process takes a lot of time (upwards of hours). This `types.json` takes the `CELLTYPE` part of the file name and basically makes a dictionary and saves these parameters as the value. This allows the program to check if we've already seen this type of cell and pickup the parameters instead of repeated parameter tuning. Opening this file, isn't super helpful to lab members, but if you want, you can manually change the parameters for a type of file.

### in/

This is where you'll put the tiff file you want to analyze. This is just so that you don't have to type out an incredibly long file name. CellFlow will just go through and analyze _all_ the tiff files in in/ when you execute a command.

### DATE_CELLTYPE/

This is the primary file for your TIFF stack. When you upload a file of the name `DATE_CELLTYPE` this is the first file created. It'll contain all the information for that TIFF file.

### flow/

This folder holds the optical flow outputs for your Tiff file. This information is stored in a `.np` file of shape `(frames, view, height, width, 2)`, where the 2 represents a `(dx, dy)` pair. Basically, this has multiple views, each with some amount of frames. For each one of these frames, you have `(dx, dy)` pairs that represent the velocity in the x and y direction. In effect, each view is a vector field.

The name scheme is just the original file's name, appended with '_fi' where is i is some integer. The f stands for 'flow' and the integer is to prevent the overriding of optical flow. The user can manually delete any unwanted flows by navigating the directory on the desktop.

### trajectory/

This folder holds the trajectory information for the TIFF file. Information is stored in a `.np` file of shape `(frames, view, height, width, 2)`. This is exactly a vector field as described above in [flow](#flow).

The name scheme is similar to that above as well, with the files's name being appended with '_ti', where t stands for 'trajectory' and i is an integer that increments to avoid file overwriting.

### video/

This folder holds any videos the user might have created. Users can either created videos of the optical flow or the trajectory. They're in an `.mp4` format, so you should be able to play it from really any device.

This name scheme is a little more complicated than the other files. Again, we have the file's original name tagged with something. Either this is '_vfi' which stands for "video flow" (the i being an integer to avoid overwriting videos) or it's '_vti' which stands for "video trajectory" (i being used for the same reason).

### meta.json

This file holds metadata about the original Tiff stack. In particular, `meta.json` has the following structure when loaded into Python.

```python
{
        "path": path,
        "stack_type": CELLTYPE,
        "name": DATE_CELLTYPE
    }
```

This is all information you could parse out from the "Optical Flow" folder, but I put it in its own json to make it easier to access.

## Basic Usage

Let's say you've finally installed CellFlow. Open an empty cmd window (or Powershell if you prefer). The first thing you have to do is init the directory (the one described [above](#how-files-are-saved)). Navigate to whatever directory you want to make the main directory in using the `cd` command (I'll use Desktop as an example).

```bash
> cd path\to\your\desired\directory # this is the general format
> cd C:\Users\my_username\Desktop # this is the example
```

Now, we'll use CellFlow to create our directory.

```bash
> cf init
```

This will create a new file labeled CellFlow in that directory. Notice the format of this command. The first "word" is `cf` which stands for CellFlow. This just tells the computer that you're accessing the CellFlow program. You're basically just telling the computer that you want CellFlow to do something. The second "word" is the actual command, in this case `init` which stands for initialize (the directory/program). 

You can move into that directory using the `cd` command again.

```bash
> cd CellFlow
```

Now, you can view the actual file. If you can easily access it from the explorer/finder, just double click on the file. Otherwise, we can use the command line to open it.

```bash
> explorer.exe . # the period just means the current directory
```

You should see something like this:

```
|-  types.json
|-  in/
```

Now, take you tiff stack and drop it into `in/`. Now, your directory will look like this.

```
|-  types.json
|-  in/
    |-  DATE_CELLTYPE.tiff # this is your file
```

Let's go back to the command line. Now, we'll execute just evaluate the optical flow for this program.

```bash
> cf optflow
```

You'll see a loading screen, then CellFlow will tell you that you're done! Now, your directory will look like this.

```
|-  types.json
|-  in/
    |-  DATE_CELLTYPE.tiff 
|-  DATE_CELLTYPE
    |-  meta.json
    |-  flow/
        |-  DATE_CELLTYPE_f0.np
```

That's it! The file `DATE_CELLTYPE_f0.np` is your optical flow file. This probably isn't super helpful to you (although you'll want to keep this since it'll act as sort of a "raw data" file). Instead, your probably want to visualize it. CellFlow has a nice little feature where you can make a video of the vector field. Let's say you want to have the vector field over the original video (that is, you want to have a video of the vector field and want the video of the cells moving as the background).

Notice the "`_f0.np`" at the end of the file in `flow/`. That's important. Every time you run the optical flow command you'll get a new file with the same name, except that number is increased by one. Let's call this the index number. Currently, we're interested in making a video of the file indexed with 0. So, type the following. 

```bash
> cf video 
```

In the command line, you'll see something like this.

```bash
[0]  DATE_CELLTYPE

Please select a stack.
```

You'll notice the 0 next to your file. This is just to help with accessing it. So, just type in 0. You'll now see something like this.

```bash
> 0
Which type of field do you want to make a video of? Type 'f' for optical flow and 't' for trajectory.
> f
Flags? Press ENTER if none.
> overlay
```

Flags are optional arguments you can give CellFlow. Basically, this can change the default behavior of the program. In this case, CellFlow usually doesn't do the overlay, but you're instructing it to do so now. You should now see the following in your directory.

```
|-  types.json
|-  in/
    |-  DATE_CELLTYPE.tiff 
|-  DATE_CELLTYPE
    |-  meta.json
    |-  flow/
        |-  DATE_CELLTYPE_f0.np
    |-  video/
        |-  DATE_CELLTYPE_vf0.mp4
```

This was the interactive route. If you already know the index and commands you want to input, you can just type the following for the same effect.

```bash
cf video 0 f0 --overlay
```

Notice how the flag (overlay) is preceded by the double dashes (--). You'll have to include that if you want CellFlow to read the flag properly. You can also shorthand it as `-o`, this time using a single dash. Now, we'll do the exact same thing with the trajectory. This is similar to optical flow, but with a couple of more caveats. Let's go over two situations. First, you run the trajectory command directly. Second, you have and you want to make the trajectory of a specific optical flow file. We'll keep using the index 0 for the tiff stack.

1. Direct.

```bash
cf traj
```

You'll see a loading screen (this might take a while) and that's it! Running the command directly means its creating a trajectory of original stack. That is, its creating a _new_ optical flow and tracking the trajectory of that. So, your directory will look like this.

```
|-  types.json
|-  in/
    |-  DATE_CELLTYPE.tiff 
|-  DATE_CELLTYPE
    |-  meta.json
    |-  flow/
        |-  DATE_CELLTYPE_f0.np
        |-  DATE_CELLTYPE_f1.np
    |-  trajectory/
        |-  DATE_CELLTYPE_t1.np
    |-  video/
        |-  DATE_CELLTYPE_vf0.mp4
```

Notice the `f1` and `t1`. This just means that this trajectory corresponds with the optical flow (ie. the 1 indicates this is the trajectory of optical flow 1).

2. Of a specific flow.
Now, suppose you want to do the trajectory for a specific optical flow. Let's do it of `DATE_CELLTYPE_f1.np` again. Suppose we don't know the index. We can do this interactively by executing the following command.

```bash
cf traj --spec
```

or

```bash
cf traj -s
```

Now, you'll see this.

```bash
[0]  DATE_CELLTYPE

Please select a stack.
> 0
Which flow?
> 1 # find the index by looking at the file
Flags? Press ENTER if none.
>
```

We won't enter any flags. Now, your directory will look like this.

```
|-  types.json
|-  in/
    |-  DATE_CELLTYPE.tiff 
|-  DATE_CELLTYPE
    |-  meta.json
    |-  flow/
        |-  DATE_CELLTYPE_f0.np
        |-  DATE_CELLTYPE_f1.np
    |-  trajectory/
        |-  DATE_CELLTYPE_t1.np
        |-  DATE_CELLTYPE_t1a.np
    |-  video/
        |-  DATE_CELLTYPE_vf0.mp4
```

Notice how we still have `t1` at the end of the trajectory file. The `a` just denotes its the second version. This will increment alphabetically, going from 'a' to 'b' and so on. Once you hit 'z', it'll wrap around and do 'aa'.

Now, let's make a video of the `t1a` trajectory. We're not going to overlay it on the original video this time. We'll also use our shortcut.

```bash
cf video 0 t1a --overlay
```

Now, the directory will look like this.

```
|-  types.json
|-  in/
    |-  DATE_CELLTYPE.tiff 
|-  DATE_CELLTYPE
    |-  meta.json
    |-  flow/
        |-  DATE_CELLTYPE_f0.np
        |-  DATE_CELLTYPE_f1.np
    |-  trajectory/
        |-  DATE_CELLTYPE_t1.np
        |-  DATE_CELLTYPE_t1a.np
    |-  video/
        |-  DATE_CELLTYPE_vf0.mp4
        |- DATE_CELLTYPE_vt1a.mp4
```

That's the whole workflow! If you're done, remove your file from the `in/` box, and you can just take out the file with all the videos and optical flows.

## Cell Flow as Code Examples

For usage examples, please refer to the `example_notebooks` directory.

## Acknowledgments
