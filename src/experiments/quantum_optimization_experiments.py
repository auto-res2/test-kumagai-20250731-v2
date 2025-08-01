import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
from time import time
import torch.nn.functional as F

class QuantumInspiredOptimizer(torch.optim.Optimizer):
    """Quantum-inspired optimizer with tunneling and entanglement"""
    def __init__(self, params, lr=0.01, quantum_noise=0.1, tunneling_prob=0.1):
        defaults = dict(lr=lr, quantum_noise=quantum_noise, tunneling_prob=tunneling_prob)
        super(QuantumInspiredOptimizer, self).__init__(params, defaults)
        
        # Initialize quantum state
        for group in self.param_groups:
            for p in group['params']:
                state = self.state[p]
                state['momentum'] = torch.zeros_like(p.data)
                state['quantum_phase'] = torch.randn_like(p.data)
                state['tunneling_count'] = 0
    
    def step(self):
        for group in self.param_groups:
            for p in group['params']:
                if p.grad is None:
                    continue
                
                grad = p.grad.data
                state = self.state[p]
                momentum = state['momentum']
                quantum_phase = state['quantum_phase']
                
                # Quantum noise injection
                quantum_noise = group['quantum_noise']
                quantum_perturbation = quantum_noise * torch.randn_like(grad) * quantum_phase
                
                # Quantum tunneling
                if torch.rand(1).item() < group['tunneling_prob']:
                    # Tunnel through local minima
                    tunnel_direction = torch.randn_like(grad)
                    grad = grad + 0.5 * tunnel_direction
                    state['tunneling_count'] += 1
                
                # Update momentum with quantum effects
                momentum.mul_(0.9).add_(grad + quantum_perturbation)
                
                # Entanglement-inspired coupling
                if hasattr(self, 'global_quantum_state'):
                    coupling = 0.01 * self.global_quantum_state.mean()
                    momentum.add_(coupling)
                
                # Update parameters
                p.data.add_(momentum, alpha=-group['lr'])
                
                # Update quantum phase
                quantum_phase.mul_(0.99).add_(torch.randn_like(quantum_phase), alpha=0.01)

def create_cnn_model():
    """Create CNN for CIFAR-10"""
    return nn.Sequential(
        nn.Conv2d(3, 32, 3, padding=1),
        nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Conv2d(32, 64, 3, padding=1),
        nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Flatten(),
        nn.Linear(64 * 8 * 8, 128),
        nn.ReLU(),
        nn.Linear(128, 10)
    )

