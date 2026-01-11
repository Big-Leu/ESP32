# ServiceNow Integration Module

This module provides complete ServiceNow integration for managing college repair tickets through a FastAPI backend.

## 🏗️ Architecture

```
Backend/
├── services/servicenow/
│   ├── __init__.py
│   ├── config.py          # Configuration settings
│   ├── client.py          # ServiceNow API client
│   ├── schemas.py         # Data models
│   └── service.py         # Business logic layer
│
└── web/api/servicenow/
    ├── __init__.py
    ├── schema.py          # API request/response schemas
    └── views.py           # FastAPI endpoints
```

## ✨ Features

### 🎯 Automatic Routing
Tickets are automatically routed to the appropriate department based on keywords:
- **IT Department**: wifi, internet, speed
- **Electronics Department**: light, bulb, wire, switch
- **Furniture Department**: chair, door, handle, table, desk, bench
- **General Maintenance**: everything else

### ⚡ Priority Calculation
Automatic priority assignment based on urgency:
- **High Priority** (Impact=1, Urgency=1): urgent, emergency
- **Medium Priority** (Impact=2, Urgency=2): everything else

## 🚀 API Endpoints

### 1. Create Ticket
```http
POST /api/servicenow/tickets
Content-Type: application/json

{
  "student_name": "John Doe",
  "roll_number": "2021CS001",
  "room_number": "A-101",
  "contact_number": "+1234567890",
  "description": "The WiFi is not working in my room"
}
```

**Response:**
```json
{
  "success": true,
  "ticket_number": "REP0001001",
  "assignment_group": "IT Department",
  "impact": "2",
  "urgency": "2",
  "message": "Ticket created successfully and routed to IT Department"
}
```

### 2. Check Ticket Status (GET)
```http
GET /api/servicenow/tickets/{ticket_number}/status
```

**Response:**
```json
{
  "success": true,
  "ticket_number": "REP0001001",
  "state": "New",
  "short_description": "Repair Request from John Doe (Room A-101)",
  "latest_reply": "No reply from authority yet"
}
```

### 3. Check Ticket Status (POST)
```http
POST /api/servicenow/tickets/status
Content-Type: application/json

{
  "ticket_number": "REP0001001"
}
```

## ⚙️ Configuration

### Environment Variables
Add to `config.yml`:

```yaml
# ServiceNow Configuration
SERVICENOW_INSTANCE_URL: https://dev322675.service-now.com
SERVICENOW_TABLE_NAME: x_1897466_colleg_0_college_repair
SERVICENOW_USERNAME: college_api_user
SERVICENOW_PASSWORD: "z:Dg6<*!i=.Q4@,_]Tpi?{?OR.ZIU^fPR"
```

Or use environment variables:
```bash
export SERVICENOW_INSTANCE_URL="https://dev322675.service-now.com"
export SERVICENOW_TABLE_NAME="x_1897466_colleg_0_college_repair"
export SERVICENOW_USERNAME="college_api_user"
export SERVICENOW_PASSWORD="your-password"
```

## 🧪 Testing

### Using the CLI Tool
A command-line interface is provided for easy testing:

```bash
# Install required package
pip install rich

# Run the CLI
python servicenow_cli.py

# Or specify custom backend URL
python servicenow_cli.py http://localhost:8000
```

### Using cURL

**Create a ticket:**
```bash
curl -X POST "http://localhost:8000/api/servicenow/tickets" \
  -H "Content-Type: application/json" \
  -d '{
    "student_name": "John Doe",
    "roll_number": "2021CS001",
    "room_number": "A-101",
    "contact_number": "+1234567890",
    "description": "urgent wifi problem in my room"
  }'
```

**Check ticket status:**
```bash
curl "http://localhost:8000/api/servicenow/tickets/REP0001001/status"
```

### Using Python Requests

```python
import requests

# Create ticket
response = requests.post(
    "http://localhost:8000/api/servicenow/tickets",
    json={
        "student_name": "Jane Smith",
        "roll_number": "2021CS002",
        "room_number": "B-205",
        "contact_number": "+1234567891",
        "description": "The light bulb in my room is broken"
    }
)
print(response.json())

# Check status
ticket_number = response.json()["ticket_number"]
status = requests.get(
    f"http://localhost:8000/api/servicenow/tickets/{ticket_number}/status"
)
print(status.json())
```

## 📚 API Documentation

Once your server is running, visit:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## 🔧 Usage in Code

### Direct Service Usage

```python
from Backend.services.servicenow.service import servicenow_service
from Backend.services.servicenow.schemas import TicketCreate

# Create a ticket
ticket_data = TicketCreate(
    student_name="John Doe",
    roll_number="2021CS001",
    room_number="A-101",
    contact_number="+1234567890",
    description="The WiFi is not working"
)

result = servicenow_service.create_ticket(ticket_data)
print(f"Ticket created: {result.ticket_number}")
print(f"Routed to: {result.assignment_group}")

# Check status
status = servicenow_service.get_ticket_status(result.ticket_number)
print(f"Current state: {status.state}")
```

### Using the Client Directly

```python
from Backend.services.servicenow.client import ServiceNowClient

client = ServiceNowClient()

# Create ticket with custom payload
payload = {
    "student_name": "Jane Smith",
    "roll_number": "2021CS002",
    "room_number": "B-205",
    "contact_number": "+1234567891",
    "description": "Broken door handle",
    "assignment_group": "Furniture Department",
    "impact": "2",
    "urgency": "2"
}

response = client.create_ticket(payload)
print(response)

# Get ticket details
ticket = client.get_ticket("REP0001001")
print(ticket)
```

## 🎯 Department Routing Logic

The system uses keyword matching to determine the appropriate department:

```python
# IT Department keywords
["wifi", "internet", "speed"]

# Electronics Department keywords
["light", "bulb", "wire", "switch"]

# Furniture Department keywords
["chair", "door", "door handle", "handle", "table", "desk", "bench"]
```

To add more keywords or departments, modify the `determine_department` method in [Backend/services/servicenow/service.py](Backend/services/servicenow/service.py).

## 🔐 Security Notes

1. **Credentials**: Store credentials in environment variables or secure configuration files
2. **HTTPS**: Always use HTTPS in production
3. **Authentication**: Consider adding API authentication to your endpoints
4. **Input Validation**: All inputs are validated using Pydantic schemas

## 🐛 Error Handling

The API returns appropriate HTTP status codes:
- `201`: Ticket created successfully
- `404`: Ticket not found
- `502`: ServiceNow API error
- `500`: Internal server error

Example error response:
```json
{
  "detail": "Ticket REP0001999 not found"
}
```

## 📈 Next Steps

1. **Add Authentication**: Implement JWT or API key authentication
2. **Add Webhooks**: Receive notifications when tickets are updated
3. **Add Filtering**: List tickets by student, department, or status
4. **Add Comments**: Allow adding comments to existing tickets
5. **Add Attachments**: Support file uploads for evidence

## 🤝 Contributing

To extend the module:

1. **Add new endpoints**: Update [Backend/web/api/servicenow/views.py](Backend/web/api/servicenow/views.py)
2. **Add business logic**: Update [Backend/services/servicenow/service.py](Backend/services/servicenow/service.py)
3. **Add client methods**: Update [Backend/services/servicenow/client.py](Backend/services/servicenow/client.py)
4. **Add schemas**: Update schema files as needed

## 📝 License

Part of the ESP32 Backend project.
