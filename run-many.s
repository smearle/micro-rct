exp=$1
subexp=$2
start=$3
end=$4
echo "Experiment: $exp"
echo "SubExperiment: $subexp"
echo "From $start to $end"


for i in $(seq $start $end); do
	sbatch run.s -e $exp -s $subexp -c $i
	echo $i
done;
