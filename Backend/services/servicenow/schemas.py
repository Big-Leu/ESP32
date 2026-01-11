"""ServiceNow schemas."""
from typing import Optional
from pydantic import BaseModel, Field


class TicketCreate(BaseModel):
    """Schema for creating a ticket."""

    student_name: str = Field(..., description="Name of the student")
    roll_number: str = Field(..., description="Roll number of the student")
    room_number: str = Field(..., description="Room number")
    contact_number: str = Field(..., description="Contact number")
    description: str = Field(..., description="Problem description")


class TicketResponse(BaseModel):
    """Schema for ticket response."""

    ticket_number: str = Field(..., description="Generated ticket number")
    assignment_group: str = Field(..., description="Assigned department")
    impact: str = Field(..., description="Impact level")
    urgency: str = Field(..., description="Urgency level")
    short_description: str = Field(..., description="Short description")


class TicketStatus(BaseModel):
    """Schema for ticket status."""

    ticket_number: str = Field(..., description="Ticket number")
    state: str = Field(..., description="Current state")
    short_description: str = Field(..., description="Problem description")
    latest_reply: Optional[str] = Field(
        None,
        description="Latest reply from authority",
    )


class PrioritySettings(BaseModel):
    """Priority settings for a ticket."""

    impact: str = Field(..., description="Impact level (1=high, 2=medium)")
    urgency: str = Field(..., description="Urgency level (1=high, 2=medium)")
