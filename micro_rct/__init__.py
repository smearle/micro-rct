from gym.envs.registration import register

register(
        id='RCT-v0',
        entry_point='micro_rct.gym_envs:RCT',
        )
