CHUNK_SUMMARY_PROMPT = """ 
Your job is to summarize the following transcript chunks into clean, high quality summaries.\
Use only the information presented in the summary, do not add facts that are not present.
Return only JSON, no extra text and with keys 'summary', 'key_points', 'questions' (as an array).
Transcript: 
{chunk_text} """




MASTER_SUMMARY_PROMPT = """
Your job is to take a look at the following summaries, and create a master summary of the most valuable, important and relevant information.
Structure the summary for course learning with clear sections for key concepts, important insights, and actionable takeaways.
Return only JSON, no extra text, no markdown formatting, no code blocks, and with keys 'summary' (as a single string), 'key_points' (as an array), 'questions' (as an array).
Summaries: 
{summaries} """



DEEP_FLASHCARD_PROMPT = """
Pretend you're designing a quiz to train someone's to be the best at the provided topic.
Task:
- Create flashcards from the provided transcript text.
- The questions should be challenging and test deep understanding of the material.
- Avoid trivia, dates, or obscure details. Focus on key concepts, mechanisms, and insights.
- Keep answers concise, accurate, and directly tied to the question.

Format rules:
- Return ONLY flashcards in the following format, no extra text, no explanations:
START
Basic
(Question here)
Back: (Answer here)
Tags: (Optional comma-separated tags)
END

Transcript:
{transcript}
"""



QUICK_FLASHCARD_PROMPT = """
Pretend you’re designing a 5-minute quiz to test someone’s understanding of the main concepts, not the details
Task:
- Create flashcards from the provided summaries.
- The questions should be challenging and test deep understanding of the material.
- Limit to a maximum of 10 cards.
- Avoid trivia, dates, or obscure details. Focus on key concepts, mechanisms, and insights.
- Keep answers concise, accurate, and directly tied to the question.

Format rules:
- Return ONLY flashcards in the following format, no extra text, no explanations:
START
Basic
(Question here)
Back: (Answer here)
Tags: (Optional comma-separated tags)
END

Summaries:
{summaries}
"""