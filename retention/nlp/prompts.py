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