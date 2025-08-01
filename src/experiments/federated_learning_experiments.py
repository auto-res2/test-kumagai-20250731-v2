# Federated Learning with Differential Privacy
import torch
import torch.nn as nn
import numpy as np
from torch.utils.data import DataLoader, TensorDataset

class DPFederatedLearning:
    """Federated learning with differential privacy for healthcare"""
    
    def __init__(self, model, epsilon=1.0, delta=1e-5, num_clients=10):
        self.global_model = model
        self.epsilon = epsilon
        self.delta = delta
        self.num_clients = num_clients
        self.client_models = [self._copy_model() for _ in range(num_clients)]
    
    def _copy_model(self):
        """Create a copy of the model"""
        import copy
        return copy.deepcopy(self.global_model)
    
    def _add_noise(self, gradients, sensitivity=1.0):
        """Add Gaussian noise for differential privacy"""
        sigma = sensitivity * np.sqrt(2 * np.log(1.25 / self.delta)) / self.epsilon
        
        for grad in gradients:
            if grad is not None:
                noise = torch.randn_like(grad) * sigma
                grad.data += noise
    
    def train_round(self, client_data_loaders):
        """One round of federated training"""
        client_updates = []
        
        for client_id, data_loader in enumerate(client_data_loaders):
            # Local training
            model = self.client_models[client_id]
            model.load_state_dict(self.global_model.state_dict())
            
            optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
            criterion = nn.BCEWithLogitsLoss()
            
            for data, labels in data_loader:
                optimizer.zero_grad()
                outputs = model(data)
                loss = criterion(outputs, labels)
                loss.backward()
                
                # Add DP noise to gradients
                self._add_noise([p.grad for p in model.parameters()])
                
                optimizer.step()
            
            # Collect client update
            client_updates.append(model.state_dict())
        
        # Aggregate updates
        self._aggregate_models(client_updates)
    
    def _aggregate_models(self, client_updates):
        """Aggregate client models using FedAvg"""
        global_dict = self.global_model.state_dict()
        
        for key in global_dict.keys():
            global_dict[key] = torch.mean(
                torch.stack([client[key] for client in client_updates]), 
                dim=0
            )
        
        self.global_model.load_state_dict(global_dict)

# Test federated learning
def test_federated_learning():
    # Create synthetic healthcare data
    num_samples_per_client = 100
    num_features = 20
    num_clients = 5
    
    # Global model
    model = nn.Sequential(
        nn.Linear(num_features, 50),
        nn.ReLU(),
        nn.Linear(50, 1)
    )
    
    # Create client datasets
    client_loaders = []
    for i in range(num_clients):
        X = torch.randn(num_samples_per_client, num_features)
        y = (torch.randn(num_samples_per_client, 1) > 0).float()
        dataset = TensorDataset(X, y)
        loader = DataLoader(dataset, batch_size=32, shuffle=True)
        client_loaders.append(loader)
    
    # Initialize federated learning
    fl = DPFederatedLearning(model, epsilon=1.0, num_clients=num_clients)
    
    # Train for multiple rounds
    print("Training with differential privacy...")
    for round_num in range(10):
        fl.train_round(client_loaders)
        print(f"Round {round_num + 1} completed")
    
    print("Federated learning with DP completed successfully")

if __name__ == "__main__":
    test_federated_learning()