def run_comparison_experiment():
    """Compare quantum optimizer with standard optimizers"""
    print("=" * 80)
    print("QUANTUM-INSPIRED NEURAL NETWORK OPTIMIZATION EXPERIMENT")
    print("=" * 80)
    
    # Create synthetic CIFAR-10-like data
    print("\nGenerating synthetic dataset...")
    train_size = 5000
    test_size = 1000
    X_train = torch.randn(train_size, 3, 32, 32)
    y_train = torch.randint(0, 10, (train_size,))
    X_test = torch.randn(test_size, 3, 32, 32)
    y_test = torch.randint(0, 10, (test_size,))
    
    # Optimizers to compare
    optimizers_config = [
        ('SGD', lambda p: torch.optim.SGD(p, lr=0.01, momentum=0.9)),
        ('Adam', lambda p: torch.optim.Adam(p, lr=0.001)),
        ('QuantumInspired', lambda p: QuantumInspiredOptimizer(p, lr=0.01, quantum_noise=0.1))
    ]
    
    results = {}
    
    for opt_name, opt_fn in optimizers_config:
        print(f"\n{'='*60}")
        print(f"Training with {opt_name}")
        print('='*60)
        
        model = create_cnn_model()
        optimizer = opt_fn(model.parameters())
        criterion = nn.CrossEntropyLoss()
        
        train_losses = []
        test_accuracies = []
        train_times = []
        
        # Training
        epochs = 20
        batch_size = 64
        
        for epoch in range(epochs):
            model.train()
            epoch_loss = 0
            correct = 0
            total = 0
            start_time = time()
            
            # Mini-batch training
            for i in range(0, len(X_train), batch_size):
                batch_X = X_train[i:i+batch_size]
                batch_y = y_train[i:i+batch_size]
                
                optimizer.zero_grad()
                outputs = model(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
                
                epoch_loss += loss.item()
                _, predicted = outputs.max(1)
                total += batch_y.size(0)
                correct += predicted.eq(batch_y).sum().item()
            
            train_time = time() - start_time
            train_times.append(train_time)
            
            # Evaluation
            model.eval()
            with torch.no_grad():
                test_outputs = model(X_test)
                _, test_predicted = test_outputs.max(1)
                test_acc = test_predicted.eq(y_test).sum().item() / len(y_test)
            
            train_losses.append(epoch_loss / (len(X_train) / batch_size))
            test_accuracies.append(test_acc)
            
            if epoch % 5 == 0:
                print(f"Epoch {epoch:3d}: Loss={train_losses[-1]:.4f}, "
                      f"Train Acc={correct/total:.3f}, Test Acc={test_acc:.3f}, "
                      f"Time={train_time:.2f}s")
        
        # Store results
        results[opt_name] = {
            'train_losses': train_losses,
            'test_accuracies': test_accuracies,
            'train_times': train_times,
            'final_loss': train_losses[-1],
            'final_accuracy': test_accuracies[-1],
            'total_time': sum(train_times),
            'convergence_epoch': np.argmax(test_accuracies) + 1
        }
        
        # Quantum-specific metrics
        if opt_name == 'QuantumInspired':
            total_tunneling = sum(state.get('tunneling_count', 0) 
                                for state in optimizer.state.values())
            results[opt_name]['tunneling_events'] = total_tunneling
            print(f"\nQuantum tunneling events: {total_tunneling}")
    
    # Print comprehensive results
    print("\n" + "="*80)
    print("FINAL RESULTS COMPARISON")
    print("="*80)
    
    for opt_name, metrics in results.items():
        print(f"\n{opt_name}:")
        print(f"  Final Loss: {metrics['final_loss']:.4f}")
        print(f"  Final Test Accuracy: {metrics['final_accuracy']:.3f}")
        print(f"  Total Training Time: {metrics['total_time']:.2f}s")
        print(f"  Best Accuracy Epoch: {metrics['convergence_epoch']}")
        if 'tunneling_events' in metrics:
            print(f"  Quantum Tunneling Events: {metrics['tunneling_events']}")
    
    # Performance comparison
    print("\n" + "="*80)
    print("PERFORMANCE COMPARISON vs SGD")
    print("="*80)
    
    sgd_acc = results['SGD']['final_accuracy']
    sgd_time = results['SGD']['total_time']
    
    for opt_name in ['Adam', 'QuantumInspired']:
        acc_improvement = (results[opt_name]['final_accuracy'] - sgd_acc) / sgd_acc * 100
        time_ratio = results[opt_name]['total_time'] / sgd_time
        
        print(f"\n{opt_name}:")
        print(f"  Accuracy Improvement: {acc_improvement:+.1f}%")
        print(f"  Time Factor: {time_ratio:.2f}x")
        print(f"  Efficiency Score: {acc_improvement / time_ratio:.2f}")
    
    # Create visualization
    plt.figure(figsize=(15, 5))
    
    # Loss curves
    plt.subplot(1, 3, 1)
    for opt_name in results:
        plt.plot(results[opt_name]['train_losses'], label=opt_name)
    plt.xlabel('Epoch')
    plt.ylabel('Training Loss')
    plt.title('Training Loss Comparison')
    plt.legend()
    plt.grid(True)
    
    # Accuracy curves
    plt.subplot(1, 3, 2)
    for opt_name in results:
        plt.plot(results[opt_name]['test_accuracies'], label=opt_name)
    plt.xlabel('Epoch')
    plt.ylabel('Test Accuracy')
    plt.title('Test Accuracy Comparison')
    plt.legend()
    plt.grid(True)
    
    # Final comparison bar chart
    plt.subplot(1, 3, 3)
    opt_names = list(results.keys())
    final_accs = [results[opt]['final_accuracy'] for opt in opt_names]
    plt.bar(opt_names, final_accs)
    plt.ylabel('Final Test Accuracy')
    plt.title('Final Performance Comparison')
    plt.ylim(0, 1)
    for i, v in enumerate(final_accs):
        plt.text(i, v + 0.01, f'{v:.3f}', ha='center')
    
    plt.tight_layout()
    plt.savefig('quantum_optimization_comprehensive_results.pdf')
    print("\nResults saved to quantum_optimization_comprehensive_results.pdf")

if __name__ == "__main__":
    run_comparison_experiment()
