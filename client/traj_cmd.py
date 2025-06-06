import click
from client.cli_utils import user_stack_input
from src.memory import main_path, load_flow
from src.defaults import default_trajectory
from src.trajectory import trajectory
import os

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
    stacks, stack_index = user_stack_input()

    if stack_index < 0 or stack_index >= len(stacks):
        click.exceptions("Invalid stack selection. Please run the command again and select a valid number.")

    stack_path = main_path / stacks[stack_index]
    flow_path = stack_path / 'flow'
    flows = [
        entry for entry in flow_path.iterdir()
        if entry.is_file() and entry.suffix == '.npy' and '_' in entry.stem
    ]
    ftags = [
        entry.stem.rsplit('_', 1)[-1]
        for entry in flows
    ]

    ftag = click.prompt(f"""You selected: {stacks[stack_index]}. Please type the file tag or type 'list' (or 'l') 
                        to get a list of all the tags.""")
    if ftag.lower() == 'list' or ftag.lower() == 'l':
        for entry in ftags:
            click.echo(f"{entry}")
        ftag = click.prompt(f"""You selected: {stacks[stack_index]}. Please type the file tag or type 'list' (or 'l') 
                        to get a list of all the tags.""")
    elif ftag not in ftags:
        raise click.exceptions(f"File tag {ftag} not found in the flow directory. Please check the available tags.")

    try:
        ftag_index = ftags.index(ftag)
    except ValueError:
        raise click.exceptions(f"File tag {ftag} not found in the flow directory. Please check the available tags.")
    
    flow_name = flows[ftag_index]
    flow = load_flow(stack_path / flow_name)

    if tune:
        click.echo("Sorry, this feature is not implemented yet. :p")

    if default:
        click.echo(f"Using default parameters for {flow_name}.")
        traj_args = default_trajectory
    
    trajectory(flow, **traj_args)