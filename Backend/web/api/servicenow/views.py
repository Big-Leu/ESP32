"""ServiceNow API views."""
from fastapi import APIRouter, HTTPException, status
from requests.exceptions import HTTPError

from Backend.services.servicenow.service import servicenow_service
from Backend.services.servicenow.schemas import TicketCreate
from Backend.web.api.servicenow.schema import (
    TicketCreateRequest,
    TicketCreateResponse,
    TicketStatusRequest,
    TicketStatusResponse,
)

router = APIRouter()


@router.post(
    "/tickets",
    response_model=TicketCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a repair ticket",
    description=(
        "Submit a new repair request that will be automatically "
        "routed to the appropriate department"
    ),
)
async def create_ticket(request: TicketCreateRequest) -> TicketCreateResponse:
    """
    Create a new repair ticket.

    The ticket will be automatically:
    - Routed to the appropriate department based on the description
    - Assigned a priority level based on urgency keywords
    """
    try:
        # Convert request to service schema
        ticket_data = TicketCreate(
            student_name=request.student_name,
            roll_number=request.roll_number,
            room_number=request.room_number,
            contact_number=request.contact_number,
            description=request.description,
        )

        # Create ticket
        ticket_response = servicenow_service.create_ticket(ticket_data)

        return TicketCreateResponse(
            success=True,
            ticket_number=ticket_response.ticket_number,
            assignment_group=ticket_response.assignment_group,
            impact=ticket_response.impact,
            urgency=ticket_response.urgency,
            message=(
                f"Ticket created successfully and routed to "
                f"{ticket_response.assignment_group}"
            ),
        )

    except HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"ServiceNow API error: {str(e)}",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create ticket: {str(e)}",
        ) from e


@router.get(
    "/tickets/{ticket_number}/status",
    response_model=TicketStatusResponse,
    summary="Check ticket status",
    description=(
        "Get the current status of a repair ticket by ticket number"
    ),
)
async def get_ticket_status(ticket_number: str) -> TicketStatusResponse:
    """
    Check the status of a repair ticket.

    Returns current state, description, and any replies from the
    maintenance team.
    """
    try:
        ticket_status = servicenow_service.get_ticket_status(ticket_number)

        return TicketStatusResponse(
            success=True,
            ticket_number=ticket_status.ticket_number,
            state=ticket_status.state,
            short_description=ticket_status.short_description,
            latest_reply=ticket_status.latest_reply
            or "No reply from authority yet",
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"ServiceNow API error: {str(e)}",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get ticket status: {str(e)}",
        ) from e


@router.post(
    "/tickets/status",
    response_model=TicketStatusResponse,
    summary="Check ticket status (POST)",
    description=(
        "Get the current status of a repair ticket by ticket number "
        "using POST method"
    ),
)
async def check_ticket_status(
    request: TicketStatusRequest,
) -> TicketStatusResponse:
    """
    Check the status of a repair ticket using POST method.

    Alternative endpoint for checking status when GET is not preferred.
    """
    return await get_ticket_status(request.ticket_number)
