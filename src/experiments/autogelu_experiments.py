#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script implements three experiments to compare AutoGELU with fixed activation functions.
It includes:
  1. Activation Function Comparison on CIFAR‑10 with a SimpleCNN.
  2. Visualization of the learnable parameters (α, β) in AutoGELU.
  3. Gradient Flow Analysis using a deep MLP on MNIST.
All plots are saved as PDF files.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
from torchvision.datasets import MNIST
import numpy as np
import random
import matplotlib.pyplot as plt
import os

# ---------------------------
# Utility functions
# ---------------------------
def set_seed(seed):
    torch.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        
set_seed(42)

# ---------------------------
# Activation Functions
# ---------------------------
def gelu(x):
    return 0.5 * x * (1 + torch.tanh(np.sqrt(2/np.pi) * (x + 0.044715 * torch.pow(x, 3))))

def swish(x):
    return x * torch.sigmoid(x)

# ---------------------------
# AutoGELU Activation Module
# ---------------------------
class AutoGELU(nn.Module):
    def __init__(self):
        super(AutoGELU, self).__init__()
        # Initialize with values similar to original GELU
        self.alpha = nn.Parameter(torch.tensor(1.0))
        self.beta = nn.Parameter(torch.tensor(0.044715))
    
    def forward(self, x):
        return x * 0.5 * (1 + torch.tanh(np.sqrt(2/np.pi) * (self.alpha * x + self.beta * torch.pow(x, 3))))

