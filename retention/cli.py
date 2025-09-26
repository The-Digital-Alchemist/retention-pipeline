import typer
from pathlib import Path
import whisper

model = whisper.load_model("base")
app = typer.Typer()


@app.command()

def run(lecture: str):

    path = Path(lecture)
    if path.exists():
        print (f"Got file: {lecture} \n Transcribing....")
        result = model.transcribe(lecture)
        with open("output.txt", "w", encoding="utf-8") as f:
            f.write(result["text"]) # type: ignore
       
    else:
        print (f"file not found: {lecture}")




if __name__ == "__main__":
    app()