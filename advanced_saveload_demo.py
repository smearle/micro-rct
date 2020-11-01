from stable_baselines3 import SAC
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.sac.policies import CnnPolicy
import gym_micro_rct

# Create the model, the training environment
# and the test environment (for evaluation)
model = SAC('CnnPolicy', 'RCT-v0', verbose=1,
            learning_rate=1e-3, create_eval_env=True)

# Evaluate the model every 1000 steps on 5 test episodes
# and save the evaluation to the "logs/" folder
model.learn(6000, eval_freq=1000, n_eval_episodes=5, eval_log_path="./logs/")

# save the model
model.save("sac_rct")

# the saved model does not contain the replay buffer
loaded_model = SAC.load("sac_rct")
print(f"The loaded_model has {loaded_model.replay_buffer.size()} transitions in its buffer")

# now save the replay buffer too
model.save_replay_buffer("sac_replay_buffer")

# load it into the loaded_model
loaded_model.load_replay_buffer("sac_replay_buffer")

# now the loaded replay is not empty anymore
print(f"The loaded_model has {loaded_model.replay_buffer.size()} transitions in its buffer")

# Save the policy independently from the model
# Note: if you don't save the complete model with `model.save()`
# you cannot continue training afterward
policy = model.policy
policy.save("sac_policy_rct.pkl")

# Retrieve the environment
env = model.get_env()

# Evaluate the policy
mean_reward, std_reward = evaluate_policy(policy, env, n_eval_episodes=10, deterministic=True)

print(f"mean_reward={mean_reward:.2f} +/- {std_reward}")

# Load the policy independently from the model
saved_policy = CnnPolicy.load("sac_policy_rct")

# Evaluate the loaded policy
mean_reward, std_reward = evaluate_policy(saved_policy, env, n_eval_episodes=10, deterministic=True)

print(f"mean_reward={mean_reward:.2f} +/- {std_reward}")
