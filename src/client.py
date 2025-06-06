import click
from defaults import default_process, default_flow, default_trajectory
import src.tiffstack as ts
from src.memory import init_memory, main_path, types_path

@click.group()
def cf():
    """Command line interface for CellFlow."""
    pass

@cf.command()
@click.option('--force', '-f', 
              is_flag=True, 
              help="""
              Force re-initialization of memory, even if it already exists.
              \nWARNING: This will delete everything in the CellFlow direcctory.
              """)
def init(force):
    """Initialize CellFlow."""
    init_memory()

@cf.command()
@click.option('--tune', '-t', 
           is_flag=True, 
           help="""
           Tune the parameters for the default process. This may take a while... upwards of 
           hours PER TIFF FILE, but if you're not getting good results, it might be worth 
           running overnight. It's recommended that you take one tiff file of each type, 
           then run it.
           \nWARNING: This will overwrite the current parameters in types.json.
           """)
@click.option('--default', '-d', 
           is_flag=True, 
           help="Use the default parameters for the process.")
def optflow(tune, default):
    """Optical flow related commands."""
    pass

@cf.command()
@click.option('--tune', '-t', 
           is_flag=True, 
           help="""
           Tune the parameters for the default process. This may take a while... upwards of 
           hours PER TIFF FILE, but if you're not getting good results, it might be worth 
           running overnight. It's recommended that you only tune once per experiment setup.
           \nWARNING: This will overwrite the current parameters in types.json.
           """)
@click.option('--default', '-d', 
           is_flag=True, 
           help="Use the default parameters for the process.")
@click.option('-flows', '-f', 
              multiple=True,
              help="Select optical flow files to extract a trajectory file from.")
def traj(tune, default, flows):
    """Trajectory related commands."""
    pass

@cf.command()
def video():
    """Visualization related commands."""
    pass