# main.py

import io
import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image
import uvicorn # Import uvicorn for running directly if needed

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse # Optional: For more control over responses

# --- 1. Setup and Model Definition ---
# Ensure this definition matches the one used for training
class SimpleMNIST_NN(nn.Module):
    def __init__(self):
        super(SimpleMNIST_NN, self).__init__()
        self.flatten = nn.Flatten()
        self.fc1 = nn.Linear(28 * 28, 128) # Input layer expects 28*28
        self.relu1 = nn.ReLU()
        self.fc2 = nn.Linear(128, 64)
        self.relu2 = nn.ReLU()
        self.fc3 = nn.Linear(64, 10)


    def forward(self, x):
        x = self.flatten(x)
        x = self.relu1(self.fc1(x))
        x = self.relu2(self.fc2(x))
        x = self.fc3(x)
        return x

# --- 2. Device and Model Loading ---
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = SimpleMNIST_NN().to(device)

# Load the trained weights
MODEL_PATH = "best_mnist_model.pth" # Make sure this file exists
try:
    # Use map_location to load correctly whether trained on CPU or GPU
    model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
except FileNotFoundError:
    print(f"ERROR: Model weights file not found at {MODEL_PATH}")
    print("Please ensure the model has been trained and the .pth file is in the correct directory.")
    exit() # Exit if model weights aren't found

model.eval() # Set the model to evaluation mode (important!)

# --- 3. Image Transformations ---
# Define the image transformation - SHOULD MATCH TRAINING (except maybe ToTensor if not done)
# Using 28x28 as it's standard for MNIST and likely what the model was trained on
transform = transforms.Compose([
    transforms.Resize((28, 28)), # Resize to the size the model expects
    transforms.ToTensor(),       # Convert image to PyTorch tensor (scales pixels to [0, 1])
    transforms.Normalize((0.1307,), (0.3081,)) # Normalize (use MNIST std mean/dev)
])

# --- 4. FastAPI App ---
app = FastAPI(
    title="MNIST Digit Recognizer API",
    description="Upload a grayscale image of a handwritten digit to get a prediction.",
    version="1.0.0"
)

# Reminder for the user
print("\n---")
print("Ensure 'python-multipart' is installed: pip install python-multipart")
print("---")

# --- 5. Prediction Endpoint ---
@app.post("/predict", summary="Predict Handwritten Digit", tags=["Prediction"])
async def predict(file: UploadFile = File(..., description="Image file of a handwritten digit")):
    """
    Accepts an image file, processes it, and returns the predicted digit (0-9).
    - **file**: The image file to be processed (e.g., PNG, JPG).
    """
    print(f"Received file: {file.filename}, Content-Type: {file.content_type}")

    # Basic check for image content type (optional but good practice)
    if not file.content_type.startswith("image/"):
         return JSONResponse(
            status_code=400,
            content={"error": "File provided is not an image."}
        )

    try:
        # Read image content from uploaded file
        contents = await file.read()
        # Open image using Pillow, convert to grayscale ('L' mode)
        img = Image.open(io.BytesIO(contents)).convert("L")

        # Apply the transformations
        # unsqueeze(0) adds the batch dimension (N, C, H, W) -> (1, 1, 28, 28)
        img_tensor = transform(img).unsqueeze(0).to(device)

        # Perform inference
        with torch.no_grad(): # Disable gradient calculations
            outputs = model(img_tensor)
            probabilities = torch.softmax(outputs, dim=1) # Get probabilities
            _, predicted_idx = torch.max(outputs, 1)      # Get the index of the max logit

        predicted_class = predicted_idx.item() # Get the predicted class as an integer
        confidence = probabilities[0, predicted_class].item() # Get confidence of the prediction

        print(f"Prediction: {predicted_class}, Confidence: {confidence:.4f}")

        # Return the prediction
        return {"prediction": predicted_class, "confidence": round(confidence, 4)}

    except Exception as e:
        print(f"Error processing file: {e}")
        # Return a more informative error message in JSON format
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to process image: {str(e)}"}
        )
    finally:
        # Ensure the file is closed if necessary (FastAPI might handle this)
        await file.close()


# --- 6. Root Endpoint (Optional) ---
@app.get("/", summary="API Root", tags=["General"])
async def read_root():
    """Provides basic information about the API."""
    return {
        "message": "Welcome to the MNIST Digit Recognizer API",
        "docs_url": "/docs",
        "predict_endpoint": "/predict (POST)"
        }

# --- 7. Run the app (Optional: for running directly) ---
# This block allows running the script directly with `python main.py`
# However, `uvicorn main:app --reload` is generally preferred for development
if __name__ == "__main__":
    print("Starting FastAPI server using uvicorn...")
    uvicorn.run(app, host="127.0.0.1", port=8000)

    # Alternatively, to match the command line exactly:
    # uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
    # Note: reload=True in code might have limitations compared to CLI