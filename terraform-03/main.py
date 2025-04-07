from fastapi import FastAPI, File, UploadFile
import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image
import io

# Load the pre-trained model
class EnhancedNN(nn.Module):
    def __init__(self):
        super(EnhancedNN, self).__init__()
        self.fc1 = nn.Linear(32 * 32, 256)
        self.bn1 = nn.BatchNorm1d(256)
        self.dropout1 = nn.Dropout(0.3)

        self.fc2 = nn.Linear(256, 128)
        self.bn2 = nn.BatchNorm1d(128)
        self.dropout2 = nn.Dropout(0.3)

        self.fc3 = nn.Linear(128, 64)
        self.bn3 = nn.BatchNorm1d(64)
        self.dropout3 = nn.Dropout(0.3)

        self.fc4 = nn.Linear(64, 10)

    def forward(self, x):
        x = x.view(-1, 32 * 32)  # Flatten the image
        x = torch.relu(self.bn1(self.fc1(x)))
        x = self.dropout1(x)
        x = torch.relu(self.bn2(self.fc2(x)))
        x = self.dropout2(x)
        x = torch.relu(self.bn3(self.fc3(x)))
        x = self.dropout3(x)
        x = self.fc4(x)  # No softmax, as CrossEntropyLoss applies it internally
        return x

# Initialize FastAPI app
app = FastAPI()

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load the pre-trained model
model = EnhancedNN().to(device)
model.load_state_dict(torch.load('best_mnist_model.pth'))
model.eval()

# Define the image transformation
transform = transforms.Compose([
    transforms.Resize((32, 32)),
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])

# Inference endpoint
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # Read image from file
    img = Image.open(io.BytesIO(await file.read())).convert("L")  # Convert to grayscale

    # Apply transformation
    img_tensor = transform(img).unsqueeze(0).to(device)  # Add batch dimension and move to device

    # Perform inference
    with torch.no_grad():
        outputs = model(img_tensor)
        _, predicted = torch.max(outputs, 1)

    # Return the predicted class
    return {"prediction": predicted.item()}