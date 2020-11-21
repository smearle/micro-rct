import gym
import numpy as np
import matplotlib.pyplot as plt
import os
import pygame

from gym_micro_rct.envs.rct_env import RCT

from stable_baselines3 import A2C
from stable_baselines3.a2c import CnnPolicy
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common import results_plotter
from stable_baselines3.common.results_plotter import load_results, ts2xy
from stable_baselines3.common.noise import NormalActionNoise
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.policies import ActorCriticCnnPolicy

#video logging
from stable_baselines3.common.logger import Video
from stable_baselines3.common.evaluation import evaluate_policy
import torch as th
from typing import Any, Dict
from pygame.surfarray import array3d


class VideoRecorderCallback(BaseCallback):
    def __init__(self, eval_env: gym.Env, render_freq: int, n_eval_episodes: int = 1, deterministic: bool = True):
        """
        Records a video of an agent's trajectory traversing ``eval_env`` and logs it to TensorBoard

        :param eval_env: A gym environment from which the trajectory is recorded
        :param render_freq: Render the agent's trajectory every eval_freq call of the callback.
        :param n_eval_episodes: Number of episodes to render
        :param deterministic: Whether to use deterministic or stochastic policy
        """
        super().__init__()
        self._eval_env = eval_env
        self._render_freq = render_freq
        self._n_eval_episodes = n_eval_episodes
        self._deterministic = deterministic

    def _on_step(self) -> bool:
        if self.n_calls % self._render_freq == 0:
            screens = []

            def grab_screens(_locals: Dict[str, Any], _globals: Dict[str, Any]) -> None:
                """
                Renders the environment in its current state, recording the screen in the captured `screens` list

                :param _locals: A dictionary containing all local variables of the callback's scope
                :param _globals: A dictionary containing all global variables of the callback's scope
                """
                #screen = self._eval_env.render(mode="rgb_array")

                pg_surface = self._eval_env.rct_env.screen
                pg_array = array3d(pg_surface)
                screen = th.from_numpy(pg_array)
                # PyTorch uses CxHxW vs HxWxC gym (and tensorflow) image convention
                screens.append(screen.permute(2, 0, 1))

            evaluate_policy(
                self.model,
                self._eval_env,
                callback=grab_screens,
                n_eval_episodes=self._n_eval_episodes,
                deterministic=self._deterministic,
            )
            self.logger.record(
                "trajectory/video",
                Video(th.stack(screens), fps=10),
                #Video(th.ByteTensor([screens]), fps=10),
                exclude=("stdout", "log", "json", "csv"),
            )
        return True





log_dir = "./tmp/a2cCnn-log"
os.makedirs(log_dir, exist_ok=True)

#this dir is part of the info that gets printed in verbose

tb_logs = "./tmp/a2cCnn-tb"
os.makedirs(tb_logs, exist_ok=True)

env = RCT(settings_path='configs/settings.yml')
env = Monitor(env, log_dir)

#n_actions = env.action_space.shape[-1]
#action_noise = NormalActionNoise(mean=np.zeros(n_actions), sigma=0.1 * np.ones(n_actions))
#callback = SaveOnBestTrainingRewardCallback(check_freq=1000, log_dir=log_dir)

videocallback = VideoRecorderCallback(env, render_freq=50)

model = A2C(ActorCriticCnnPolicy, env, tensorboard_log = tb_logs, verbose=1)
try:
  model.learn(total_timesteps=int(9e9), callback = videocallback)
  model.save("./tmp/cnn")
except KeyboardInterrupt:
  model.save("./tmp/cnn")

