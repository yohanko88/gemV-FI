bench_home="/home/yonsei_dclab/yohan/miBench"

case "$2" in
hello )
  bench="helloWorld/hello_$1"
  options=""
  ;;
matmul )
  bench="matrixmul/matmul_$1"
  options=""
  ;;
qsort )
  bench="automotive/qsort/qsort_small_$1"
  options="$bench_home/automotive/qsort/input_small.dat"
  ;;
stringsearch )
  bench="office/stringsearch/search_small_$1"
  options=""
  ;;
susan )
  bench="/automotive/susan/susan_$1"
  options="$bench_home/automotive/susan/input_small.pgm output_small.smoothing.pgm -e"
  ;;
dijkstra )
  bench="network/dijkstra/dijkstra_small_$1"
  options="$bench_home/network/dijkstra/input.dat"
  ;;
jpeg )
  bench="consumer/jpeg/jpeg-6a/cjpeg_$1"
  options="-dct int -progressive -opt -outfile output_small_encode.jpeg $bench_home/consumer/jpeg/input_small.ppm"
  ;;
bitcount )
  bench="automotive/bitcount/bitcnts_$1"
  options=75000
  ;;
gsm )
  bench="telecomm/gsm/bin/toast_$1"
  options="-fps -c $bench_home/telecomm/gsm/data/small.au"
  ;;
basicmath ) 
  bench="automotive/basicmath/basicmath_small_$1"
  options=""
  ;;
fft )
  bench="telecomm/FFT/fft"
  options="4 4096"
  ;;
typese )
  bench="/consumer/typeset/lout-3.24/lout_arm"
  options=" -I $bench_home/consumer/typeset/lout-3.24/include -D $bench_home/consumer/typeset/lout-3.24/data -F $bench_home/consumer/typeset/lout-3.24/font -C $bench_home/consumer/typeset/lout-3.24/maps -H $bench_home/consumer/typeset/lout-3.24/hyph $bench_home/consumer/typeset/small.lout"
  ;;
crc )
  bench="telecomm/CRC32/crc_arm"
  options="$bench_home/telecomm/adpcm/data/large.pcm"
  ;;
patricia )
  bench="network/patricia/patricia"
  options="$bench_home/network/patricia/small.udp"
esac

protection=no_protection								# Protection scheme to be used
vul_analysis=yes								# Enable/Disable vulnerability analysis
cpu_type=arm_detailed								# CPU Type
num_procs=1									# Number of processors
num_l2=1									# Number of L2 caches
l1d_size=8kB									# Size of L1 Data cache
l1i_size=4kB									# Size of L1 Instruction cache
l2_size=32kB									# Size of L2 cacche
l1d_assoc=2									# L1 Data cache associativity
l1i_assoc=2									# L1 Instruction cache associativity
l2_assoc=4									# L2 associativity
cacheline_size=64					            			# Size of cache line
options3=~/benchmarks/mibench/automotive/qsort/input_small.dat					# Options to be passed to the binary. Add "-o $options" to the end of the command if any options exist.
#options=4 4096					# Options to be passed to the binary. Add "-o $options" to the end of the command if any options exist.
gemv_exec_path=./build/$1/gem5.opt		# Path to gemv executable
config_path=./configs/example/se.py		# Path to config file

$gemv_exec_path -d $2_trace -re --stdout-file=simout_$3_$4 --stderr-file=simerr_$3_$4 --debug-file=GR_$3_$4 --debug-flags=FI,Exec,-ExecTicks,RegTrace $config_path --cpu-type=$cpu_type --caches --l2cache -n $num_procs --num-l2caches=$num_l2 --l1d_size=$l1d_size --l1i_size=$l1i_size --l2_size=$l2_size --l1d_assoc=$l1d_assoc --l1i_assoc=$l1i_assoc --l2_assoc=$l2_assoc --cacheline_size=$cacheline_size --vul_analysis=$vul_analysis --cache_prot=$protection  -c "$bench_home/$bench" -o "$options" --output=$2_trace/result_$3_$4 --vul_params=./params.in --checkArch=$6 --injectTime=$3 --injectLoc=$4 -m $5 --maxTraceInst 1000

$gemv_exec_path -d $2_trace -re --stdout-file=simout_$3_$4 --stderr-file=simerr_$3_$4 --debug-file=FI_$3_$4 --debug-flags=FI,Exec,-ExecTicks,RegTrace $config_path --cpu-type=$cpu_type --caches --l2cache -n $num_procs --num-l2caches=$num_l2 --l1d_size=$l1d_size --l1i_size=$l1i_size --l2_size=$l2_size --l1d_assoc=$l1d_assoc --l1i_assoc=$l1i_assoc --l2_assoc=$l2_assoc --cacheline_size=$cacheline_size --vul_analysis=$vul_analysis --cache_prot=$protection  -c "$bench_home/$bench" -o "$options" --output=$2_trace/result_$3_$4 --vul_params=./params.in --injectArch=$6 --injectTime=$3 --injectLoc=$4 -m $5 --maxTraceInst=1000 #--traceFault=1 #--take-checkpoints 0,10000

#$gemv_exec_path -d $2_trace -re --stdout-file=simout_$3_$4 --stderr-file=simerr_$3_$4 --debug-file=FI_$3_$4 --debug-flags=FI,Exec,-ExecTicks,FaultTrace,RegTrace $config_path --cpu-type=$cpu_type --caches --l2cache -n $num_procs --num-l2caches=$num_l2 --l1d_size=$l1d_size --l1i_size=$l1i_size --l2_size=$l2_size --l1d_assoc=$l1d_assoc --l1i_assoc=$l1i_assoc --l2_assoc=$l2_assoc --cacheline_size=$cacheline_size --vul_analysis=$vul_analysis --cache_prot=$protection  -c "$bench_home/$bench" -o "$options" --output=$2_trace/result_$3_$4 --vul_params=./params.in --injectArch=RF --injectTime=$3 --injectLoc=$4 -m $5 --maxTraceInst=1000 --traceFault=1 #--take-checkpoints 0,10000
