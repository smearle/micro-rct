''' Render and debug. '''
from rct_env import RCTEnv

def main():
    env = RCTEnv(render=True)
    env.reset()
    env.simulate()

if __name__ == "__main__":
    main()
