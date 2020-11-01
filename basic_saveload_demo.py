
import gym
from stable_baselines3 import DQN, A2C
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.evaluation import evaluate_policy

from gym_micro_rct.envs.rct_env import RCT

env = RCT(settings_path='configs/settings.yml')

# It will check your custom environment and output additional warnings if needed
check_env(env, warn=True)

# Instantiate the agent
model = A2C('MlpPolicy', env, learning_rate=1e-3,  # prioritized_replay=True,
        verbose=1)
# Train the agent
model.learn(total_timesteps=int(2e5))
# Save the agent
model.save("rct_test_0")
del model  # delete trained model to demonstrate loading

# Load the trained agent
model = A2C.load("rct_test_0")

# Evaluate the agent
mean_reward, std_reward = evaluate_policy(model, model.get_env(), n_eval_episodes=10)

# Enjoy trained agent
obs = env.reset()

for i in range(1000):
    action, _states = model.predict(obs)
    obs, rewards, dones, info = env.step(action)
    env.render()
