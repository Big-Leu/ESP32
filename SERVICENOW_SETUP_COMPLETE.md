# ServiceNow Integration - Complete Setup Summary

## ✅ What Was Created

### 1. Service Layer (`Backend/services/servicenow/`)
- **config.py** - Configuration management with environment variable support
- **client.py** - ServiceNow REST API client for ticket operations
- **schemas.py** - Pydantic data models for type safety
- **service.py** - Business logic with automatic routing and priority assignment
- **README.md** - Comprehensive documentation

### 2. API Layer (`Backend/web/api/servicenow/`)
- **views.py** - FastAPI endpoints for ticket creation and status checking
- **schema.py** - API request/response schemas
- **__init__.py** - Router export

### 3. Configuration Files
- **config.yml** - Updated with ServiceNow credentials
- **Backend/settings.py** - Added ServiceNow settings to main config
- **Backend/web/api/router.py** - Registered ServiceNow routes

### 4. Tools & Examples
- **servicenow_cli.py** - Interactive CLI for testing
- **examples/servicenow_example.py** - Code examples and demonstrations
- **tests/test_servicenow.py** - Unit tests
- **SERVICENOW_QUICKSTART.md** - Quick start guide

## 🎯 Features Implemented

### Automatic Department Routing
The system automatically routes tickets based on keywords in the description:

```python
# Keywords -> Department mapping
{
    "wifi, internet, speed": "IT Department",
    "light, bulb, wire, switch": "Electronics Department",
    "chair, door, handle, table, desk, bench": "Furniture Department",
    "others": "General Maintenance"
}
```

### Automatic Priority Assignment
Priority is calculated based on urgency keywords:

```python
# Urgent keywords trigger high priority
"urgent, emergency" -> Impact=1, Urgency=1

# All other issues get medium priority
"others" -> Impact=2, Urgency=2
```

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/servicenow/tickets` | Create new ticket |
| GET | `/api/servicenow/tickets/{ticket_number}/status` | Get ticket status |
| POST | `/api/servicenow/tickets/status` | Get ticket status (POST) |

## 🚀 How to Use

### 1. Start the Backend
```bash
python -m Backend
```

### 2. Test with CLI
```bash
pip install rich  # First time only
python servicenow_cli.py
```

### 3. Test with Examples
```bash
python examples/servicenow_example.py
```

### 4. Use in Code
```python
import requests

response = requests.post(
    "http://localhost:8000/api/servicenow/tickets",
    json={
        "student_name": "John Doe",
        "roll_number": "2021CS001",
        "room_number": "A-101",
        "contact_number": "+1234567890",
        "description": "WiFi is not working"
    }
)

ticket = response.json()
print(f"Ticket: {ticket['ticket_number']}")
print(f"Routed to: {ticket['assignment_group']}")
```

## 🔧 Configuration

### ServiceNow Credentials
Located in `config.yml`:

```yaml
SERVICENOW_INSTANCE_URL: https://dev322675.service-now.com
SERVICENOW_TABLE_NAME: x_1897466_colleg_0_college_repair
SERVICENOW_USERNAME: college_api_user
SERVICENOW_PASSWORD: "z:Dg6<*!i=.Q4@,_]Tpi?{?OR.ZIU^fPR"
```

### Environment Variables
You can also use environment variables:

```bash
export SERVICENOW_INSTANCE_URL="https://dev322675.service-now.com"
export SERVICENOW_TABLE_NAME="x_1897466_colleg_0_college_repair"
export SERVICENOW_USERNAME="college_api_user"
export SERVICENOW_PASSWORD="your-password"
```

## 📂 Project Structure

```
ESP32/
├── Backend/
│   ├── services/
│   │   └── servicenow/
│   │       ├── __init__.py
│   │       ├── client.py          # API client
│   │       ├── config.py          # Configuration
│   │       ├── schemas.py         # Data models
│   │       ├── service.py         # Business logic
│   │       └── README.md
│   ├── web/
│   │   └── api/
│   │       ├── router.py          # Updated with servicenow routes
│   │       └── servicenow/
│   │           ├── __init__.py
│   │           ├── schema.py      # API schemas
│   │           └── views.py       # API endpoints
│   └── settings.py                # Updated with servicenow settings
├── tests/
│   └── test_servicenow.py         # Unit tests
├── examples/
│   └── servicenow_example.py      # Usage examples
├── servicenow_cli.py              # CLI tool
├── config.yml                     # Updated with credentials
└── SERVICENOW_QUICKSTART.md       # Quick start guide
```

## 🧪 Testing

### Run Unit Tests
```bash
pytest tests/test_servicenow.py -v
```

### Test Coverage
- Department routing logic
- Priority calculation
- Ticket creation
- Status retrieval
- Error handling

## 📚 Documentation

- **Quick Start**: [SERVICENOW_QUICKSTART.md](SERVICENOW_QUICKSTART.md)
- **Full Documentation**: [Backend/services/servicenow/README.md](Backend/services/servicenow/README.md)
- **API Docs**: http://localhost:8000/api/docs (when server is running)

## ✨ Example Usage Scenarios

### Scenario 1: WiFi Issue
```json
{
  "student_name": "Alice",
  "roll_number": "2021CS001",
  "room_number": "A-101",
  "contact_number": "+1234567890",
  "description": "WiFi is very slow"
}
```
**→ Routes to IT Department, Medium Priority**

### Scenario 2: Urgent Electrical
```json
{
  "student_name": "Bob",
  "roll_number": "2021CS002",
  "room_number": "B-205",
  "contact_number": "+1234567891",
  "description": "urgent - light switch sparking"
}
```
**→ Routes to Electronics Department, High Priority**

### Scenario 3: Furniture Repair
```json
{
  "student_name": "Carol",
  "roll_number": "2021CS003",
  "room_number": "C-310",
  "contact_number": "+1234567892",
  "description": "broken chair leg"
}
```
**→ Routes to Furniture Department, Medium Priority**

## 🔐 Security Features

- ✅ Environment variable support for credentials
- ✅ Pydantic validation for all inputs
- ✅ HTTP timeout configuration
- ✅ Proper error handling
- ✅ Type safety with Pydantic models

## 🎉 Ready to Use!

Your ServiceNow integration is fully configured and ready to use. All endpoints are documented and tested.

### Quick Test
```bash
# Start backend
python -m Backend

# In another terminal, test with CLI
python servicenow_cli.py

# Or run examples
python examples/servicenow_example.py
```

### API Documentation
Visit http://localhost:8000/api/docs for interactive API documentation.

---

**Need Help?**
- Check [SERVICENOW_QUICKSTART.md](SERVICENOW_QUICKSTART.md) for quick start
- See [Backend/services/servicenow/README.md](Backend/services/servicenow/README.md) for details
- Run examples: `python examples/servicenow_example.py`
- Use the CLI: `python servicenow_cli.py`
