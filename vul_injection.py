import os
import sys
import random

isa = sys.argv[1]
bench = sys.argv[2]

if(bench == 'stringsearch'):
	runtime = 138149500
elif(bench == 'matmul'):
	runtime = 20618500
elif(bench == 'qsort'):
	runtime = 13467377000
elif(bench == 'hello'):
	runtime = 16169500
elif(bench == 'bitcount'):
	runtime = 12314086500
elif(bench == 'susan'):
	runtime = 1528159500
elif(bench == 'dijkstra'):
	runtime = 25391777500
elif(bench == 'jpeg'):
	runtime = 9902426000
elif(bench == 'gsm'):
	runtime = 9985126500
elif(bench == 'basicmath'):
	runtime = 25391777500

data = file("input_"+bench+".txt")
for line1 in data:
	line2 = line1.strip().split('\t')
	os.system("./analysis.sh " +str(isa) + " " + str(bench) + " " + str(line2[2]) + " " + str(line2[3]) + " " + str(runtime*2))
	#print line2[2]