#!/bin/bash
#
#SBATCH --job-name=RCT_ME
#SBATCH --nodes=1 --ntasks-per-node=1
#SBATCH --cpus-per-task=48
#SBATCH --time=24:00:00
#SBATCH --mem=20GB
#SBATCH --output=/scratch/mcg520/micro_rct_me/logs/%A.out
#SBATCH --error=/scratch/mcg520/micro_rct_me/logs/%A.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=mike.green@nyu.edu


module purge
#module load jdk/1.8.0_111


while getopts e:c: flag
do
	case "${flag}" in
		e) experiment=${OPTARG};;
		c) count=${OPTARG};;
	esac
done


sed -i "s/%DIR%/$count/g" /scratch/mcg520/micro_rct_me/$experiment/$count/settings.yml

singularity exec --nv --overlay /scratch/mcg520/micro_rct_me/rct_overlay.ext3:ro /scratch/work/public/singularity/cuda11.0-cudnn8-devel-ubuntu18.04.sif bash -c "source 
/ext3/env.sh; python vanilla_map_elites.py --settings-path /scratch/mcg520/micro_rct_me/$experiment/$count/settings.yml"

# python vanilla_map_elites.py --settings-path /scratch/mcg520/micro_rct_me/$experiment/$count/settings.yml

#BLANK LINE UNDER THS LINE. SACRIFICE TO THE CARRIAGE RETURN GODS.
