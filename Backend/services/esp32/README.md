# ESP32 Sensor Service

Production-grade service for managing ESP32 gas sensor readings with ML-based alert system.

## Features

- **Sensor Reading Management**: Store and retrieve ammonia (NH₃) and hydrogen sulfide (H₂S) readings
- **ML-Based Predictions**: Ridge regression model predicts odor thresholds based on temperature and humidity
- **Sustained Alert Detection**: Configurable time-based alert system prevents false alarms
- **Multi-Channel Notifications**: SMS (Twilio) and Email (SendGrid) alerts
- **Async Operations**: Full async/await support for high performance
- **Production Ready**: Comprehensive logging, error handling, and type hints

## Architecture

```
Backend/
├── db/models/
│   └── sensor.py              # SQLAlchemy model for sensor readings
├── services/esp32/
│   ├── crud.py                # Database operations and alert evaluation
│   ├── predictor.py           # ML threshold prediction
│   ├── alert_service.py       # Alert detection and notification
│   └── model.pkl              # Trained Ridge regression model (add yours)
└── web/api/esp32/
    ├── schema.py              # Pydantic schemas
    └── views.py               # API endpoints
```

## API Endpoints

### POST `/api/esp32/readings`
Create a new sensor reading. Automatically evaluates alerts.

**Request Body:**
```json
{
  "ammonia_ppm": 2.5,
  "h2s_ppm": 0.05,
  "temperature": 25.0,
  "humidity": 60.0
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "ammonia_ppm": 2.5,
  "h2s_ppm": 0.05,
  "temperature": 25.0,
  "humidity": 60.0,
  "created_at": "2025-11-30T12:00:00Z"
}
```

### GET `/api/esp32/readings`
Get all sensor readings with pagination.

**Query Parameters:**
- `limit` (int, default=100, max=1000): Number of readings to return
- `offset` (int, default=0): Number of readings to skip

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "ammonia_ppm": 2.5,
    "h2s_ppm": 0.05,
    "temperature": 25.0,
    "humidity": 60.0,
    "created_at": "2025-11-30T12:00:00Z"
  }
]
```

### GET `/api/esp32/readings/{reading_id}`
Get a specific reading by ID.

**Response:** `200 OK` or `404 Not Found`

### POST `/api/esp32/predict`
Predict odor thresholds based on environmental conditions.

**Request Body:**
```json
{
  "temperature": 25.0,
  "humidity": 60.0
}
```

**Response:** `200 OK`
```json
{
  "baseline_fused": 45.2,
  "score_moderate": 67.8,
  "score_strong": 90.4
}
```

### POST `/api/esp32/alerts/evaluate/{reading_id}`
Manually evaluate alert conditions for a specific reading.

**Response:** `200 OK`
```json
{
  "alert": true,
  "level": 2,
  "message": "⚠️ Level-2 MODERATE odour detected (score=72.50). Please attend soon.",
  "score": 72.5,
  "thresholds": {
    "baseline_fused": 45.2,
    "score_moderate": 67.8,
    "score_strong": 90.4
  }
}
```

## Alert Levels

- **Level 1 (Normal)**: Odor below moderate threshold
- **Level 2 (Moderate)**: Odor ≥ moderate threshold, requires attention
- **Level 3 (Strong)**: Odor ≥ strong threshold, immediate action needed

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Alert Configuration
SUSTAIN_SECONDS=10              # Seconds before triggering alert

# Twilio SMS (Optional)
TWILIO_SID=your_account_sid
TWILIO_TOKEN=your_auth_token
TWILIO_PHONE=+1234567890        # Your Twilio number
ALERT_PHONE=+1234567890         # Recipient number

# SendGrid Email (Optional)
SENDGRID_API_KEY=your_api_key
FROM_EMAIL=alerts@yourdomain.com
ALERT_EMAIL=recipient@example.com
```

### ML Model

Place your trained `model.pkl` file in `Backend/services/esp32/model.pkl`.

The model should:
- Accept input: `[temperature, humidity]`
- Return output: `[baseline_nh3, baseline_h2s]`
- Be trained using scikit-learn Ridge regression

## How It Works

### 1. Sensor Reading Flow

```
ESP32 → POST /readings → Store in DB → Evaluate Alert (async)
```

### 2. Alert Evaluation

1. **Predict Thresholds**: ML model predicts thresholds based on temperature/humidity
2. **Compute Fused Score**: Normalize and combine NH₃ and H₂S readings
3. **Check Sustained Condition**: Verify odor exceeds threshold for configured duration
4. **Send Notifications**: SMS and email alerts if triggered

### 3. Normalization

Gas readings are normalized to 0-100 scale:
- NH₃: Max expected = 5.0 ppm
- H₂S: Max expected = 0.1 ppm

Fused score = (normalized_nh3 × 0.5) + (normalized_h2s × 0.5)

## Dependencies

```toml
# Add to pyproject.toml
dependencies = [
    "fastapi",
    "sqlalchemy",
    "pandas",
    "scikit-learn",
    "twilio",        # Optional, for SMS
    "sendgrid",      # Optional, for email
]
```

## Testing

Run the API server:
```bash
uv run uvicorn Backend.web.application:get_app --reload
```

Test with curl:
```bash
# Create reading
curl -X POST http://localhost:8000/api/esp32/readings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "ammonia_ppm": 2.5,
    "h2s_ppm": 0.05,
    "temperature": 25.0,
    "humidity": 60.0
  }'

# Get readings
curl http://localhost:8000/api/esp32/readings \
  -H "Authorization: Bearer YOUR_TOKEN"

# Predict thresholds
curl -X POST http://localhost:8000/api/esp32/predict \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "temperature": 25.0,
    "humidity": 60.0
  }'
```

## Production Considerations

### Logging

- All operations logged via `loguru`
- Set `LOG_LEVEL` environment variable (DEBUG, INFO, WARNING, ERROR)

### Error Handling

- Graceful degradation if ML model or notifications fail
- Readings always saved even if alert evaluation fails
- HTTP 404 for missing resources
- HTTP 500 for internal errors

### Performance

- Singleton predictor instance (model loaded once)
- Async database operations
- Non-blocking alert evaluation
- Efficient pagination for large datasets

### Security

- All endpoints require authentication (`current_active_user`)
- Secrets managed via environment variables
- No sensitive data in logs

### Scalability

- Stateless alert service (except in-memory state)
- Consider Redis for distributed alert state
- Database indexes on `created_at` for query performance

## Monitoring

Monitor these metrics:
- Alert response time
- SMS/Email delivery success rate
- False positive/negative rates
- API endpoint latency
- Database query performance

## Troubleshooting

**Notifications not working:**
- Verify credentials in `.env`
- Check logs for error messages
- Test credentials directly with provider APIs

**Alerts not triggering:**
- Verify `SUSTAIN_SECONDS` configuration
- Check threshold predictions vs actual readings
- Review logs for state transitions

**Model not loading:**
- Ensure `model.pkl` exists in `Backend/services/esp32/`
- Verify model format (scikit-learn pickle)
- Check file permissions

## License

[Your License]
