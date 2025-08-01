# Graph Neural Networks for Protein-Protein Interaction
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import matplotlib.pyplot as plt

class ProteinGNN(nn.Module):
    """Graph Neural Network for protein-protein interaction prediction"""
    
    def __init__(self, input_dim, hidden_dim, output_dim):
        super(ProteinGNN, self).__init__()
        self.conv1 = GraphConvLayer(input_dim, hidden_dim)
        self.conv2 = GraphConvLayer(hidden_dim, hidden_dim)
        self.conv3 = GraphConvLayer(hidden_dim, output_dim)
        self.dropout = nn.Dropout(0.2)
    
    def forward(self, x, edge_index):
        x = F.relu(self.conv1(x, edge_index))
        x = self.dropout(x)
        x = F.relu(self.conv2(x, edge_index))
        x = self.dropout(x)
        x = self.conv3(x, edge_index)
        return x

class GraphConvLayer(nn.Module):
    """Simple graph convolution layer"""
    
    def __init__(self, in_features, out_features):
        super(GraphConvLayer, self).__init__()
        self.linear = nn.Linear(in_features, out_features)
        self.neighbor_linear = nn.Linear(in_features, out_features)
    
    def forward(self, x, edge_index):
        # Self connections
        self_features = self.linear(x)
        
        # Aggregate neighbor features
        neighbor_features = torch.zeros_like(self_features)
        for i, j in edge_index.t():
            neighbor_features[i] += x[j]
        
        neighbor_features = self.neighbor_linear(neighbor_features)
        
        return self_features + neighbor_features

def test_protein_gnn():
    """Test GNN on synthetic protein interaction data"""
    
    # Create synthetic protein network
    num_proteins = 100
    num_features = 50
    
    # Node features (protein properties)
    X = torch.randn(num_proteins, num_features)
    
    # Create edges (protein interactions)
    num_edges = 300
    edge_index = torch.randint(0, num_proteins, (2, num_edges))
    
    # Create model
    model = ProteinGNN(num_features, 64, 16)
    
    # Forward pass
    embeddings = model(X, edge_index)
    
    # Compute pairwise interaction scores
    scores = torch.matmul(embeddings, embeddings.t())
    
    # Visualize interaction matrix
    plt.figure(figsize=(10, 8))
    plt.imshow(scores.detach().numpy(), cmap='RdBu_r')
    plt.colorbar(label='Interaction Score')
    plt.title('Predicted Protein-Protein Interactions')
    plt.xlabel('Protein Index')
    plt.ylabel('Protein Index')
    plt.savefig('protein_interaction_heatmap.pdf')
    
    print(f"Generated interaction predictions for {num_proteins} proteins")
    print(f"Number of strong interactions (>0.5): {(scores > 0.5).sum().item()}")

if __name__ == "__main__":
    test_protein_gnn()
