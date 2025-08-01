#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Quick test to verify experiment setup"""

import torch
import numpy as np
import matplotlib.pyplot as plt
import os

print("="*60)
print("QUICK TEST: Verifying AutoGELU Experiment Setup")
print("="*60)

# Test imports
print("\n✓ PyTorch version:", torch.__version__)
print("✓ NumPy version:", np.__version__)
print("✓ CUDA available:", torch.cuda.is_available())

# Test AutoGELU implementation
class AutoGELU(torch.nn.Module):
    def __init__(self):
        super(AutoGELU, self).__init__()
        self.alpha = torch.nn.Parameter(torch.tensor(1.0))
        self.beta = torch.nn.Parameter(torch.tensor(0.044715))
    
    def forward(self, x):
        return x * 0.5 * (1 + torch.tanh(np.sqrt(2/np.pi) * (self.alpha * x + self.beta * torch.pow(x, 3))))

# Test activation
autogelu = AutoGELU()
x = torch.randn(10, 10)
output = autogelu(x)
print("\n✓ AutoGELU test passed. Output shape:", output.shape)

# Create a simple plot
plt.figure(figsize=(8, 6))
x_vals = torch.linspace(-3, 3, 100)
y_vals = autogelu(x_vals).detach().numpy()
plt.plot(x_vals.numpy(), y_vals, 'b-', linewidth=2)
plt.title('AutoGELU Activation Function')
plt.xlabel('Input')
plt.ylabel('Output')
plt.grid(True, alpha=0.3)
plt.savefig('quick_test_plot.pdf')
print("\n✓ Test plot saved as quick_test_plot.pdf")

print("\n" + "="*60)
print("All tests passed! Ready to run full experiments.")
print("="*60)