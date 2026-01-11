# Migration Guide: From Original Script to API Module

This guide helps you migrate from the standalone script to the new FastAPI module.

## 🔄 What Changed?

### Before (Original Script)
```python
# Procedural script with hardcoded credentials
def raise_ticket_pipeline():
    student_name = input("Student Name : ")
    roll_number = input("Roll Number : ")
    # ... manual input collection
    
    payload = {...}
    response = requests.post(url, auth=(admin_user, admin_pass), ...)
```

### After (New Module)
```python
# Service-oriented architecture with configuration
from Backend.services.servicenow.service import servicenow_service
from Backend.services.servicenow.schemas import TicketCreate

ticket = TicketCreate(
    student_name="John Doe",
    roll_number="2021CS001",
    room_number="A-101",
    contact_number="+1234567890",
    description="WiFi not working"
)

result = servicenow_service.create_ticket(ticket)
```

## 📋 Feature Comparison

| Feature | Original Script | New Module |
|---------|----------------|------------|
| Interface | CLI with input() | REST API + CLI |
| Configuration | Hardcoded | config.yml + env vars |
| Error Handling | Basic print | Proper exceptions + HTTP codes |
| Testing | Manual | Unit tests + examples |
| Documentation | None | Full docs + Swagger UI |
| Integration | Standalone | Part of FastAPI backend |
| Type Safety | None | Pydantic validation |
| Async Support | No | Yes (FastAPI) |

## 🔄 Function Mapping

### Original Functions → New Modules

#### 1. `determine_department()`
**Before:**
```python
def determine_department(description):
    description_lower = description.lower()
    if any(i in description_lower for i in ['wifi','internet','speed']):
        return "IT Department"
    # ...
```

**After:**
```python
# In Backend/services/servicenow/service.py
def determine_department(self, description: str) -> str:
    description_lower = description.lower()
    if any(keyword in description_lower 
           for keyword in ["wifi", "internet", "speed"]):
        return "IT Department"
    # ...
```

**Usage:**
```python
from Backend.services.servicenow.service import servicenow_service

department = servicenow_service.determine_department("wifi is slow")
# Returns: "IT Department"
```

#### 2. `calculate_priority()`
**Before:**
```python
def calculate_priority(description):
    description_lower = description.lower()
    if any(i in description_lower for i in ['urgent','emergency']):
        return {"impact":"1", "urgency":"1"}
    else:
        return {"impact":"2", "urgency":"2"}
```

**After:**
```python
# In Backend/services/servicenow/service.py
def calculate_priority(self, description: str) -> PrioritySettings:
    description_lower = description.lower()
    if any(keyword in description_lower 
           for keyword in ["urgent", "emergency"]):
        return PrioritySettings(impact="1", urgency="1")
    return PrioritySettings(impact="2", urgency="2")
```

**Usage:**
```python
from Backend.services.servicenow.service import servicenow_service

priority = servicenow_service.calculate_priority("urgent wifi issue")
# Returns: PrioritySettings(impact="1", urgency="1")
```

#### 3. `raise_ticket_pipeline()`
**Before:**
```python
def raise_ticket_pipeline():
    student_name = input("Student Name : ")
    # ... collect all inputs
    
    payload = {...}
    response = requests.post(url, auth=(SN_USER, SN_PWD), ...)
    
    if response.status_code == 201:
        print(f"SUCCESS! Ticket {response.json()['result']['number']} created.")
```

**After (API):**
```python
# POST /api/servicenow/tickets
import requests

response = requests.post(
    "http://localhost:8000/api/servicenow/tickets",
    json={
        "student_name": "John Doe",
        "roll_number": "2021CS001",
        "room_number": "A-101",
        "contact_number": "+1234567890",
        "description": "WiFi not working"
    }
)

if response.status_code == 201:
    ticket = response.json()
    print(f"Ticket: {ticket['ticket_number']}")
```

**After (Direct Service):**
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
print(f"Department: {result.assignment_group}")
```

**After (CLI):**
```bash
# Interactive CLI tool
python servicenow_cli.py
```

#### 4. `check_status()`
**Before:**
```python
def check_status():
    ticket_num = input("Enter your Ticket number : ")
    
    c_url = base_url + query
    response = requests.get(c_url, auth=(SN_USER,SN_PWD), ...)
    
    if response.status_code == 200:
        # ... display status
```

**After (API):**
```python
# GET /api/servicenow/tickets/{ticket_number}/status
import requests

response = requests.get(
    "http://localhost:8000/api/servicenow/tickets/REP0001001/status"
)

if response.status_code == 200:
    status = response.json()
    print(f"State: {status['state']}")
    print(f"Reply: {status['latest_reply']}")