# ---------------------------
# Model Architectures
# ---------------------------
class SimpleCNN(nn.Module):
    def __init__(self, activation, activation_name="unknown"):
        super(SimpleCNN, self).__init__()
        self.activation_name = activation_name
        self.activation = activation  # can be a function or a module instance
        self.conv1 = nn.Conv2d(3, 32, 3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(64 * 8 * 8, 256)
        self.fc2 = nn.Linear(256, 10)
        self.dropout = nn.Dropout(0.5)
    
    def forward(self, x):
        # Conv Block 1
        x = self.conv1(x)
        if isinstance(self.activation, nn.Module):
            x = self.activation(x)
        else:
            x = self.activation(x)
        x = self.pool(x)
        
        # Conv Block 2
        x = self.conv2(x)
        if isinstance(self.activation, nn.Module):
            x = self.activation(x)
        else:
            x = self.activation(x)
        x = self.pool(x)
        
        # Fully Connected Layers
        x = x.view(-1, 64 * 8 * 8)
        x = self.fc1(x)
        if isinstance(self.activation, nn.Module):
            x = self.activation(x)
        else:
            x = self.activation(x)
        x = self.dropout(x)
        x = self.fc2(x)
        return x

class DeepMLP(nn.Module):
    def __init__(self, activation, activation_name="unknown", input_dim=784, hidden_dim=512, num_layers=10, num_classes=10):
        super(DeepMLP, self).__init__()
        self.activation_name = activation_name
        layers = []
        layers.append(nn.Linear(input_dim, hidden_dim))
        for _ in range(num_layers - 1):
            layers.append(nn.Linear(hidden_dim, hidden_dim))
        self.hidden_layers = nn.ModuleList(layers)
        self.output_layer = nn.Linear(hidden_dim, num_classes)
        self.activation = activation
        
    def forward(self, x):
        # Flatten the image for MLP
        x = x.view(x.size(0), -1)
        for layer in self.hidden_layers:
            x = layer(x)
            if isinstance(self.activation, nn.Module):
                x = self.activation(x)
            else:
                x = self.activation(x)
        x = self.output_layer(x)
        return x

# ---------------------------
# Training Functions
# ---------------------------
def train_model(model, trainloader, testloader, epochs=20, lr=0.1, device='cpu'):
    model.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=lr, momentum=0.9, weight_decay=5e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    
    history = {'train_loss':[], 'train_acc':[], 'test_acc':[]}
    
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        for inputs, labels in trainloader:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item() * inputs.size(0)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
        train_loss = running_loss / total
        train_acc = 100. * correct / total
        
        # Evaluation on test set
        model.eval()
        correct_test = 0
        total_test = 0
        with torch.no_grad():
            for inputs, labels in testloader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                _, predicted = outputs.max(1)
                total_test += labels.size(0)
                correct_test += predicted.eq(labels).sum().item()
        test_acc = 100. * correct_test / total_test
        
        scheduler.step()
        
        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['test_acc'].append(test_acc)
        
        print(f"[{model.activation_name}] Epoch [{epoch+1}/{epochs}] Train loss: {train_loss:.3f} Train acc: {train_acc:.2f}% Test acc: {test_acc:.2f}%")
    
    return history

def train_model_with_logging(model, trainloader, testloader, epochs=20, lr=0.1, device='cpu'):
    model.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=lr, momentum=0.9, weight_decay=5e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    
    # Lists to log AutoGELU parameters
    alpha_vals = []
    beta_vals = []
    test_accs = []
    
    for epoch in range(epochs):
        model.train()
        for inputs, labels in trainloader:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
        
        scheduler.step()
        
        # Log AutoGELU parameters
        if hasattr(model, 'activation') and isinstance(model.activation, AutoGELU):
            alpha_vals.append(model.activation.alpha.item())
            beta_vals.append(model.activation.beta.item())
        
        # Evaluate test accuracy
        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for inputs, labels in testloader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                _, predicted = outputs.max(1)
                total += labels.size(0)
                correct += predicted.eq(labels).sum().item()
        test_acc = 100. * correct / total
        test_accs.append(test_acc)
        
        print(f"Epoch {epoch+1}: AutoGELU alpha = {alpha_vals[-1]:.4f}, beta = {beta_vals[-1]:.6f}, Test acc = {test_acc:.2f}%")
    
    return alpha_vals, beta_vals, test_accs

def train_deep_model(model, trainloader, epochs=10, lr=0.01, device='cpu'):
    model.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=lr, momentum=0.9, weight_decay=5e-4)
    
    # For gradient logging
    grad_norms_history = []
    
    for epoch in range(epochs):
        model.train()
        epoch_grad_norms = []  # store grad norms for each batch
        
        for batch_idx, (inputs, labels) in enumerate(trainloader):
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            
            # Calculate gradient norms for each hidden layer
            layer_grad_norms = []
            for i, layer in enumerate(model.hidden_layers):
                if layer.weight.grad is not None:
                    norm = layer.weight.grad.data.norm(2).item()
                    layer_grad_norms.append(norm)
            
            if len(layer_grad_norms) > 0:
                epoch_grad_norms.append(layer_grad_norms)
            
            optimizer.step()
            
            if batch_idx % 100 == 0:
                print(f"[{model.activation_name}] Epoch {epoch+1}, Batch {batch_idx}, Loss: {loss.item():.4f}")
        
        # Average the gradient norms for each layer over the epoch
        if len(epoch_grad_norms) > 0:
            avg_grad_norms = np.mean(epoch_grad_norms, axis=0)
            grad_norms_history.append(avg_grad_norms)
            print(f"[{model.activation_name}] Epoch {epoch+1}, Avg Grad Norms (first 3 layers): {avg_grad_norms[:3]}")
    
    return grad_norms_history

