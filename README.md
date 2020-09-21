# micro-rct

This is micro-rct, a minimal theme park management sim inspired by RollerCoaster Tycoon and based on the implementation of [OpenRCT2](https://github.com/OpenRCT2/OpenRCT2). The project is intended as a test bed for experimental theme park-planning AI.

## Installation

We recommend [installing anaconda](https://docs.anaconda.com/anaconda/install/), then creating a new environment using the latest version of python:
 
 `conda create --name rct python=3.8`
 
 Activate the conda environment:
 
 `conda activate rct`
 
 And install dependencies:
 
 `python -m pip install -r requirements.txt`
 
 ## Usage
 
 To run a park with a random layout, run:
 
 `python rct_env.py`
 
 In `rct_env.py`, set `RENDER = True` to render the park using sprites from the original game using pygame.
