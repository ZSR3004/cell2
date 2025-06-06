import click

@click.command()
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