# ---------------------------
# Experiment 1: Activation Function Comparison
# ---------------------------
def experiment1_activation_comparison(test_mode=False):
    print("\n" + "="*60)
    print("EXPERIMENT 1: Activation Function Comparison on CIFAR-10")
    print("="*60)
    
    # Data preparation for CIFAR-10
    transform = transforms.Compose([
        transforms.RandomCrop(32, padding=4),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])
    
    test_transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])
    
    trainset = torchvision.datasets.CIFAR10(root='./data', train=True, download=True, transform=transform)
    testset = torchvision.datasets.CIFAR10(root='./data', train=False, download=True, transform=test_transform)
    
    # Use smaller batch size and epochs for test mode
    batch_size = 128 if not test_mode else 64
    epochs = 20 if not test_mode else 2
    
    trainloader = torch.utils.data.DataLoader(trainset, batch_size=batch_size, shuffle=True, num_workers=2)
    testloader = torch.utils.data.DataLoader(testset, batch_size=batch_size, shuffle=False, num_workers=2)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Create and train models using different activation variants
    results = {}
    
    # Train with ReLU
    print("\nTraining with ReLU...")
    model_relu = SimpleCNN(activation=F.relu, activation_name="ReLU")
    history_relu = train_model(model_relu, trainloader, testloader, epochs=epochs, lr=0.1, device=device)
    results['ReLU'] = history_relu
    
    # Train with GELU
    print("\nTraining with GELU...")
    model_gelu = SimpleCNN(activation=gelu, activation_name="GELU")
    history_gelu = train_model(model_gelu, trainloader, testloader, epochs=epochs, lr=0.1, device=device)
    results['GELU'] = history_gelu
    
    # Train with Swish
    print("\nTraining with Swish...")
    model_swish = SimpleCNN(activation=swish, activation_name="Swish")
    history_swish = train_model(model_swish, trainloader, testloader, epochs=epochs, lr=0.1, device=device)
    results['Swish'] = history_swish
    
    # Train with AutoGELU
    print("\nTraining with AutoGELU...")
    auto_gelu = AutoGELU()
    model_auto_gelu = SimpleCNN(activation=auto_gelu, activation_name="AutoGELU")
    history_auto_gelu = train_model(model_auto_gelu, trainloader, testloader, epochs=epochs, lr=0.1, device=device)
    results['AutoGELU'] = history_auto_gelu
    
    # Print final test accuracies
    print("\n" + "-"*40)
    print("Final Test Accuracies:")
    for name, history in results.items():
        final_acc = history['test_acc'][-1]
        print(f"{name}: {final_acc:.2f}%")
    
    # Plot comparison results
    plt.figure(figsize=(15, 5))
    
    # Test Accuracy Plot
    plt.subplot(1, 3, 1)
    for name, history in results.items():
        plt.plot(history['test_acc'], label=name, marker='o', markersize=4)
    plt.title('Test Accuracy Comparison', fontsize=14)
    plt.xlabel('Epoch')
    plt.ylabel('Test Accuracy (%)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Training Loss Plot
    plt.subplot(1, 3, 2)
    for name, history in results.items():
        plt.plot(history['train_loss'], label=name, marker='o', markersize=4)
    plt.title('Training Loss Comparison', fontsize=14)
    plt.xlabel('Epoch')
    plt.ylabel('Training Loss')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Final Accuracy Bar Chart
    plt.subplot(1, 3, 3)
    names = list(results.keys())
    final_accs = [results[name]['test_acc'][-1] for name in names]
    bars = plt.bar(names, final_accs, color=['blue', 'green', 'orange', 'red'])
    plt.title('Final Test Accuracy', fontsize=14)
    plt.ylabel('Test Accuracy (%)')
    plt.ylim(0, 100)
    for bar, acc in zip(bars, final_accs):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{acc:.1f}%', ha='center', va='bottom')
    
    plt.tight_layout()
    filename = 'experiment1_activation_comparison.pdf'
    plt.savefig(filename, dpi=150)
    print(f"\nPlot saved as {filename}")
    plt.close()
    
    return results

# ---------------------------
# Experiment 2: Parameter Evolution
# ---------------------------
def experiment2_parameter_evolution(test_mode=False):
    print("\n" + "="*60)
    print("EXPERIMENT 2: AutoGELU Parameter Evolution")
    print("="*60)
    
    # Data preparation
    transform = transforms.Compose([
        transforms.RandomCrop(32, padding=4),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])
    
    test_transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])
    
    trainset = torchvision.datasets.CIFAR10(root='./data', train=True, download=True, transform=transform)
    testset = torchvision.datasets.CIFAR10(root='./data', train=False, download=True, transform=test_transform)
    
    batch_size = 128 if not test_mode else 64
    epochs = 20 if not test_mode else 3
    
    trainloader = torch.utils.data.DataLoader(trainset, batch_size=batch_size, shuffle=True, num_workers=2)
    testloader = torch.utils.data.DataLoader(testset, batch_size=batch_size, shuffle=False, num_workers=2)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Create model with AutoGELU
    auto_gelu2 = AutoGELU()
    model_auto_gelu2 = SimpleCNN(activation=auto_gelu2, activation_name="AutoGELU")
    
    # Train and log parameters
    alpha_history, beta_history, test_acc_history = train_model_with_logging(
        model_auto_gelu2, trainloader, testloader, epochs=epochs, lr=0.1, device=device
    )
    
    # Plot the parameter trajectories
    plt.figure(figsize=(15, 5))
    
    # Alpha evolution
    plt.subplot(1, 3, 1)
    plt.plot(alpha_history, marker='o', color='blue', linewidth=2, markersize=6)
    plt.title('Evolution of AutoGELU Alpha', fontsize=14)
    plt.xlabel('Epoch')
    plt.ylabel('Alpha Value')
    plt.grid(True, alpha=0.3)
    plt.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5, label='Initial value')
    plt.legend()
    
    # Beta evolution
    plt.subplot(1, 3, 2)
    plt.plot(beta_history, marker='o', color='red', linewidth=2, markersize=6)
    plt.title('Evolution of AutoGELU Beta', fontsize=14)
    plt.xlabel('Epoch')
    plt.ylabel('Beta Value')
    plt.grid(True, alpha=0.3)
    plt.axhline(y=0.044715, color='gray', linestyle='--', alpha=0.5, label='Initial value')
    plt.legend()
    
    # Test accuracy evolution
    plt.subplot(1, 3, 3)
    plt.plot(test_acc_history, marker='o', color='green', linewidth=2, markersize=6)
    plt.title('Test Accuracy with AutoGELU', fontsize=14)
    plt.xlabel('Epoch')
    plt.ylabel('Test Accuracy (%)')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    filename = 'experiment2_parameter_evolution.pdf'
    plt.savefig(filename, dpi=150)
    print(f"\nPlot saved as {filename}")
    plt.close()
    
    # Print parameter statistics
    print("\n" + "-"*40)
    print("Parameter Evolution Statistics:")
    print(f"Alpha - Initial: 1.0000, Final: {alpha_history[-1]:.4f}, Change: {alpha_history[-1] - 1.0:.4f}")
    print(f"Beta  - Initial: 0.0447, Final: {beta_history[-1]:.4f}, Change: {beta_history[-1] - 0.044715:.4f}")
    print(f"Final Test Accuracy: {test_acc_history[-1]:.2f}%")
    
    return alpha_history, beta_history, test_acc_history

