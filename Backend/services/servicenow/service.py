"""ServiceNow business logic service."""
from Backend.services.servicenow.client import ServiceNowClient
from Backend.services.servicenow.schemas import (
    TicketCreate,
    TicketResponse,
    TicketStatus,
    PrioritySettings,
)


class ServiceNowService:
    """Service for handling ServiceNow ticket operations."""

    def __init__(self):
        """Initialize the service."""
        self.client = ServiceNowClient()

    def determine_department(self, description: str) -> str:
        """
        Determine the department based on problem description.

        Args:
            description: Problem description

        Returns:
            Department name
        """
        description_lower = description.lower()

        if any(
            keyword in description_lower
            for keyword in ["wifi", "internet", "speed"]
        ):
            return "IT Department"

        if any(
            keyword in description_lower
            for keyword in ["light", "bulb", "wire", "switch"]
        ):
            return "Electronics Department"

        if any(
            keyword in description_lower
            for keyword in [
                "chair",
                "door",
                "door handle",
                "handle",
                "table",
                "desk",
                "bench",
            ]
        ):
            return "Furniture Department"

        return "General Maintenance"

    def calculate_priority(self, description: str) -> PrioritySettings:
        """
        Calculate priority based on problem description.

        Args:
            description: Problem description

        Returns:
            PrioritySettings with impact and urgency levels
        """
        description_lower = description.lower()

        if any(
            keyword in description_lower
            for keyword in ["urgent", "emergency"]
        ):
            return PrioritySettings(impact="1", urgency="1")

        return PrioritySettings(impact="2", urgency="2")

    def create_ticket(self, ticket_data: TicketCreate) -> TicketResponse:
        """
        Create a repair ticket with automated routing and priority.

        Args:
            ticket_data: Ticket creation data

        Returns:
            TicketResponse with created ticket details

        Raises:
            requests.HTTPError: If the API call fails
        """
        # Determine department and priority using business logic
        assigned_group = self.determine_department(ticket_data.description)
        priority_settings = self.calculate_priority(ticket_data.description)

        # Prepare payload for ServiceNow
        payload = {
            "student_name": ticket_data.student_name,
            "roll_number": ticket_data.roll_number,
            "room_number": ticket_data.room_number,
            "contact_number": ticket_data.contact_number,
            "short_description": (
                f"Repair Request from {ticket_data.student_name} "
                f"(Room {ticket_data.room_number})"
            ),
            "description": ticket_data.description,
            "assignment_group": assigned_group,
            "impact": priority_settings.impact,
            "urgency": priority_settings.urgency,
        }

        # Create ticket via API
        response_data = self.client.create_ticket(payload)

        # Extract and return relevant information
        result = response_data.get("result", {})
        return TicketResponse(
            ticket_number=result.get("number", ""),
            assignment_group=assigned_group,
            impact=priority_settings.impact,
            urgency=priority_settings.urgency,
            short_description=payload["short_description"],
        )

    def get_ticket_status(self, ticket_number: str) -> TicketStatus:
        """
        Get the status of a ticket.

        Args:
            ticket_number: Ticket number to check

        Returns:
            TicketStatus with current ticket information

        Raises:
            ValueError: If ticket not found
            requests.HTTPError: If the API call fails
        """
        ticket_data = self.client.get_ticket(ticket_number)

        if not ticket_data:
            raise ValueError(f"Ticket {ticket_number} not found")

        return TicketStatus(
            ticket_number=ticket_number,
            state=ticket_data.get("state", "Unknown"),
            short_description=ticket_data.get(
                "short_description",
                "No description",
            ),
            latest_reply=ticket_data.get("comments") or None,
        )


# Singleton instance
servicenow_service = ServiceNowService()
