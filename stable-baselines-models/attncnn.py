import gym
import numpy as np
import matplotlib.pyplot as plt
import os
#import tensorflow as tf

from micro_rct.gym_envs.rct_env import RCT

from stable_baselines3 import A2C
#from stable_baselines3.common.policies import MlpLstmPolicy
from stable_baselines3.common.policies import SelfAttnCnnPolicy
#from stable_baselines3.a2c import MlpPolicy
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import SubprocVecEnv, DummyVecEnv
#from stable_baselines3.common.noise import NormalActionNoise
from stable_baselines3.common.utils import set_random_seed
from stable_baselines3.common.callbacks import CheckpointCallback
from typing import Callable
import tensorflow as tf


def make_RCT_env(rank: int, seed: int = 0) -> Callable:
    """
    Utility function for multiprocessed env.
    
    :param env_id: (str) the environment ID
    :param num_env: (int) the number of environment you wish to have in subprocesses
    :param seed: (int) the inital seed for RNG
    :param rank: (int) index of the subprocess
    :return: (Callable)
    """
    def _init() -> gym.Env:
        env = RCT(settings_path='configs/settings.yml')
        #env = RCT(settings_path='/home/mae236/DeepLearning/micro-rct/configs/settings.yml')
        env.seed(seed + rank)
        env = Monitor(env, log_dir)
        return env
    set_random_seed(seed)
    return _init

if __name__ == '__main__':
    num_cpu = 1  # Number of processes to use
    # Create the vectorized environment
    tb_logs = "./tmp/test"
    os.makedirs(tb_logs, exist_ok=True)

    log_dir = "./tmp/test-log"
    os.makedirs(log_dir, exist_ok=True)

    model_dir = "./tmp/models"

    #tf.debugging.experimental.enable_dump_debug_info(tb_logs, tensor_debug_mode="FULL_HEALTH", circular_buffer_size=-1)

    env = DummyVecEnv([make_RCT_env(rank=i, seed=0) for i in range(num_cpu)])
    #env = SubprocVecEnv([make_RCT_env(rank=1, seed=0) for i in range(num_cpu)])

    attncnn= A2C(SelfAttnCnnPolicy, env, learning_rate = 1e-5, tensorboard_log=tb_logs, verbose=1)

    callback = CheckpointCallback(save_freq = int(4.2e5), save_path = model_dir)

    try:
      attncnn.learn(total_timesteps=int(1e8), callback = callback)
      attncnn.save("./tmp/model")
    except KeyboardInterrupt:
      attncnn.save("./tmp/model")