# ---------------------------
# Experiment 3: Gradient Flow Analysis
# ---------------------------
def experiment3_gradient_flow(test_mode=False):
    print("\n" + "="*60)
    print("EXPERIMENT 3: Gradient Flow Analysis on Deep Networks")
    print("="*60)
    
    # Data preparation for MNIST
    mnist_transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    
    mnist_train = MNIST(root='./data', train=True, download=True, transform=mnist_transform)
    mnist_test = MNIST(root='./data', train=False, download=True, transform=mnist_transform)
    
    batch_size = 128 if not test_mode else 64
    epochs = 5 if not test_mode else 2
    
    trainloader = torch.utils.data.DataLoader(mnist_train, batch_size=batch_size, shuffle=True, num_workers=2)
    testloader = torch.utils.data.DataLoader(mnist_test, batch_size=batch_size, shuffle=False, num_workers=2)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Create deep models
    num_layers = 10
    print(f"\nCreating deep MLP with {num_layers} hidden layers...")
    
    # Train with GELU
    print("\nTraining DeepMLP with fixed GELU...")
    model_deep_gelu = DeepMLP(
        activation=gelu,
        activation_name="GELU",
        input_dim=28*28,
        hidden_dim=512,
        num_layers=num_layers,
        num_classes=10
    )
    grad_norms_gelu = train_deep_model(model_deep_gelu, trainloader, epochs=epochs, lr=0.01, device=device)
    
    # Train with AutoGELU
    print("\nTraining DeepMLP with AutoGELU...")
    auto_gelu_deep = AutoGELU()
    model_deep_autogelu = DeepMLP(
        activation=auto_gelu_deep,
        activation_name="AutoGELU",
        input_dim=28*28,
        hidden_dim=512,
        num_layers=num_layers,
        num_classes=10
    )
    grad_norms_autogelu = train_deep_model(model_deep_autogelu, trainloader, epochs=epochs, lr=0.01, device=device)
    
    # Plot gradient norms for multiple layers
    plt.figure(figsize=(15, 10))
    
    # Select layers to visualize (first, middle, last)
    layers_to_plot = [0, num_layers//2, num_layers-1]
    
    for idx, layer_idx in enumerate(layers_to_plot):
        plt.subplot(2, 2, idx+1)
        
        if layer_idx < len(grad_norms_gelu[0]):
            epochs_range = list(range(1, len(grad_norms_gelu)+1))
            gelu_norms = [epoch_norms[layer_idx] for epoch_norms in grad_norms_gelu]
            autogelu_norms = [epoch_norms[layer_idx] for epoch_norms in grad_norms_autogelu]
            
            plt.plot(epochs_range, gelu_norms, marker='o', label='GELU', linewidth=2, markersize=6)
            plt.plot(epochs_range, autogelu_norms, marker='s', label='AutoGELU', linewidth=2, markersize=6)
            plt.xlabel('Epoch')
            plt.ylabel('Average Gradient L2 Norm')
            plt.title(f'Gradient Flow in Layer {layer_idx+1}', fontsize=12)
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.yscale('log')  # Log scale to better visualize differences
    
    # Overall gradient norm comparison
    plt.subplot(2, 2, 4)
    mean_gelu = [np.mean(epoch_norms) for epoch_norms in grad_norms_gelu]
    mean_autogelu = [np.mean(epoch_norms) for epoch_norms in grad_norms_autogelu]
    plt.plot(epochs_range, mean_gelu, marker='o', label='GELU (mean)', linewidth=2, markersize=6)
    plt.plot(epochs_range, mean_autogelu, marker='s', label='AutoGELU (mean)', linewidth=2, markersize=6)
    plt.xlabel('Epoch')
    plt.ylabel('Mean Gradient L2 Norm')
    plt.title('Average Gradient Norm Across All Layers', fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.yscale('log')
    
    plt.tight_layout()
    filename = 'experiment3_gradient_flow.pdf'
    plt.savefig(filename, dpi=150)
    print(f"\nPlot saved as {filename}")
    plt.close()
    
    # Print gradient statistics
    print("\n" + "-"*40)
    print("Gradient Flow Statistics:")
    print(f"GELU - Mean gradient norm (final epoch): {mean_gelu[-1]:.6f}")
    print(f"AutoGELU - Mean gradient norm (final epoch): {mean_autogelu[-1]:.6f}")
    print(f"Ratio (AutoGELU/GELU): {mean_autogelu[-1]/mean_gelu[-1]:.4f}")
    
    return grad_norms_gelu, grad_norms_autogelu

# ---------------------------
# Main Test Function
# ---------------------------
def test():
    """Run all experiments in test mode (fewer epochs for quick verification)"""
    print("\n" + "#"*60)
    print("# Running AutoGELU Experiments in TEST MODE")
    print("# (Using fewer epochs for quick verification)")
    print("#"*60)
    
    # Experiment 1
    exp1_results = experiment1_activation_comparison(test_mode=True)
    
    # Experiment 2
    alpha_hist, beta_hist, acc_hist = experiment2_parameter_evolution(test_mode=True)
    
    # Experiment 3
    grad_gelu, grad_autogelu = experiment3_gradient_flow(test_mode=True)
    
    print("\n" + "#"*60)
    print("# All experiments completed successfully!")
    print("# PDF plots have been saved to the current directory.")
    print("#"*60)
    
    # List generated files
    import os
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf') and 'experiment' in f]
    if pdf_files:
        print("\nGenerated PDF files:")
        for f in sorted(pdf_files):
            print(f"  - {f}")

def main():
    """Run all experiments with full training"""
    print("\n" + "#"*60)
    print("# Running AutoGELU Experiments")
    print("#"*60)
    
    # Experiment 1
    exp1_results = experiment1_activation_comparison(test_mode=False)
    
    # Experiment 2
    alpha_hist, beta_hist, acc_hist = experiment2_parameter_evolution(test_mode=False)
    
    # Experiment 3
    grad_gelu, grad_autogelu = experiment3_gradient_flow(test_mode=False)
    
    print("\n" + "#"*60)
    print("# All experiments completed!")
    print("# PDF plots have been saved to the current directory.")
    print("#"*60)
    
    # List generated files
    import os
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf') and 'experiment' in f]
    if pdf_files:
        print("\nGenerated PDF files:")
        for f in sorted(pdf_files):
            print(f"  - {f}")

if __name__ == "__main__":
    # Run test mode by default for quick verification
    # Change to main() for full experiments
    test()