from retention.nlp.prompts import DEEP_FLASHCARD_PROMPT, QUICK_FLASHCARD_PROMPT
from openai import OpenAI
import typer
from dotenv import load_dotenv
from pathlib import Path
import os
import json

app = typer.Typer()


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

@app.command()

def deep_flashcard(filename : str, output_dir : str = "data/flashcards"):
    """
    Convert the raw transcript into Anki-styled flashcards. A bit heavy on usage, but good for retaining maximum knowledge.
    """

    # Load the JSON chunks
    chunks = json.load(open(filename, "r", encoding="UTF-8"))

    # Construct the path
    path = Path(filename)
    flashcards_path = Path(output_dir) / f"{path.stem}_flashcards.md"
    flashcards_path.parent.mkdir(parents=True, exist_ok=True)

    # Initialize the list of flashcards
    all_flashcards = []

    for chunk in chunks:
        # Get the text of the chunk
        text = chunk["text"]

        # Construct the user prompt
        user_prompt = DEEP_FLASHCARD_PROMPT.format(transcript = text)


        # Send the prompt to the OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a super learning student who is known as the best at extracting knowledge from courses"},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0
        )

        content = response.choices[0].message.content

        print(content) # Debugging purposes
        all_flashcards.append(content)

    # Write the flashcards to a file
    with open(flashcards_path, "w", encoding="UTF-8") as f:
        f.write("\n\n".join(all_flashcards))

    typer.echo(f"Flashcards saved to {flashcards_path}")


@app.command()
def quick_flashcard(filename : str, output_dir : str = "data/flashcards"):
    """
    Convert the raw transcript into Anki-styled flashcards. A bit heavy on usage, but good for retaining maximum knowledge.
    """
    
    # Load the summaries
    summaries = json.load(open(filename, "r", encoding="UTF-8"))
    summaries = [s["summary"] for s in summaries]

    # Initialize the list of flashcards
    all_flashcards = []

    # Construct the path
    path = Path(filename)
    flashcards_path = Path(output_dir) / f"{path.stem}_flashcards.md"
    flashcards_path.parent.mkdir(parents=True, exist_ok=True)

    # Construct the user prompt
    user_prompt = QUICK_FLASHCARD_PROMPT.format(summaries=summaries)

    # Send the prompt to the OpenAI API
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a super learning student who is known as the best at extracting knowledge from courses"},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0
    )
    content = response.choices[0].message.content
    print(content) # Debugging purposes
    all_flashcards.append(content)

    # Write the flashcards to a file
    with open(flashcards_path, "w", encoding="UTF-8") as f:
        f.write("\n\n".join(all_flashcards))

    typer.echo(f"Flashcards saved to {flashcards_path}")


if __name__ == "__main__":
    app()
