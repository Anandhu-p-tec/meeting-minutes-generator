from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class MeetingMinutes(BaseModel):
    meeting_date: Optional[str] = Field(
        None,
        description="The date the meeting was held, format: dd/mm/yyyy (e.g., 30/03/2025)"
    )
    meeting_time: Optional[str] = Field(
        None,
        description="The start and end time of the meeting. Example: '10:00 - 11:30'"
    )
    location: Optional[str] = Field(
        None,
        description="Location of the meeting. Can be a room, office, or online (e.g., 'Meeting Room A')"
    )
    host: Optional[str] = Field(
        None,
        description="Name of the person who chaired the meeting (e.g., 'John Smith')"
    )
    note_taker: Optional[str] = Field(
        None,
        description="Name of the person who took the meeting notes"
    )
    attendees: Optional[List[str]] = Field(
        None,
        description="List of attendees who participated in the meeting"
    )
    meeting_goal: Optional[str] = Field(
        None,
        description="A brief summary of the main goal of the meeting"
    )
    agenda: Optional[List[str]] = Field(
        None,
        description="List of main items or topics discussed during the meeting"
    )
    discussion_content: Optional[Dict[str, List[str]]] = Field(
        None,
        description="Detailed content discussed under each agenda topic. Format: {topic: [key points]}"
    )
    decisions: Optional[List[str]] = Field(
        None,
        description="List of official decisions made during the meeting"
    )
    conclusion: Optional[str] = Field(
        None,
        description="Summary of the conclusion and next steps after the meeting"
    )
    attached_documents: Optional[List[str]] = Field(
        None,
        description="List of documents that were attached or mentioned during the meeting"
    )
    notes: Optional[str] = Field(
        None,
        description="Additional notes, if any"
    )
