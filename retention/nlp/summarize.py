from retention.nlp.prompts import CHUNK_SUMMARY_PROMPT, MASTER_SUMMARY_PROMPT
from openai import OpenAI
from dotenv import load_dotenv
import os
import typer
from pathlib import Path
import json

app = typer.Typer()

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

@app.command()
def summarize_file(filename: str, output_dir: str = "data/summaries"):
    """
    Summarize each chunk from a chunks.json file into a single Markdown file.
    """
    # Load chunks.json
    chunks = json.load(open(filename, "r", encoding="utf-8"))    
    summaries = []

    # Build output path
    path = Path(filename)
    summaries_path = Path(output_dir) / f"{path.stem}_summary.md"
    summaries_path.parent.mkdir(parents=True, exist_ok=True)

    # Loop through chunks
    for chunk in chunks:
        text = chunk["text"]

        # Format prompt with chunk text
        user_prompt = CHUNK_SUMMARY_PROMPT.format(chunk_text=text)

        # Send request to OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a summarizer that outputs only JSON."},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0
        )

        content = response.choices[0].message.content

        # Parse JSON safely
        try:
            parsed = json.loads(content) # type: ignore
        except json.JSONDecodeError:
            typer.echo(f"Failed to parse JSON for chunk {chunk['id']}, raw output:\n{content}")
            continue

        # Store structured summary
        summaries.append({
            "id": chunk["id"],
            "summary": parsed.get("summary", ""),
            "key_points": parsed.get("key_points", []),
            "questions": parsed.get("questions", [])
        })

    # Write all summaries to Markdown
    with open(summaries_path, "w", encoding="utf-8") as f:
        f.write("# Lecture Summary\n\n")
        for s in summaries:
            f.write(f"## Chunk {s['id']}\n")
            f.write(f"**Summary:** {s['summary']}\n\n")
            f.write("**Key Points:**\n")
            for p in s["key_points"]:
                f.write(f"- {p}\n")
            f.write("\n**Questions:**\n")
            for q in s["questions"]:
                f.write(f"- {q}\n")
            f.write("\n\n")

    # Write sidecar JSON for quick flashcards
    summaries_json_path = Path(output_dir) / f"{path.stem}_summaries.json"
    with open(summaries_json_path, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    typer.echo(f" Summaries saved to {summaries_path}")
    typer.echo(f" Summaries JSON saved to {summaries_json_path}")

    typer.echo("Creating a master summary...")

    master_summary(summaries, str(summaries_path))





@app.command()
def master_summary(summaries_list: list, output_path: str):
    """
    Generate a master summary of the most valuable, important and relevant information."""


    # Join the summaries into a single string

    summaries = "\n".join([s["summary"] for s in summaries_list])

    # Construct the user prompt
    master_prompt = MASTER_SUMMARY_PROMPT.format(summaries=summaries)

    # Send the prompt to the OpenAI API
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are one of the top superlearners in the world"},
            {"role": "user", "content": master_prompt}
        ],
        temperature=0
    )

    # Parse the response
    content = response.choices[0].message.content


    try:
        parsed = json.loads(content) # type: ignore
    except json.JSONDecodeError as e:
        typer.echo(f"JSON parsing error: {e}")
        typer.echo("Failed to parse master summary JSON")
        return

    # Appending the master summary to the output file
    with open(output_path, "a", encoding="UTF-8") as f:
        f.write("\n\n# Master summary\n\n")
        f.write(f"**Summary:** {parsed.get("summary", "")}\n\n")
        f.write("**Key Points:**\n")
        for p in parsed.get("key_points", []):
            f.write(f"- {p}\n")
        f.write("\n**Questions:**\n")
        for q in parsed.get("questions", []):
            f.write(f"- {q}\n")



if __name__ == "__main__":
    app()
