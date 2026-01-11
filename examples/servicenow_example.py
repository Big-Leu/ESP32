"""
ServiceNow Integration Example Script

This script demonstrates how to use the ServiceNow API without the CLI.
Run this after starting your FastAPI backend.
"""
import requests
import json
from typing import Dict, Any


class ServiceNowAPIExample:
    """Example usage of ServiceNow API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize with backend URL."""
        self.api_url = f"{base_url}/api/servicenow"

    def create_ticket(
        self,
        student_name: str,
        roll_number: str,
        room_number: str,
        contact_number: str,
        description: str,
    ) -> Dict[str, Any]:
        """
        Create a new repair ticket.

        Args:
            student_name: Name of the student
            roll_number: Roll number
            room_number: Room number
            contact_number: Contact number
            description: Problem description

        Returns:
            API response data
        """
        payload = {
            "student_name": student_name,
            "roll_number": roll_number,
            "room_number": room_number,
            "contact_number": contact_number,
            "description": description,
        }

        print(f"\n📤 Creating ticket for {student_name}...")
        print(f"   Description: {description}")

        response = requests.post(
            f"{self.api_url}/tickets",
            json=payload,
            timeout=30,
        )

        if response.status_code == 201:
            data = response.json()
            print(f"\n✅ SUCCESS!")
            print(f"   Ticket Number: {data['ticket_number']}")
            print(f"   Assigned to: {data['assignment_group']}")
            print(f"   Priority: Impact={data['impact']}, Urgency={data['urgency']}")
            return data
        else:
            print(f"\n❌ ERROR: {response.status_code}")
            print(f"   {response.text}")
            response.raise_for_status()

    def check_status(self, ticket_number: str) -> Dict[str, Any]:
        """
        Check the status of a ticket.

        Args:
            ticket_number: The ticket number to check

        Returns:
            Ticket status data
        """
        print(f"\n🔍 Checking status for ticket {ticket_number}...")

        response = requests.get(
            f"{self.api_url}/tickets/{ticket_number}/status",
            timeout=30,
        )

        if response.status_code == 200:
            data = response.json()
            print(f"\n📋 TICKET STATUS:")
            print(f"   Number: {data['ticket_number']}")
            print(f"   State: {data['state']}")
            print(f"   Description: {data['short_description']}")
            print(f"   Latest Reply: {data['latest_reply']}")
            return data
        else:
            print(f"\n❌ ERROR: {response.status_code}")
            print(f"   {response.text}")
            response.raise_for_status()


def example_wifi_issue():
    """Example: WiFi problem (should route to IT Department)."""
    api = ServiceNowAPIExample()

    print("\n" + "=" * 60)
    print("EXAMPLE 1: WiFi Issue")
    print("=" * 60)

    ticket = api.create_ticket(
        student_name="Alice Johnson",
        roll_number="2021CS001",
        room_number="A-101",
        contact_number="+1234567890",
        description="The WiFi connection is very slow in my room",
    )

    # Check status
    api.check_status(ticket["ticket_number"])


def example_urgent_light_issue():
    """Example: Urgent light problem (should be high priority)."""
    api = ServiceNowAPIExample()

    print("\n" + "=" * 60)
    print("EXAMPLE 2: Urgent Light Issue")
    print("=" * 60)

    ticket = api.create_ticket(
        student_name="Bob Smith",
        roll_number="2021CS002",
        room_number="B-205",
        contact_number="+1234567891",
        description="urgent - all lights in my room stopped working",
    )

    api.check_status(ticket["ticket_number"])


def example_furniture_issue():
    """Example: Furniture problem."""
    api = ServiceNowAPIExample()

    print("\n" + "=" * 60)
    print("EXAMPLE 3: Furniture Issue")
    print("=" * 60)

    ticket = api.create_ticket(
        student_name="Carol Williams",
        roll_number="2021CS003",
        room_number="C-310",
        contact_number="+1234567892",
        description="The chair in my room is broken and wobbly",
    )

    api.check_status(ticket["ticket_number"])


def example_custom_ticket():
    """Create a custom ticket with user input."""
    api = ServiceNowAPIExample()

    print("\n" + "=" * 60)
    print("EXAMPLE 4: Custom Ticket")
    print("=" * 60)

    ticket = api.create_ticket(
        student_name="David Brown",
        roll_number="2021CS004",
        room_number="D-405",
        contact_number="+1234567893",
        description="emergency - door lock is completely broken, cannot secure room",
    )

    api.check_status(ticket["ticket_number"])


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("ServiceNow API Integration Examples")
    print("=" * 60)
    print("\n⚠️  Make sure your FastAPI backend is running!")
    print("   Start it with: python -m Backend")
    print()

    try:
        # Test connection
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running!\n")
        else:
            print("⚠️  Backend returned unexpected status\n")
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to backend at http://localhost:8000")
        print("   Please start the backend first!\n")
        return

    # Run examples
    try:
        example_wifi_issue()
        input("\nPress Enter to continue to next example...")

        example_urgent_light_issue()
        input("\nPress Enter to continue to next example...")

        example_furniture_issue()
        input("\nPress Enter to continue to next example...")

        example_custom_ticket()

        print("\n" + "=" * 60)
        print("All examples completed!")
        print("=" * 60)
        print("\n📚 Check the API documentation at:")
        print("   http://localhost:8000/api/docs\n")

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user\n")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")


if __name__ == "__main__":
    main()
