import typer
from pathlib import Path
import whisper
from retention.nlp.chunk import chunk_file, chunk_text
from retention.nlp.summarize import summarize_file
from retention.validation import validate_file


model = whisper.load_model("base")
app = typer.Typer()


@app.command()

def run(lecture: str):

    path = Path(lecture)    

    if not validate_file(path):
        typer.echo("Validation failed. Please check the errors above.", err=True)
        raise typer.Exit(1)

    
  
    typer.echo(f"Got file: {lecture} \n Transcribing....")
    result = model.transcribe(str(lecture))


    # save the raw transcription
    transcription_path =  Path("data/transcriptions") / f"{path.stem}_transcription.txt"
    transcription_path.parent.mkdir(parents=True, exist_ok=True)
    transcription_path.write_text(str(result["text"]), encoding="UTF-8") 

    typer.echo(f"chunking lecture {lecture} transcriptions..")
    chunk_file(str(transcription_path))

    # Generate the expected chunk file path
    chunk_file_path = f"data/chunks/{path.stem}_transcription_chunks.json"

    typer.echo("Done chunking. Summarizing now...")

    summarize_file(chunk_file_path)




if __name__ == "__main__":
    app()