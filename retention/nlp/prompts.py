CHUNK_SUMMARY_PROMPT = """ 
Your job is to summarize the following transcript chunks into clean, high quality summaries.\
Use only the information presented in the summary, do not add facts that are not present.
Return only JSON, no extra text and with keys 'summary', 'key_points', 'questions'.
Transcript: 
{chunk_text} """