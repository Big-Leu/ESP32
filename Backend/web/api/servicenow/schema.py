"""ServiceNow API request/response schemas."""
from pydantic import BaseModel, Field


class TicketCreateRequest(BaseModel):
    """Request schema for creating a ticket."""

    student_name: str = Field(description="Student name")
    roll_number: str = Field(description="Roll number")
    room_number: str = Field(description="Room number")
    contact_number: str = Field(description="Contact number")
    description: str = Field(description="Problem description")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "student_name": "John Doe",
                    "roll_number": "2021CS001",
                    "room_number": "A-101",
                    "contact_number": "+1234567890",
                    "description": "The WiFi is not working in my room",
                }
            ]
        }
    }


class TicketCreateResponse(BaseModel):
    """Response schema after creating a ticket."""

    success: bool
    ticket_number: str
    assignment_group: str
    impact: str
    urgency: str
    message: str


class TicketStatusRequest(BaseModel):
    """Request schema for checking ticket status."""

    ticket_number: str = Field(description="Ticket number")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"ticket_number": "REP0001001"}
            ]
        }
    }


class TicketStatusResponse(BaseModel):
    """Response schema for ticket status."""

    success: bool
    ticket_number: str
    state: str
    short_description: str
    latest_reply: str | None = None
