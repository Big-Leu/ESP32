"""ServiceNow API client."""
import json
from typing import Dict, Any, Optional, List
import requests
from requests.auth import HTTPBasicAuth

from Backend.services.servicenow.config import servicenow_settings


class ServiceNowClient:
    """Client for interacting with ServiceNow API."""

    def __init__(self):
        """Initialize the ServiceNow client."""
        self.base_url = servicenow_settings.table_api_url
        self.auth = HTTPBasicAuth(
            servicenow_settings.username,
            servicenow_settings.password,
        )
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def create_ticket(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new ticket in ServiceNow.

        Args:
            payload: Ticket data

        Returns:
            Response data from ServiceNow

        Raises:
            requests.HTTPError: If the request fails
        """
        response = requests.post(
            self.base_url,
            auth=self.auth,
            headers=self.headers,
            data=json.dumps(payload),
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def get_ticket(self, ticket_number: str) -> Optional[Dict[str, Any]]:
        """
        Get ticket details by ticket number.

        Args:
            ticket_number: The ticket number to retrieve

        Returns:
            Ticket data if found, None otherwise

        Raises:
            requests.HTTPError: If the request fails
        """
        query = (
            f"?sysparm_query=number={ticket_number}"
            f"&sysparm_fields=state,short_description,comments,number"
            f"&sysparm_display_value=true"
        )
        url = self.base_url + query

        response = requests.get(
            url,
            auth=self.auth,
            headers={"Accept": "application/json"},
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()
        if "result" in data and len(data["result"]) > 0:
            return data["result"][0]
        return None

    def get_tickets_by_student(
        self,
        student_name: Optional[str] = None,
        roll_number: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get all tickets for a specific student.

        Args:
            student_name: Student name to filter by
            roll_number: Roll number to filter by

        Returns:
            List of ticket data

        Raises:
            requests.HTTPError: If the request fails
        """
        query_parts = []
        if student_name:
            query_parts.append(f"student_name={student_name}")
        if roll_number:
            query_parts.append(f"roll_number={roll_number}")

        query = "&".join(query_parts)
        url = (
            f"{self.base_url}?sysparm_query={query}"
            f"&sysparm_display_value=true"
        )

        response = requests.get(
            url,
            auth=self.auth,
            headers={"Accept": "application/json"},
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()
        return data.get("result", [])
