"""ServiceNow CLI tool for testing ticket operations."""
import asyncio
import sys
from typing import Optional

import requests
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()


class ServiceNowCLI:
    """CLI interface for ServiceNow operations."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the CLI."""
        self.base_url = base_url
        self.api_url = f"{base_url}/api/servicenow"

    def create_ticket(self) -> None:
        """Interactive ticket creation."""
        console.print("\n[bold cyan]🎫 Create New Repair Ticket[/bold cyan]\n")

        student_name = Prompt.ask("Student Name")
        roll_number = Prompt.ask("Roll Number")
        room_number = Prompt.ask("Room Number")
        contact_number = Prompt.ask("Contact Number")
        description = Prompt.ask("Describe the problem")

        console.print("\n[yellow]>>> Processing ticket...[/yellow]")

        payload = {
            "student_name": student_name,
            "roll_number": roll_number,
            "room_number": room_number,
            "contact_number": contact_number,
            "description": description,
        }

        try:
            response = requests.post(
                f"{self.api_url}/tickets",
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            console.print(
                Panel(
                    f"""[green]✓ SUCCESS![/green]

[bold]Ticket Number:[/bold] {data['ticket_number']}
[bold]Routed to:[/bold] {data['assignment_group']}
[bold]Priority:[/bold] Impact={data['impact']}, Urgency={data['urgency']}

{data['message']}""",
                    title="Ticket Created",
                    border_style="green",
                ),
            )

        except requests.exceptions.HTTPError as e:
            console.print(f"[red]✗ Error: {e.response.text}[/red]")
        except Exception as e:
            console.print(f"[red]✗ Error: {str(e)}[/red]")

    def check_status(self) -> None:
        """Check ticket status."""
        console.print("\n[bold cyan]🔍 Check Ticket Status[/bold cyan]\n")

        ticket_number = Prompt.ask("Enter Ticket Number")

        try:
            response = requests.get(
                f"{self.api_url}/tickets/{ticket_number}/status",
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            latest_reply = data.get("latest_reply", "No reply yet")
            if latest_reply == "No reply from authority yet":
                latest_reply = "[dim](No reply from authority yet)[/dim]"

            console.print(
                Panel(
                    f"""[bold]Ticket:[/bold] {data['ticket_number']}
[bold]State:[/bold] {data['state']}
[bold]Problem:[/bold] {data['short_description']}
[bold]Latest Reply:[/bold] {latest_reply}""",
                    title=f"Status for {ticket_number}",
                    border_style="cyan",
                ),
            )

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                console.print(
                    f"[red]✗ Ticket '{ticket_number}' not found. Please check the number.[/red]",
                )
            else:
                console.print(f"[red]✗ Error: {e.response.text}[/red]")
        except Exception as e:
            console.print(f"[red]✗ Error: {str(e)}[/red]")

    def run(self) -> None:
        """Run the CLI application."""
        console.print(
            Panel(
                "[bold cyan]ServiceNow College Repair Management[/bold cyan]",
                border_style="cyan",
            ),
        )

        while True:
            console.print("\n[bold]Options:[/bold]")
            console.print("1. Create new ticket")
            console.print("2. Check ticket status")
            console.print("3. Exit")

            choice = Prompt.ask("\nSelect option", choices=["1", "2", "3"])

            if choice == "1":
                self.create_ticket()
            elif choice == "2":
                self.check_status()
            elif choice == "3":
                console.print("\n[yellow]Goodbye! 👋[/yellow]\n")
                break


def main() -> None:
    """Main entry point."""
    base_url = "http://localhost:8000"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]

    cli = ServiceNowCLI(base_url)
    try:
        cli.run()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Interrupted. Goodbye! 👋[/yellow]\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
