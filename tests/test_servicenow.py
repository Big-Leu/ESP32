"""Tests for ServiceNow integration."""
import pytest
from unittest.mock import Mock, patch
from Backend.services.servicenow.service import ServiceNowService
from Backend.services.servicenow.schemas import TicketCreate, PrioritySettings


class TestServiceNowService:
    """Test ServiceNow service functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = ServiceNowService()

    def test_determine_department_it(self):
        """Test IT department detection."""
        assert self.service.determine_department("wifi not working") == "IT Department"
        assert self.service.determine_department("slow internet speed") == "IT Department"
        assert self.service.determine_department("Internet connection problem") == "IT Department"

    def test_determine_department_electronics(self):
        """Test Electronics department detection."""
        assert self.service.determine_department("light bulb is broken") == "Electronics Department"
        assert self.service.determine_department("electrical wire issue") == "Electronics Department"
        assert self.service.determine_department("switch not working") == "Electronics Department"

    def test_determine_department_furniture(self):
        """Test Furniture department detection."""
        assert self.service.determine_department("broken chair") == "Furniture Department"
        assert self.service.determine_department("door handle broken") == "Furniture Department"
        assert self.service.determine_department("table leg is loose") == "Furniture Department"

    def test_determine_department_general(self):
        """Test general maintenance for unknown issues."""
        assert self.service.determine_department("paint is peeling") == "General Maintenance"
        assert self.service.determine_department("water leak") == "General Maintenance"

    def test_calculate_priority_high(self):
        """Test high priority calculation."""
        priority = self.service.calculate_priority("urgent wifi problem")
        assert priority.impact == "1"
        assert priority.urgency == "1"

        priority = self.service.calculate_priority("emergency light failure")
        assert priority.impact == "1"
        assert priority.urgency == "1"

    def test_calculate_priority_medium(self):
        """Test medium priority calculation."""
        priority = self.service.calculate_priority("chair is wobbly")
        assert priority.impact == "2"
        assert priority.urgency == "2"

    @patch('Backend.services.servicenow.service.ServiceNowClient')
    def test_create_ticket(self, mock_client_class):
        """Test ticket creation."""
        # Mock the client
        mock_client = Mock()
        mock_client.create_ticket.return_value = {
            "result": {
                "number": "REP0001001",
                "assignment_group": "IT Department"
            }
        }
        mock_client_class.return_value = mock_client

        # Create service with mocked client
        service = ServiceNowService()
        service.client = mock_client

        # Create ticket
        ticket_data = TicketCreate(
            student_name="John Doe",
            roll_number="2021CS001",
            room_number="A-101",
            contact_number="+1234567890",
            description="urgent wifi not working"
        )

        result = service.create_ticket(ticket_data)

        # Verify
        assert result.ticket_number == "REP0001001"
        assert result.assignment_group == "IT Department"
        assert result.impact == "1"  # Should be high priority due to "urgent"
        assert result.urgency == "1"

        # Verify client was called
        mock_client.create_ticket.assert_called_once()

    @patch('Backend.services.servicenow.service.ServiceNowClient')
    def test_get_ticket_status(self, mock_client_class):
        """Test getting ticket status."""
        # Mock the client
        mock_client = Mock()
        mock_client.get_ticket.return_value = {
            "number": "REP0001001",
            "state": "In Progress",
            "short_description": "WiFi repair",
            "comments": "Technician assigned"
        }
        mock_client_class.return_value = mock_client

        # Create service with mocked client
        service = ServiceNowService()
        service.client = mock_client

        # Get status
        status = service.get_ticket_status("REP0001001")

        # Verify
        assert status.ticket_number == "REP0001001"
        assert status.state == "In Progress"
        assert status.short_description == "WiFi repair"
        assert status.latest_reply == "Technician assigned"

        # Verify client was called
        mock_client.get_ticket.assert_called_once_with("REP0001001")

    @patch('Backend.services.servicenow.service.ServiceNowClient')
    def test_get_ticket_status_not_found(self, mock_client_class):
        """Test getting status of non-existent ticket."""
        # Mock the client
        mock_client = Mock()
        mock_client.get_ticket.return_value = None
        mock_client_class.return_value = mock_client

        # Create service with mocked client
        service = ServiceNowService()
        service.client = mock_client

        # Should raise ValueError
        with pytest.raises(ValueError, match="not found"):
            service.get_ticket_status("INVALID999")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
