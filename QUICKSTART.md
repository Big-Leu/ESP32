# Quick Start Guide - ESP32 Sensor Service

## Prerequisites
- Python 3.12+
- PostgreSQL database
- UV package manager
- (Optional) Twilio account for SMS
- (Optional) SendGrid account for email

## Installation

### 1. Install Dependencies
```bash
cd Backend
uv sync
```

### 2. Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
# Required: Database settings (already configured)
# Optional: Twilio/SendGrid credentials
```

### 3. Add ML Model
```bash
# Train your model (see Backend/services/esp32/MODEL_README.md)
# Copy model.pkl to Backend/services/esp32/model.pkl
```

### 4. Run Database Migration
```bash
uv run alembic revision --autogenerate -m "Add sensor readings table"
uv run alembic upgrade head
```

### 5. Start the Server
```bash
uv run uvicorn Backend.web.application:get_app --reload
```

Server will be available at: http://localhost:8000
API Documentation: http://localhost:8000/docs

## Testing the API

### 1. Get Authentication Token
```bash
# Register a user
curl -X POST http://localhost:8000/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'

# Login to get token
curl -X POST http://localhost:8000/api/users/auth/jwt/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password&username=test@example.com&password=SecurePass123!"

# Save the access_token from response
TOKEN="your_access_token_here"
```

### 2. Test Sensor Endpoints

#### Create a Reading
```bash
curl -X POST http://localhost:8000/api/esp32/readings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "ammonia_ppm": 2.5,
    "h2s_ppm": 0.05,
    "temperature": 25.0,
    "humidity": 60.0
  }'
```

#### Get All Readings
```bash
curl http://localhost:8000/api/esp32/readings?limit=10 \
  -H "Authorization: Bearer $TOKEN"
```

#### Get Specific Reading
```bash
curl http://localhost:8000/api/esp32/readings/1 \
  -H "Authorization: Bearer $TOKEN"
```

#### Predict Thresholds
```bash
curl -X POST http://localhost:8000/api/esp32/predict \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "temperature": 25.0,
    "humidity": 60.0
  }'
```

#### Evaluate Alert
```bash
curl -X POST http://localhost:8000/api/esp32/alerts/evaluate/1 \
  -H "Authorization: Bearer $TOKEN"
```

## ESP32 Integration

### Arduino/ESP32 Code Example
```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* ssid = "your_wifi_ssid";
const char* password = "your_wifi_password";
const char* serverUrl = "http://your-server:8000/api/esp32/readings";
const char* token = "your_jwt_token";

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    
    // Read sensors (replace with your sensor code)
    float ammonia = readAmmonia();
    float h2s = readH2S();
    float temp = readTemperature();
    float humidity = readHumidity();
    
    // Create JSON payload
    StaticJsonDocument<200> doc;
    doc["ammonia_ppm"] = ammonia;
    doc["h2s_ppm"] = h2s;
    doc["temperature"] = temp;
    doc["humidity"] = humidity;
    
    String jsonString;
    serializeJson(doc, jsonString);
    
    // Send HTTP POST
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");
    http.addHeader("Authorization", String("Bearer ") + token);
    
    int httpResponseCode = http.POST(jsonString);
    
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Response: " + response);
    } else {
      Serial.println("Error: " + String(httpResponseCode));
    }
    
    http.end();
  }
  
  delay(5000); // Send reading every 5 seconds
}

// Implement these functions based on your sensors
float readAmmonia() { return 2.5; }
float readH2S() { return 0.05; }
float readTemperature() { return 25.0; }
float readHumidity() { return 60.0; }
```

## Troubleshooting

### Import Errors in IDE
- Run: `uv sync` to ensure all packages installed
- Restart VS Code to refresh Python environment
- Select correct Python interpreter (from `.venv`)

### Database Connection Failed
- Verify PostgreSQL is running
- Check database credentials in `.env`
- Ensure database exists: `createdb sensor_db`

### Model Not Found Error
- Place trained `model.pkl` in `Backend/services/esp32/`
- Verify file permissions
- Check model format (should be pickled Ridge model)

### Notifications Not Working
- Verify credentials in `.env`
- Check Twilio/SendGrid account status
- Review logs for error messages
- Test credentials directly with provider APIs

### Alerts Not Triggering
- Check `SUSTAIN_SECONDS` configuration
- Verify readings exceed predicted thresholds
- Review logs for alert state transitions
- Ensure readings are recent (timestamp matters)

## Configuration Tips

### Adjust Alert Sensitivity
```bash
# Reduce sustain time for faster alerts
SUSTAIN_SECONDS=5

# Increase for less frequent alerts
SUSTAIN_SECONDS=30
```

### Customize Thresholds
Edit `Backend/services/esp32/predictor.py`:
```python
# Change multipliers in predict_thresholds method
score_moderate = min(100.0, fused_baseline * 1.3)  # Was 1.5
score_strong = min(100.0, fused_baseline * 1.8)    # Was 2.0
```

### Adjust Gas Normalization
Edit max values in `predictor.py`:
```python
norm_nh3 = self.normalize(baseline_nh3, max_value=10.0)  # Was 5.0
norm_h2s = self.normalize(baseline_h2s, max_value=0.2)   # Was 0.1
```

## Development

### Run Tests
```bash
uv run pytest
```

### Check Code Quality
```bash
uv run ruff check .
uv run mypy Backend
```

### Format Code
```bash
uv run ruff format .
```

## Support

For detailed documentation, see:
- Service README: `Backend/services/esp32/README.md`
- Model Guide: `Backend/services/esp32/MODEL_README.md`
- Implementation Summary: `IMPLEMENTATION_SUMMARY.md`
- API Docs: http://localhost:8000/docs

---

**Ready to go!** 🚀

Your production-grade ESP32 sensor service is now set up and ready for deployment.
