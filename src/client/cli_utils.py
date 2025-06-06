import os
import click
from src.memory import main_path

def user_stack_input() -> list | str:
    """
    Prompts the user to select a stack from the available stacks in the main path.
    
    This function lists all directories in the main path, excluding 'types.json', and allows the user
    to select one by entering its corresponding number.
    
    Returns:
        str: The name of the selected stack.
    """
    stacks = [entry for entry in os.listdir(main_path) if 
                os.path.isdir(os.path.join(main_path, entry)) and entry != 'types.json']

    click.echo(f"Please select a stack to visualize from. Please enter only the number.")
    for i in range(len(stacks)):
        click.echo(f"{[i]}: {stacks[i]}")
    stack_index = click.prompt("Enter the number of the stack: ", type=int)
    return stacks, stack_index