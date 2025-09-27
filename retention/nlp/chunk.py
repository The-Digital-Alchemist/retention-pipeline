import tiktoken
import typer
import json
from pathlib import Path

encoding = tiktoken.get_encoding("o200k_base")
app = typer.Typer()

chunk_size=500
overlap=50


@app.command()

def chunk_text(transcription: str):
    
    result = encoding.encode(transcription)

    i = 0
    chunks = []


    while i < len(result):
        chunk_tokens = result[ i : i + chunk_size]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append({"id": len(chunks) + 1, "text": chunk_text })
        i += chunk_size - overlap

    with open("data/chunks/chunks.json", "w", encoding="UTF-8") as f:
        f.write(json.dumps(chunks, ensure_ascii=False, indent=2))





@app.command()
def chunk_file(filename: str, output_dir : str = "data/chunks"):
    """
    CLI Command: reads a transcription file, chunks it, writes it to JSON
    """
    input_path = Path(filename)
    output_path = Path(output_dir) / f"{input_path.stem}_chunks.json"

    transcription = input_path.read_text(encoding="UTF-8")
    chunks = chunk_text(transcription)


    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="UTF-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)


    typer.echo(f"chunks saved to {output_path}")
if __name__ == "__main__":
    app()

