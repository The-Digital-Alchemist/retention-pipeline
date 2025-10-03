import os
import typer
from pathlib import Path
from dotenv import load_dotenv


app = typer.Typer()

allowed_extensions = [".mp3", ".mp4", ".wav", ".m4a"]

load_dotenv()


def get_api_key():
    """Return the OpenAI API key from env, local settings.json, or global settings path.

    Order of precedence:
    1) OPENAI_API_KEY environment variable
    2) ./settings.json (next to the executable or repo root)
    3) ~/.retention_pipeline/settings.json (used by SettingsManager)
    """
    import json

    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key

    local_settings = Path("settings.json")
    if local_settings.exists():
        try:
            with open(local_settings, "r") as f:
                settings = json.load(f)
                api_key = settings.get("api_key")
                if api_key:
                    return api_key
        except Exception:
            pass

    global_settings = Path.home() / ".retention_pipeline" / "settings.json"
    if global_settings.exists():
        try:
            with open(global_settings, "r") as f:
                settings = json.load(f)
                api_key = settings.get("api_key")
                if api_key:
                    return api_key
        except Exception:
            pass

    return ""


def validate_api_key():
    import json
    
    # First try environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    
    # If not found, try local settings.json (working directory)
    if not api_key:
        settings_path = Path("settings.json")
        if settings_path.exists():
            try:
                with open(settings_path, "r") as f:
                    settings = json.load(f)
                    api_key = settings.get("api_key")
            except:
                pass

    # If still not found, try the global settings path used by SettingsManager
    if not api_key:
        global_settings_path = Path.home() / ".retention_pipeline" / "settings.json"
        if global_settings_path.exists():
            try:
                with open(global_settings_path, "r") as f:
                    settings = json.load(f)
                    api_key = settings.get("api_key")
            except:
                pass

    # validate the api key
    if not api_key:
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