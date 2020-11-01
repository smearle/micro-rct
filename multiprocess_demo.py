import gym
import numpy as np

from stable_baselines3.common.policies import ActorCriticCnnPolicy
from stable_baselines3.common.vec_env import SubprocVecEnv
from stable_baselines3.common.env_util import make_vec_env
#from stable_baselines3.common.utils import set_global_seeds
from stable_baselines3 import A2C
import gym_micro_rct
import argparse

def make_env(env_id, rank, seed=0):
    """
    Utility function for multiprocessed env.

    :param env_id: (str) the environment ID
    :param num_env: (int) the number of environments you wish to have in subprocesses
    :param seed: (int) the inital seed for RNG
    :param rank: (int) index of the subprocess
    """
    def _init():
        env = gym.make(env_id)
        env.seed(seed + rank)
        return env
   #set_global_seeds(seed)
    return _init

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--load", action='store_true')
    parser.add_argument('--experiment-name', default='test_0')
    env_id = "RCT-v0"
    num_cpu = 40  # Number of processes to use
    # Create the vectorized environment
    env = SubprocVecEnv([make_env(env_id, i) for i in range(num_cpu)])

    # Stable Baselines provides you with make_vec_env() helper
    # which does exactly the previous steps for you:
    # env = make_vec_env(env_id, n_envs=num_cpu, seed=0)

    model = A2C(ActorCriticCnnPolicy, env, verbose=1)
    model.learn(total_timesteps=1e7)

    obs = env.reset()
    for _ in range(1000):
        action, _states = model.predict(obs)
        obs, rewards, dones, info = env.step(action)
   #    env.render()
