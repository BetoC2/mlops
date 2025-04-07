import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.transforms as transforms
import mlflow
import mlflow.pytorch
from torch.utils.data import DataLoader
from torchvision.datasets import MNIST

# Define the simple neural network model for MNIST classification
class SimpleNN(nn.Module):
    def __init__(self):
        super(SimpleNN, self).__init__()
        self.fc1 = nn.Linear(28 * 28, 128)  # First fully connected layer
        self.fc2 = nn.Linear(128, 64)       # Second fully connected layer
        self.fc3 = nn.Linear(64, 10)        # Output layer for 10 classes

    def forward(self, x):
        x = x.view(-1, 28 * 28)  # Flatten the input image
        x = torch.relu(self.fc1(x))  # Apply ReLU activation function
        x = torch.relu(self.fc2(x))  # Apply ReLU activation function
        x = self.fc3(x)              # Output layer (raw scores for each class)
        return x

# Set the hyperparameters for the experiment
learning_rates = [0.001, 0.01]
epochs_list = [5, 10]
optimizers = ['SGD', 'Adam']

# Set up the transformation to normalize the MNIST dataset
transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5,), (0.5,))])

# Load the MNIST dataset
train_data = MNIST(root='./data', train=True, download=True, transform=transform)
test_data = MNIST(root='./data', train=False, download=True, transform=transform)

# Create DataLoader for train and test datasets
train_loader = DataLoader(train_data, batch_size=64, shuffle=True)
test_loader = DataLoader(test_data, batch_size=64, shuffle=False)

# Define the training function
def train(model, criterion, optimizer, num_epochs, lr):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    for epoch in range(num_epochs):
        for inputs, labels in train_loader:
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

        accuracy = 100 * correct / total
        avg_loss = running_loss / len(train_loader)
        print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {avg_loss:.4f}, Accuracy: {accuracy:.2f}%")
    
    return avg_loss, accuracy

# Set up MLFlow experiment
mlflow.set_experiment("MNIST_Classification")

# Iterate through different hyperparameters
for lr in learning_rates:
    for epochs in epochs_list:
        for optimizer_name in optimizers:
            
            # Log experiment parameters
            with mlflow.start_run():
                mlflow.log_param('learning_rate', lr)
                mlflow.log_param('epochs', epochs)
                mlflow.log_param('optimizer', optimizer_name)
                
                # Initialize model, criterion, and optimizer
                model = SimpleNN()
                criterion = nn.CrossEntropyLoss()
                if optimizer_name == 'SGD':
                    optimizer = optim.SGD(model.parameters(), lr=lr)
                elif optimizer_name == 'Adam':
                    optimizer = optim.Adam(model.parameters(), lr=lr)

                # Train the model and log metrics
                loss, accuracy = train(model, criterion, optimizer, epochs, lr)
                mlflow.log_metric('loss', loss)
                mlflow.log_metric('accuracy', accuracy)

                # Save the model as an artifact
                mlflow.pytorch.log_model(model, "model")