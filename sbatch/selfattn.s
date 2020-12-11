#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=12
#SBATCH --gres=gpu:1
#SBATCH --time=72:00:00
#SBATCH --mem=30GB
#SBATCH --job-name=mon_attn
#SBATCH --mail-type=END
#SBATCH --mail-user=mae236@nyu.edu
#SBATCH --output=slurm_mon_attn_%j.out

module purge
module load python/intel/3.8.6
RUNDIR=$HOME/DeepLearning/run-mon-${SLURM_JOB_ID/.*}
mkdir $RUNDIR
  
DATADIR=$HOME/DeepLearning
cd $RUNDIR
source $DATADIR/env/bin/activate

python3 $DATADIR/micro-rct/model_scripts/selfattn.py