# ServiceNow Integration - Quick Start Guide

## 🚀 Quick Start (5 minutes)

### 1. Configuration
The ServiceNow credentials are already configured in [config.yml](../config.yml):

```yaml
SERVICENOW_INSTANCE_URL: https://dev322675.service-now.com
SERVICENOW_TABLE_NAME: x_1897466_colleg_0_college_repair
SERVICENOW_USERNAME: college_api_user
SERVICENOW_PASSWORD: "z:Dg6<*!i=.Q4@,_]Tpi?{?OR.ZIU^fPR"
```

### 2. Start the Backend
```bash
# From the project root
python -m Backend
```

The server will start at `http://localhost:8000`

### 3. Test the API

#### Option A: Use the Interactive CLI
```bash
# Install required package (first time only)
pip install rich

# Run the CLI
python servicenow_cli.py
```

#### Option B: Use the Example Scripts
```bash
python examples/servicenow_example.py
```

#### Option C: Use cURL
```bash
# Create a ticket
curl -X POST "http://localhost:8000/api/servicenow/tickets" \
  -H "Content-Type: application/json" \
  -d '{
    "student_name": "John Doe",
    "roll_number": "2021CS001",
    "room_number": "A-101",
    "contact_number": "+1234567890",
    "description": "WiFi is not working in my room"
  }'

# Check ticket status
curl "http://localhost:8000/api/servicenow/tickets/REP0001001/status"
```

#### Option D: Use the Swagger UI
Open http://localhost:8000/api/docs in your browser

## 📋 API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/servicenow/tickets` | Create a new repair ticket |
| GET | `/api/servicenow/tickets/{ticket_number}/status` | Get ticket status |
| POST | `/api/servicenow/tickets/status` | Get ticket status (POST method) |

## 🎯 Automatic Features

### Department Routing
Tickets are automatically routed based on keywords:

| Keywords | Department |
|----------|-----------|
| wifi, internet, speed | IT Department |
| light, bulb, wire, switch | Electronics Department |
| chair, door, handle, table, desk, bench | Furniture Department |
| others | General Maintenance |

### Priority Assignment
| Keywords | Impact | Urgency |
|----------|--------|---------|
| urgent, emergency | 1 (High) | 1 (High) |
| others | 2 (Medium) | 2 (Medium) |

## 💻 Code Examples

### Python
```python
import requests

# Create ticket
response = requests.post(
    "http://localhost:8000/api/servicenow/tickets",
    json={
        "student_name": "Jane Doe",
        "roll_number": "2021CS002",
        "room_number": "B-205",
        "contact_number": "+1234567891",
        "description": "urgent - light bulb broken"
    }
)

ticket = response.json()
print(f"Ticket created: {ticket['ticket_number']}")
print(f"Routed to: {ticket['assignment_group']}")
```

### JavaScript/Node.js
```javascript
const fetch = require('node-fetch');

// Create ticket
const response = await fetch('http://localhost:8000/api/servicenow/tickets', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    student_name: 'Jane Doe',
    roll_number: '2021CS002',
    room_number: 'B-205',
    contact_number: '+1234567891',
    description: 'urgent - light bulb broken'
  })
});

const ticket = await response.json();
console.log(`Ticket created: ${ticket.ticket_number}`);
console.log(`Routed to: ${ticket.assignment_group}`);
```

### Using the Service Directly in Your Code
```python
from Backend.services.servicenow.service import servicenow_service
from Backend.services.servicenow.schemas import TicketCreate

ticket_data = TicketCreate(
    student_name="John Doe",
    roll_number="2021CS001",
    room_number="A-101",
    contact_number="+1234567890",
    description="WiFi not working"
)

result = servicenow_service.create_ticket(ticket_data)
print(f"Ticket: {result.ticket_number}")
```

## 🧪 Testing

Run the test suite:
```bash
pytest tests/test_servicenow.py -v
```

## 📖 Full Documentation

For complete documentation, see [Backend/services/servicenow/README.md](../Backend/services/servicenow/README.md)

## 🔧 Troubleshooting

### Backend won't start
- Make sure all dependencies are installed: `pip install -e .`
- Check if port 8000 is available
- Verify database connection in config.yml

### API returns 502 Bad Gateway
- Check ServiceNow credentials in config.yml
- Verify ServiceNow instance is accessible
- Check network connectivity

### Department routing not working
- Keywords are case-insensitive
- Make sure the description contains relevant keywords
- Unknown keywords route to "General Maintenance"

## 🎓 Example Scenarios

### Scenario 1: Student WiFi Issue
```json
{
  "student_name": "Alice Johnson",
  "roll_number": "2021CS001",
  "room_number": "A-101",
  "contact_number": "+1234567890",
  "description": "The WiFi signal is very weak in my room"
}
```
**Result**: Routes to IT Department, Medium priority

### Scenario 2: Urgent Electrical Problem
```json
{
  "student_name": "Bob Smith",
  "roll_number": "2021CS002",
  "room_number": "B-205",
  "contact_number": "+1234567891",
  "description": "urgent - electrical switch is sparking"
}
```
**Result**: Routes to Electronics Department, High priority

### Scenario 3: Furniture Repair
```json
{
  "student_name": "Carol Williams",
  "roll_number": "2021CS003",
  "room_number": "C-310",
  "contact_number": "+1234567892",
  "description": "The desk drawer is stuck and won't open"
}
```
**Result**: Routes to Furniture Department, Medium priority

## 📞 Support

For issues or questions:
1. Check the full documentation in [Backend/services/servicenow/README.md](../Backend/services/servicenow/README.md)
2. Review the code examples in `examples/servicenow_example.py`
3. Test with the CLI tool: `python servicenow_cli.py`
4. Check API docs at http://localhost:8000/api/docs

## 🎉 You're Ready!

Your ServiceNow integration is complete and ready to use. Start creating tickets!
