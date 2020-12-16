# Deep Learning course project, Fall 2020

First, follow the instructions below to install the base micro-rct gym learning environment: `RCT-v0`, which is used both by our reinforcement learning project, and our concurrent work using evolution to evolve game maps. It is the combined work of Sam, Maria, and our teammates on the evolution project (notably Victoria Yen, who build the initial version of the environment, and Michael Green, who has focused mostly on applying evolution to the environment).

## Single-objective agents with (adapted) stable-baselines3

This code is the result of Maria's work adapting stable-baselines to our environment, experimenting with a range of neural architectures, and running extensive experiments to optimize for various objectives.

## Multi-objective agents with gym-city

This is a (somewhat!) stripped down version of Sam's [gym-city](https://github.com/smearle/gym-city/tree/micro-rct/multi-metrics) repo, adapted to work with micro-rct. To run a trained model, `cd gym-city`, install the requirements, some of which are contained in `requirements.txt` (though be warned that there are likely superfluous packages in here). You will need pytorch, most notably.

To run a trained model:

`python enjoy.py --load-dir trained_models/happiness_RCT-v0.tar --active-col 2 --non-det`

To train a single-objective model:

`python train.py --experiment happiness --env-name RCT-v0 --model MLPBase --num-proc 12`

To train a multi-objective model using ALP-GMM adapted for variable reward:

`python train_teacher.py --experiment happiness --env-name RCT-v0 --load --model MLPBase --env-params='happiness' --n-rand-envs 4 --num-proc 12`

Note that you can provide multiple strings to `env-params`, including any of: `num_rides`, `happiness`, `income`, `num_vomits`.

# micro-rct

This is micro-rct, a minimal theme park management sim inspired by RollerCoaster Tycoon and based on the implementation of [OpenRCT2](https://github.com/OpenRCT2/OpenRCT2). The project is intended as a test bed for experimental theme park-planning AI.



### Anaconda (optional) 
We recommend [installing anaconda](https://docs.anaconda.com/anaconda/install/), then creating a new environment using the latest version of python:
 
`conda create --name rct python=3.8`
 
To activate the conda environment:
 
 `conda activate rct`
 
## Installation
 
First, clone the repo:

`git clone https://github.com/smearle/micro-rct`
 
And install dependencies:
 
 `cd micro-rct`
 
 `python -m pip install -r requirements.txt`
 
## Use
 
 To run a park with a random layout, run:
 
 `python rct_env.py`
 
 In `rct_env.py`, set `RENDER = True` to render the park using sprites from the original game using pygame.
