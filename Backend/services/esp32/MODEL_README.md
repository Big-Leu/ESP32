# ML Model Placeholder

This directory should contain your trained Ridge regression model saved as `model.pkl`.

## Model Requirements

The model should:

1. **Input Features**: 
   - `temperature` (float): Temperature in Celsius
   - `humidity` (float): Relative humidity percentage (0-100)

2. **Output**:
   - `baseline_nh3` (float): Predicted baseline ammonia level in ppm
   - `baseline_h2s` (float): Predicted baseline H2S level in ppm

3. **Format**: Scikit-learn Ridge regression model serialized with pickle

## Training Example

```python
import pickle
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split

# Load your training data
# df should have columns: temperature, humidity, ammonia_ppm, h2s_ppm
df = pd.read_csv("sensor_training_data.csv")

X = df[["temperature", "humidity"]]
y = df[["ammonia_ppm", "h2s_ppm"]]

# Split and train
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

ridge_model = Ridge(alpha=1.0)
ridge_model.fit(X_train, y_train)

# Save model
with open("model.pkl", "wb") as f:
    pickle.dump(ridge_model, f)

print("Model saved successfully!")
```

## Using the Model

Once trained and saved, place `model.pkl` in this directory. The predictor service will automatically load it at startup.

```bash
Backend/services/esp32/
├── model.pkl          # Your trained model here
├── predictor.py       # Loads and uses the model
└── MODEL_README.md    # This file
```
