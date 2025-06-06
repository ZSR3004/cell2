import os
import click
from src.memory import main_path, load_metadata, save_video

@click.command()
def video():
    """Visualization related commands."""
    stacks = [entry for entry in os.listdir(main_path) if 
              os.path.isdir(os.path.join(main_path, entry)) and entry != 'types.json']

    click.echo(f"Please select a stack to visualize from. Please enter only the number.")
    for i in range(len(stacks)):
        click.echo(f"{[i]}: {stacks[i]}")
    stack_index = click.prompt("Enter the number of the stack: ", type=int)
    stack_path = os.path.join(main_path, stacks[stack_index])
    if 0 <= stack_index < len(stacks):
        ftag = click.prompt(f"You selected: {stacks[stack_index]}. Please type the file tag.")
        meta = load_metadata(stack_path)
        save_video(meta['name'], ftag)
        click.echo(f"Video saved for stack: {stacks[stack_index]} with tag: v{ftag}")
       
    else:
        click.echo("Invalid selection. Please run the command again and select a valid number.")