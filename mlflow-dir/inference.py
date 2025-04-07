import torch
import json
import base64
from torchvision import transforms, datasets
from PIL import Image
import io
import random
import matplotlib.pyplot as plt

# Define the model and functions as provided
class SimpleNN(torch.nn.Module):
    def __init__(self):
        super(SimpleNN, self).__init__()
        self.fc1 = torch.nn.Linear(28 * 28, 128)
        self.fc2 = torch.nn.Linear(128, 64)
        self.fc3 = torch.nn.Linear(64, 10)

    def forward(self, x):
        x = x.view(-1, 28 * 28)
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        return x

def model_fn(model_dir):
    """
    Loads the traced model from the model directory (the saved .pt file).
    """
    model_path = f"{model_dir}/model.pt"
    model = torch.jit.load(model_path)
    model.eval()
    return model

def input_fn(request_body, request_content_type):
    """
    Preprocess the incoming data and convert it into the correct format for the model.
    """
    if request_content_type == 'application/json':
        payload = json.loads(request_body)
        image_data = base64.b64decode(payload['instances'][0]['data'])
        image = Image.open(io.BytesIO(image_data))

        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.5,), (0.5,))
        ])
        image = transform(image).unsqueeze(0)  # Add batch dimension
        return image
    else:
        raise Exception(f"Unsupported content type: {request_content_type}")

def predict_fn(input_data, model):
    """
    Run the model on the input data and return the prediction.
    """
    with torch.no_grad():
        output = model(input_data)
    return output

def output_fn(prediction, response_content_type):
    """
    Process the model output and return the response in the correct format.
    """
    if response_content_type == 'application/json':
        _, predicted_class = torch.max(prediction, 1)
        return json.dumps({"predictions": predicted_class.tolist()})
    else:
        raise Exception(f"Unsupported response content type: {response_content_type}")