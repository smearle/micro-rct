
from stable_baselines3.common.env_checker import check_env
from gym_micro_rct.envs.rct_env import RCT


env = RCT(settings_path='configs/settings.yml')

# It will check your custom environment and output additional warnings if needed
check_env(env, warn=True)