import gym
from gym_micro_rct.envs.rct_env import RCT
from stable_baselines3 import A2C
from stable_baselines3.a2c import MlpPolicy
from stable_baselines3.common.env_util import make_vec_env

env = RCT(settings_path='configs/settings.yml')

model = A2C(MlpPolicy, env)
model.learn(total_timesteps=5000)
