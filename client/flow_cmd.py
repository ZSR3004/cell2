import os
import click
import src.tiffstack as ts
from src.defaults import default_process, default_flow
from src.memory import inbox_path, load_params

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
@click.option('--name', '-n', 
              type=str, 
              default=None, 
              help="Name of the cell to use for saving the results. If not provided, the name will be derived from the TIFF file name.")

def optflow(tune, default, name):
    """Optical flow related commands."""
    files = os.listdir(inbox_path)

    for file in files:
        if not file.endswith('.tif') or not file.endswith('.tiff'):
            raise click.exceptions(f"File {file} is not a TIFF file. Please remove all non-TIFF files from the inbox directory.")
        
    for file in files:
        if tune:
            click.echo(f"Sorry, this feature is not implemented yet. :p")
        
        elif default:
            click.echo(f"Using default parameters for {file}.")
            process_args = default_process
            flow_args = default_flow

        else:
            path = inbox_path / file
            img = ts.TiffStack(path, name)
            params, default_flag = load_params(img.stacktype)

            if default_flag:
                click.echo(f"Using default parameters for {file}.")
                process_args = default_process
                flow_args = default_flow
            else:
                click.echo(f"Using custom parameters for {file}.")
                process_args = params['process']
                flow_args = params['flow']

        flow = img.calculate_optical_flow(process_args=process_args, flow_args=flow_args)
        if flow.shape != (img.arr.shape[0] - 1, img.arr.shape[1], img.arr.shape[2], 2):
            raise click.exceptions(f"""
                                  Optical flow calculation failed for {file}. The output shape is {flow.shape}, 
                                  expected {(img.arr.shape[0] - 1, img.arr.shape[1], img.arr.shape[2], 2)}.
                                  \nPlease delete the corrputed file from the flow directory and try again.""")
        else:
            click.echo(f"Optical flow calculation successful for {file}!")