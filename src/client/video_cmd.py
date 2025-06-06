import os
import click
from src.memory import main_path, load_metadata, save_video
from src.client.cli_utils import user_stack_input

@click.command()
def video():
    """Visualization related commands."""
    stacks, stack_index = user_stack_input()
    stack_path = os.path.join(main_path, stacks[stack_index])
    if 0 <= stack_index < len(stacks):
        ftag = click.prompt(f"You selected: {stacks[stack_index]}. Please type the file tag.")
        meta = load_metadata(stack_path)
        save_video(meta['name'], ftag)
        click.echo(f"Video saved for stack: {stacks[stack_index]} with tag: v{ftag}")
       
    else:
        click.echo("Invalid selection. Please run the command again and select a valid number.")