import click
from src.memory import init_memory

@click.command()
@click.option('--force', '-f', 
              is_flag=True, 
              help="""
              Force re-initialization of memory, even if it already exists.
              \nWARNING: This will delete everything in the CellFlow direcctory.
              """)
def init(force):
    """Initialize CellFlow."""
    init_memory(overwrite_flag=force)