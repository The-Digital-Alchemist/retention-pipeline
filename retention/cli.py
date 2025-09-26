import typer
from pathlib import Path


app = typer.Typer()


@app.command()

def run(lecture: str):

    path = Path(lecture)
    if path.exists():
        print (f"Got file: {lecture}")
    else:
        print (f"file not found: {lecture}")




if __name__ == "__main__":
    app()