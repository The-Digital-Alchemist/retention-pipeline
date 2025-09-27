import typer
from pathlib import Path
import whisper
from retention.nlp.chunk import chunk_file, chunk_text
from retention.nlp.summarize import summarize_file


model = whisper.load_model("base")
app = typer.Typer()


@app.command()

def run(lecture: str):

    path = Path(lecture)


    if not path.exists():
        print (f"file not found: {lecture}")
        return
    
  
    print (f"Got file: {lecture} \n Transcribing....")
    result = model.transcribe(str(lecture))


    # save the raw transcription
    transcription_path =  Path("data/transcriptions") / f"{path.stem}_transcription.txt"
    transcription_path.parent.mkdir(parents=True, exist_ok=True)
    transcription_path.write_text(str(result["text"]), encoding="UTF-8") 

    print(f"chunking lecture {lecture} transcriptions..")
    chunk_file(str(transcription_path))


    print("Done chunking. Summarizing now...")

    summarize_file("data/chunks/chunks.json")




if __name__ == "__main__":
    app()