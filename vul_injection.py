import os
import sys
import random

arch = sys.argv[1]
bench = sys.argv[2]
component = sys.argv[3]

if(bench == 'hello'):
	runtime = 16169500
elif(bench == 'matmul'):
	runtime = 84996000
elif(bench == 'stringsearch'):
	runtime = 138149500
elif(bench == 'susan'):
	runtime = 1540836000
elif(bench == 'jpeg'):
	runtime = 9902426000
elif(bench == 'gsm'):
	runtime = 9985126500
elif(bench == 'bitcount'):
	runtime = 12314086500
elif(bench == 'qsort'):
	runtime = 13467377000
elif(bench == 'dijkstra'):
	runtime = 25391777500
elif(bench == 'basicmath'):
	runtime = 25391777500
	
data = file("input_"+bench+".txt")

for line in data:
	line2 = line.strip().split('\t')
	#print line2
	if bench == 'susan' or bench == 'jpeg':
		os.system("./compare_output.sh " +str(arch) + " " + str(bench) + " " + str(line2[0]) + " " + str(line2[1]) + " " + str(runtime*2) + " " + component)
	else:
		os.system("./compare.sh " +str(arch) + " " + str(bench) + " " + str(line2[0]) + " " + str(line2[1]) + " " + str(runtime*2) + " " + component)