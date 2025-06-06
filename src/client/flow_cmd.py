import click

@click.command()
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