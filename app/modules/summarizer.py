from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from openai import api_key

from app.modules.schema import MeetingMinutes
from app.config import OPENAI_API_KEY
import os
from typing import List

# Function to generate meeting minutes from a transcript using OpenAI
def generate_meeting_minutes(transcript: str) -> MeetingMinutes:
    """
    Takes a transcript as input and uses a large language model (LLM)
    via LangChain to generate structured meeting minutes in JSON format.

    Args:
        transcript (str): The transcript text of the meeting.

    Returns:
        MeetingMinutes: A structured JSON object with the meeting details.
    """
    parser = PydanticOutputParser(pydantic_object=MeetingMinutes)
    format_instructions = parser.get_format_instructions().replace("{", "{{").replace("}", "}}")

    prompt_template = """
You are an intelligent AI assistant. Your task is to read the meeting transcript below and extract important details to generate structured meeting minutes.
If any section is missing, set its value to null.
The output must follow the JSON format exactly, with keys in the order provided:
{format_instructions}

Sample Output:
{{
  "meeting_date": "30/03/2025",
  "meeting_time": "10:00 - null",
  "location": "Meeting Room A",
  "host": "Nguyen Van A",
  "note_taker": "Tran Thi B",
  "attendees": ["Nguyen Van A", "Tran Thi B", "Le Van C", "Pham Thi D"],
  "meeting_goal": "Review progress and plan next steps",
  "agenda": ["Progress report", "Challenge discussion", "Solutions and task assignments"],
  "discussion_content": {{
    "Progress report": ["70% of work is complete"],
    "Challenges": ["Lack of testing personnel"],
    "Solutions": ["Add 2 testers", "Le Van C will lead", "Deadline: 15/04/2025"]
  }},
  "decisions": ["Approve adding personnel", "Reassign tasks"],
  "conclusion": "Agreed on next meeting date and deadline",
  "attached_documents": null,
  "notes": null
}}

Transcript to process:
{transcript}
"""

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["transcript"],
        partial_variables={"format_instructions": format_instructions}
    )

    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
    formatted_prompt = prompt.format_prompt(transcript=transcript)
    response = llm.invoke(formatted_prompt.to_messages())

    meeting_minutes = parser.parse(response.content)
    return meeting_minutes


# Function to combine multiple MeetingMinutes objects into one
def merge_meeting_minutes(minutes_list: List[MeetingMinutes]) -> MeetingMinutes:
    """
    Merges a list of meeting minutes into one object.
    - Combines list fields (e.g., attendees) without duplicates.
    - Merges discussion content by combining topics and comments.
    - For text fields, combines values with semicolons if there are differences.

    Args:
        minutes_list (List[MeetingMinutes]): List of meeting minutes to merge.

    Returns:
        MeetingMinutes: A single combined meeting minutes object.
    """
    merged = {}
    for key in MeetingMinutes.model_fields.keys():
        if key in ["attendees", "agenda", "decisions", "attached_documents"]:
            union_set = set()
            for m in minutes_list:
                value = getattr(m, key)
                if value:
                    union_set.update(value)
            merged[key] = list(union_set) if union_set else None

        elif key == "discussion_content":
            merged_sub = {}
            for m in minutes_list:
                subdict = getattr(m, key)
                if subdict:
                    for subkey, sublist in subdict.items():
                        if subkey in merged_sub:
                            merged_sub[subkey].update(sublist)
                        else:
                            merged_sub[subkey] = set(sublist)
            merged[key] = {k: list(v) for k, v in merged_sub.items()} if merged_sub else None

        else:
            union_set = set()
            for m in minutes_list:
                value = getattr(m, key)
                if value:
                    union_set.add(value)
            if not union_set:
                merged[key] = None
            elif len(union_set) == 1:
                merged[key] = union_set.pop()
            else:
                merged[key] = "; ".join(sorted(union_set))
    return MeetingMinutes(**merged)


# Function to split a transcript text file into chunks
def read_transcript_in_chunks(file_path: str, chunk_size: int = 7, chunk_overlap: int = 0) -> List[str]:
    """
    Splits a transcript file into smaller text chunks based on line count.

    Args:
        file_path (str): Path to the transcript file.
        chunk_size (int): Number of lines per chunk.
        chunk_overlap (int): Number of overlapping lines between chunks.

    Returns:
        List[str]: List of text chunks.
    """
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size.")

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    chunks = []
    i = 0
    while i < len(lines):
        chunk = "".join(lines[i:i + chunk_size]).strip()
        if chunk:
            chunks.append(chunk)
        i += (chunk_size - chunk_overlap) if (chunk_size - chunk_overlap) > 0 else 1
    return chunks


# Function to process an entire transcript file and generate ful