```

**After (Direct Service):**
```python
from Backend.services.servicenow.service import servicenow_service

status = servicenow_service.get_ticket_status("REP0001001")
print(f"State: {status.state}")
print(f"Reply: {status.latest_reply}")
```

## 🔐 Configuration Migration

### Before
```python
# Hardcoded in script
admin_user = "admin"
admin_pass = "cP3S4@oUGrf@"
url = "https://dev322675.service-now.com/api/now/table/x_1897466_colleg_0_college_repair"
```

### After
```yaml
# In config.yml
SERVICENOW_INSTANCE_URL: https://dev322675.service-now.com
SERVICENOW_TABLE_NAME: x_1897466_colleg_0_college_repair
SERVICENOW_USERNAME: college_api_user
SERVICENOW_PASSWORD: "z:Dg6<*!i=.Q4@,_]Tpi?{?OR.ZIU^fPR"
```

Or use environment variables:
```bash
export SERVICENOW_USERNAME="college_api_user"
export SERVICENOW_PASSWORD="your-password"
```

## 🚀 Usage Examples

### Example 1: Create Ticket via API
```python
import requests

# Create ticket
response = requests.post(
    "http://localhost:8000/api/servicenow/tickets",
    json={
        "student_name": "Alice Johnson",
        "roll_number": "2021CS001",
        "room_number": "A-101",
        "contact_number": "+1234567890",
        "description": "urgent wifi problem"
    }
)

ticket = response.json()
print(f"Created: {ticket['ticket_number']}")
print(f"Routed to: {ticket['assignment_group']}")
print(f"Priority: Impact={ticket['impact']}, Urgency={ticket['urgency']}")
```

### Example 2: Check Status via API
```python
import requests

# Check status
ticket_number = "REP0001001"
response = requests.get(
    f"http://localhost:8000/api/servicenow/tickets/{ticket_number}/status"
)

status = response.json()
print(f"Ticket: {status['ticket_number']}")
print(f"State: {status['state']}")
print(f"Description: {status['short_description']}")
print(f"Reply: {status['latest_reply']}")
```

### Example 3: Use Service Directly
```python
from Backend.services.servicenow.service import servicenow_service
from Backend.services.servicenow.schemas import TicketCreate

# Create ticket
ticket_data = TicketCreate(
    student_name="Bob Smith",
    roll_number="2021CS002",
    room_number="B-205",
    contact_number="+1234567891",
    description="light bulb broken"
)

result = servicenow_service.create_ticket(ticket_data)
print(f"Ticket: {result.ticket_number}")

# Check status
status = servicenow_service.get_ticket_status(result.ticket_number)
print(f"State: {status.state}")
```

### Example 4: Use CLI (Most Similar to Original)
```bash
python servicenow_cli.py
```

This provides an interactive interface similar to the original script!

## 🎯 Benefits of New Module

### 1. **Better Integration**
- Part of your FastAPI backend
- Works with other APIs
- Shared configuration and logging

### 2. **Type Safety**
- Pydantic validation
- Catches errors early
- Better IDE support

### 3. **Flexibility**
- REST API for external access
- Direct service calls for internal use
- CLI for manual testing

### 4. **Maintainability**
- Modular structure
- Unit tests
- Documentation

### 5. **Production Ready**
- Proper error handling
- Configuration management
- Async support

## 📚 Next Steps

1. **Start the backend:**
   ```bash
   python -m Backend
   ```

2. **Test with CLI (most familiar):**
   ```bash
   pip install rich
   python servicenow_cli.py
   ```

3. **Test with examples:**
   ```bash
   python examples/servicenow_example.py
   ```

4. **Read the docs:**
   - [Quick Start](SERVICENOW_QUICKSTART.md)
   - [Full Documentation](Backend/services/servicenow/README.md)
   - API Docs: http://localhost:8000/api/docs

## ❓ FAQ

**Q: Can I still use the original script?**
A: Yes, but the new module is more powerful and maintainable.

**Q: Do I need to learn FastAPI?**
A: Not necessarily! You can use the CLI or direct service calls.

**Q: How do I test it?**
A: Use the CLI tool (`python servicenow_cli.py`) - it works like the original!

**Q: Is it compatible with my existing code?**
A: Yes! You can call the REST API from any language.

**Q: What about the credentials?**
A: They're now in `config.yml` and can be overridden with environment variables.

## 🎉 You're Ready!

The new module does everything the original script did, but better:
- ✅ Same functionality
- ✅ Better structure
- ✅ More flexible
- ✅ Production ready
- ✅ Well documented

Try the CLI first - it's the closest to the original experience!
