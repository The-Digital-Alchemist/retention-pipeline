import os
import typer
from pathlib import Path
from dotenv import load_dotenv


app = typer.Typer()

allowed_extensions = [".mp3", ".mp4", ".wav", ".m4a"]

load_dotenv()



def validate_api_key():
    
    api_key = os.getenv("OPENAI_API_KEY")

    # validate the api key
    if not api_key:
        typer.echo("OPENAI_API_KEY not found in the environment variables")
        return False
    elif not api_key.startswith("sk-"):
        return False
    else:
        return True


def validate_file_type(file_path: Path):
    
    # Validate the file type
    extension = file_path.suffix.lower() # Getting the file extension and normalizing it
    if extension in allowed_extensions:
        return True
    else:
        typer.echo("Invalid file type. Only audio files are allowed")
        return False


def validate_file_size(file_size: Path):

    # Validate the file size (not less than 1 MB, not more than 1 GB)
    try: 
        if file_size.stat().st_size < 1024 * 1024: 
            typer.echo("file size is less than 1 MB")
            return False
        if file_size.stat().st_size > 1024 * 1024 * 1024:
            typer.echo("file size is greater than 1 GB")
            return False
        else:
            return True
    except FileNotFoundError:
        typer.echo("File not found")
        return False

@app.command("validate_file")
def validate_file(file_path: Path):
    
    # Validate the file
    if validate_api_key() and validate_file_type(file_path) and validate_file_size(file_path):
        return True
    else:
        return False


if __name__ == "__main__":
    app()