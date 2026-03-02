import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import random
from cyberbattle._env.cyberbattle_chain import CyberBattleChain
from cyberbattle._env.flatten_wrapper import FlattenActionWrapper

# 1. SIMPLE NEURAL NETWORK
class SimpleQNetwork(nn.Module):
    def __init__(self, input_dim, output_dims):
        super(SimpleQNetwork, self).__init__()
        self.fc1 = nn.Linear(input_dim, 64)
        self.fc2 = nn.Linear(64, 64)
        
        # We need separate output heads for each part of the MultiDiscrete action
        # Actions are usually: [SourceNode, TargetNode, Port, etc.]
        self.heads = nn.ModuleList([nn.Linear(64, dim) for dim in output_dims])
        
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return [head(x) for head in self.heads]

# 2. FEATURE EXTRACTOR
def extract_features(env):
    total = env.environment.network.number_of_nodes()
    owned = len(env.environment.owned_nodes)
    creds = len(env.environment.credential_cache)
    return np.array([owned/total, creds/50.0], dtype=np.float32)

# 3. MAIN TRAINING LOOP
def train_dqn(size, episodes=500):
    print(f"\n--- Training DQN on Chain(size={size}) ---")
    
    # Setup Env
    raw_env = CyberBattleChain(size=size, observation_padding=False)
    env = FlattenActionWrapper(raw_env)
    
    # Get Action Dimensions (e.g., [10, 50, 50...])
    # The action space is MultiDiscrete, so we check .nvec
    action_dims = env.action_space.nvec.tolist()
    
    # Setup AI
    input_dim = 2 
    model = SimpleQNetwork(input_dim, action_dims)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    wins = 0
    epsilon = 1.0 
    
    for episode in range(episodes):
        env.reset()
        state = extract_features(env)
        state_tensor = torch.FloatTensor(state)
        
        done = False
        steps = 0
        total_reward = 0
        
        while not done and steps < 2000:
            # Choose Action
            if random.random() < epsilon:
                action = env.action_space.sample()
            else:
                with torch.no_grad():
                    q_values_list = model(state_tensor)
                    # Pick best sub-action for each head
                    action = np.array([torch.argmax(q).item() for q in q_values_list])
            
            # Step
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            
            # Learn (Simplified)
            next_state = extract_features(env)
            next_state_tensor = torch.FloatTensor(next_state)
            
            # Calculate Target (Sum of max Qs across all heads)
            target_val = reward
            if not done:
                next_qs = model(next_state_tensor)
                target_val += 0.99 * sum([torch.max(q).item() for q in next_qs])
            
            # Current Prediction
            curr_qs = model(state_tensor)
            
            # Loss is sum of losses for each head
            loss = 0
            for i, sub_action in enumerate(action):
                pred = curr_qs[i][sub_action]
                # We distribute the target value across heads (simplified strategy)
                sub_target = target_val / len(action) 
                loss += (pred - sub_target) ** 2
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            state_tensor = next_state_tensor
            steps += 1
            total_reward += reward
            
            if reward > 0 and done: 
                wins += 1
        
        epsilon = max(0.1, epsilon * 0.995)
        
        if (episode+1) % 10 == 0:
            print(f"Episode {episode+1}: Win Rate: {wins/(episode+1):.2%}")

    print(f"Final Win Rate (Size {size}): {wins/episodes:.2%}")

if __name__ == "__main__":
    train_dqn(size=10, episodes=50)
    train_dqn(size=50, episodes=50)
