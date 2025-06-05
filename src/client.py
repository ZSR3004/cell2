import click
from defaults import default_process, default_flow, default_trajectory
import src.tiffstack as ts

@click.group()
def cf():
    """Command line interface for CellFlow."""
    pass

@cf.group()
def init():
    """Initialize CellFlow."""
    pass

@cf.group()
def optical_flow():
    """Optical flow related commands."""
    pass

@cf.group()
def trajectory():
    """Trajectory related commands."""
    pass

@cf.group()
def visualize():
    """Visualization related commands."""
    pass