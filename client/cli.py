import click
from .init_cmd import init
from .flow_cmd import optflow
from .traj_cmd import traj
from .video_cmd import video

@click.group()
def cf():
    """Command line interface for CellFlow."""
    pass

cf.add_command(init)
cf.add_command(optflow)
cf.add_command(traj)
cf.add_command(video)