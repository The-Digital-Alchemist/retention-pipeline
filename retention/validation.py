import os
from pathlib import Path
from typing import Optional

import typer
from dotenv import load_dotenv

app = typer.Typer()

allowed_extensions = [".mp3", ".mp4", ".wav", ".m4a"]

load_dotenv()


def sanitize_api_key(value: Optional[str]) -> str:
    """Normalize an API key string from env/settings."""
    if not value:
        return ""

    cleaned = value.strip()
    if not cleaned:
        return ""

    # Remove optional export prefix
    if cleaned.lower().startswith("export "):
        cleaned = cleaned.split(None, 1)[1].strip()

    if cleaned.upper().startswith("OPENAI_API_KEY="):
        cleaned = cleaned.split("=", 1)[1].strip()

    # Remove wrapping quotes if present
    if len(cleaned) >= 2 and cleaned[0] in {'"', "'"} and cleaned[-1] == cleaned[0]:
        cleaned = cleaned[1:-1].strip()

    return cleaned


def get_api_key() -> str:
    """Return the OpenAI API key from env or settings files."""
    import json

    api_key = sanitize_api_key(os.getenv("OPENAI_API_KEY"))
    if api_key:
        return api_key

    local_settings = Path("settings.json")
    if local_settings.exists():
        try:
            with open(local_settings, "r", encoding="utf-8") as f:
                settings = json.load(f)
                api_key = sanitize_api_key(settings.get("api_key"))
                if api_key:
                    return api_key
        except Exception:
            pass

    global_settings = Path.home() / ".retention_pipeline" / "settings.json"
    if global_settings.exists():
        try:
            with open(global_settings, "r", encoding="utf-8") as f:
                settings = json.load(f)
                api_key = sanitize_api_key(settings.get("api_key"))
                if api_key:
                    return api_key
        except Exception:
            pass

    return ""


def validate_api_key() -> bool:
    api_key = get_api_key()
    return bool(api_key and api_key.startswith("sk-"))


def validate_file_type(file_path: Path) -> bool:
    extension = file_path.suffix.lower()
    if extension in allowed_extensions:
        return True

    typer.echo("Invalid file type. Only audio files are allowed")
    return False


def validate_file_size(file_size: Path) -> bool:
    try:
        size = file_size.stat().st_size
    except FileNotFoundError:
        typer.echo("File not found")
        return False

    if size < 1024 * 1024:
        typer.echo("file size is less than 1 MB")
        return False
    if size > 1024 * 1024 * 1024:
        typer.echo("file size is greater than 1 GB")
        return False
    return True


@app.command("validate_file")
def validate_file(file_path: Path):
    if validate_api_key() and validate_file_type(file_path) and validate_file_size(file_path):
        return True
    return False


if __name__ == "__main__":
    app()
