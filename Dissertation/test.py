import gym
import cyberbattle.simulation.model as model
import numpy as np

# 1. Create the Environment (Small 10-node Chain)
# This mimics a simple network: PC -> Router -> Server -> ...
env = gym.make('CyberBattleChain-v0', size=10, attacker_goal=model.TargetToken(0))

print(f"Network created with {len(list(env.environment.network.nodes))} nodes.")

# 2. Run the Experiment (The 'Random' Hacker)
episodes = 5  # Let's play 5 games
max_steps = 100 # Give up after 100 moves

for game in range(episodes):
    obs = env.reset()
    total_reward = 0
    steps_taken = 0
    
    print(f"\n--- Game {game+1} Started ---")
    
    for step in range(max_steps):
        # The 'Random' Strategy: Pick any valid button
        action = env.sample_valid_action()
        
        if action:
            obs, reward, done, info = env.step(action)
            total_reward += reward
            steps_taken += 1
            
            # Use 'done' to check if we won
            if done:
                print(f"WINNER! Hacked the admin in {steps_taken} steps!")
                break
        else:
            # If no valid actions, just wait (this happens if scanned everything)
            pass
            
    print(f"Game Over. Total Score: {total_reward}")

env.close()
