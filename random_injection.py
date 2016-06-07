import os
import sys
import random

arch = sys.argv[1]
bench = sys.argv[2]
injectArch = sys.argv[3]
start = sys.argv[4]
end = sys.argv[5]

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

os.system("mkdir " + str(bench))
#f = open(str(bench) + "/val_" + str(injectArch)+"_"+str(start)+"_"+str(end)+".txt", 'w') 

for i in range(int(start), int(end)):
	if (injectArch == "NO"):
		injectLoc = 0
	if (injectArch == "RF"):
		injectLoc = random.randrange(0,8192) #32: Data (256 RFs)
	if (injectArch == "RenameMap"):
		injectLoc = random.randrange(0,912) #8: PhysRegIdx (114 Arch Regs)
	if (injectArch == "HistoryBuffer"):
		injectLoc = random.randrange(0,4730) #32: SeqNum, 7: ArchReg of history buffer, 8: NewPhysReg, 8: PrevPhysReg (86 HBs)
	if (injectArch == "FetchQueue"):
		injectLoc = random.randrange(0,927) #32: PC, 32: SeqNum, 56: ArchDestRegs, 189: ArchSrcRegs (3 FQs)
	if (injectArch == "DecodeQueue"):
		injectLoc = random.randrange(0,927) #32: PC, 32: SeqNum, 56: ArchDestRegs, 189: ArchSrcRegs (3 DQs)
	if (injectArch == "RenameQueue"):
		injectLoc = random.randrange(0,1032) #32: PC, 32: SeqNum, 64: PhysDestRegs, 216: PhysSrcRegs (3 RQs)
	if (injectArch == "I2EQ"):
		injectLoc = random.randrange(0,2752) #32: PC, 32: SeqNum, 64: PhysDestRegs, 216: PhysSrcRegs (8 I2EQs)
	if (injectArch == "IEWQ"):
		injectLoc = random.randrange(0,768) #32: SeqNum, 64: PhysDestRegs (8 IEWQs)
	if (injectArch == "IQ"):
		injectLoc = random.randrange(0,9984) #64: PhysDestRegs, 216: PhysSrcRegs, 32: SeqNum (32 IQs)
	if (injectArch == "ROB"):
		injectLoc = random.randrange(0,1280) #32: SeqNum (40 ROBs)
	if (injectArch == "LSQ"):
		injectLoc = random.randrange(0,2048) #32: Data, 32: Addr (16 LQs, 16 SQs)
	
	injectTime = random.randrange(0,runtime)
	f = open(str(bench) + "/val_" + str(injectArch)+"_"+str(start)+"_"+str(end)+".txt", 'a') 
		
	if (injectArch == "RF"):
		loop = True
		# while(loop):
			# if(bench == "perlbench"):
				# os.system("./checkS.sh " + str(arch) + " " + str(bench) + " " + str(injectTime) + " " + str(injectLoc) + " " + str(i) + " " + str(injectArch))
			# else:
				# os.system("./check.sh " + str(arch) + " " + str(bench) + " " + str(injectTime) + " " + str(injectLoc) + " " + str(i) + " " + str(injectArch))
			# data2 = file(bench+"/"+injectArch+"/gemV_"+str(i))
			# for line1 in data2:
				# if "Non" in line1 or "ND" in line1:
					# loop = True
					# injectLoc = random.randrange(0,8192) #32: Data (256 RFs)
					# injectTime = random.randrange(0,runtime)
					# break
				# else:
					# loop = False
					# break
		os.system("./check.sh " + str(arch) + " " + str(bench) + " " + str(injectTime) + " " + str(injectLoc) + " " + str(i) + " " + str(injectArch))
		data2 = file(bench+"/"+injectArch+"/gemV_"+str(i))
		for line1 in data2:
			if "Non-Vulnerable" in line1:
				#os.system("./inject.sh " + str(arch) + " " + str(bench) + " " + str(injectTime) + " " + str(injectLoc) + " " + str(i) + " " + str(injectArch) + " " + str(2*runtime) + " > " + str(bench) + "/FI_" + str(injectArch) + "_" + str(i))
				print ""
			else:
				if(bench == 'susan') or (bench == 'jpeg'):
					os.system("./inject_output.sh " + str(arch) + " " + str(bench) + " " + str(injectTime) + " " + str(injectLoc) + " " + str(i) + " " + str(injectArch) + " " + str(2*runtime) + " > " + str(bench) + "/FI_" + str(injectArch) + "_" + str(i))
				else:
					os.system("./inject.sh " + str(arch) + " " + str(bench) + " " + str(injectTime) + " " + str(injectLoc) + " " + str(i) + " " + str(injectArch) + " " + str(2*runtime) + " > " + str(bench) + "/FI_" + str(injectArch) + "_" + str(i))
		
		data2 = file(bench+"/"+injectArch+"/gemV_"+str(i))
		for line1 in data2:
			if "Non-Vulnerable" in line1:
				f.write("NV\t")
				f.write("NF\n")
			elif "Non-Decision" in line1:
				f.write("ND\t")
				data3 = file(bench+"/FI_" + str(injectArch)+ "_" + str(i))
				for line2 in data3:
					line3 = line2.strip().split('\t')
					if "NF" in line2:
						f.write("NF" + "\t" + line3[1] + "\t" + line3[2] + '\n')
					else:
						f.write("F" + "\t" + line3[1] + "\t" + line3[2] + '\n')
			elif "Vulnerable" in line1:
				f.write("V\t")
				data3 = file(bench+"/FI_" + str(injectArch)+ "_" + str(i))
				for line2 in data3:
					line3 = line2.strip().split('\t')
					if "NF" in line2:
						f.write("NF" + "\t" + line3[1] + "\t" + line3[2] + '\n')
					else:
						f.write("F" + "\t" + line3[1] + "\t" + line3[2] + '\n')
				
	elif (injectArch == "FetchQueue" or injectArch == "DecodeQueue" or injectArch == "RenameQueue" or injectArch == "I2EQ" or injectArch == "IEWQ" or injectArch == "IQ" or injectArch == "LSQ" or injectArch == "ROB"):
		os.system("./inject_" + str(bench) + ".sh " + str(bench) + " " + str(injectTime) + " " + str(injectLoc) + " " + str(i) + " " + str(injectArch) + " > " + str(bench) + "/FI_" + str(injectArch) + "_" + str(i))
		
		data2 = file(bench+"/"+injectArch+"/FI_"+str(i))
		for line1 in data2:
			if "Unused" in line1:
				f.write("NV\t")
			else:
				line2 = line1.strip().split(':')
				line3 = line2[3].split(' ')
				
				if(bench == "perlbench"):
					os.system("./checkS.sh " + str(bench) + " " + str(line2[0]) + " " + str(line3[3]) + " " + str(i) + " " + str(injectArch))
				else:
					os.system("./check.sh " + str(bench) + " " + str(line2[0]) + " " + str(line3[3]) + " " + str(i) + " " + str(injectArch))
					
				data2 = file(bench+"/"+injectArch+"/gemV_"+str(i))
				for line1 in data2:
					if "Non" in line1:
						f.write("NV\t")
					else:
						f.write("V\t")
				
		data2 = file(bench+"/FI_" + str(injectArch) + "_" + str(i))
		for line1 in data2:
			line2 = line1.strip().split('\t')
			if "NF" in line1:
				f.write("NF" + "\t" + line2[1] + "\t" + line2[2] + '\n')
			else:
				f.write("F" + "\t" + line2[1] + "\t" + line2[2] + '\n')
				
	elif (injectArch == "RenameMap"):
		os.system("./inject_" + str(bench) + ".sh " + str(bench) + " " + str(injectTime) + " " + str(injectLoc) + " " + str(i) + " " + str(injectArch) + " > " + str(bench) + "/FI_" + str(injectArch) + "_" + str(i))
		
		data2 = file(bench+"/"+injectArch+"/FI_"+str(i))
		for line1 in data2:

			line2 = line1.strip().split(':')
			line3 = line2[3].split(' ')
			
			if(bench == "perlbench"):
				os.system("./checkS.sh " + str(bench) + " " + str(line2[0]) + " " + str(line3[4]) + " " + str(i) + " " + str(injectArch))
			else:
				os.system("./check.sh " + str(bench) + " " + str(line2[0]) + " " + str(line3[4]) + " " + str(i) + " " + str(injectArch))
				
			data2 = file(bench+"/"+injectArch+"/gemV_"+str(i))
			for line1 in data2:
				if "Non" in line1:
					f.write("NV\t")
				else:
					f.write("V\t")
		
		data2 = file(bench+"/FI_" + str(injectArch) + "_" + str(i))
		for line1 in data2:
			line2 = line1.strip().split('\t')
			if "NF" in line1:
				f.write("NF" + "\t" + line2[1] + "\t" + line2[2] + '\n')
			else:
				f.write("F" + "\t" + line2[1] + "\t" + line2[2] + '\n')
				
	elif (injectArch == "HistoryBuffer"):
		os.system("./inject_" + str(bench) + ".sh " + str(bench) + " " + str(injectTime) + " " + str(injectLoc) + " " + str(i) + " " + str(injectArch) + " > " + str(bench) + "/FI_" + str(injectArch) + "_" + str(i))
		
		data2 = file(bench+"/"+injectArch+"/FI_"+str(i))
		for line1 in data2:
			if "Unused" in line1:
				f.write("NV\t")
			else:
				line2 = line1.strip().split(':')
				line3 = line2[3].split(' ')

				if "PrevPhysical" in line1 or "Sequence" in line1:
					if(bench == "perlbench"):
						os.system("./checkS.sh " + str(bench) + " " + str(line2[0]) + " " + str(line3[3]) + " " + str(i) + " PrevHistoryBuffer")
					else:
						os.system("./check.sh " + str(bench) + " " + str(line2[0]) + " " + str(line3[3]) + " " + str(i) + " PrevHistoryBuffer")
						
					data2 = file(bench+"/PrevHistoryBuffer/gemV_"+str(i))
					for line1 in data2:
						if "Non" in line1:
							f.write("NV\t")
						else:
							f.write("V\t")
				else:					
					if(bench == "perlbench"):
						os.system("./checkS.sh " + str(bench) + " " + str(line2[0]) + " " + str(line3[3]) + " " + str(i) + " NewHistoryBuffer")
					else:
						os.system("./check.sh " + str(bench) + " " + str(line2[0]) + " " + str(line3[3]) + " " + str(i) + " NewHistoryBuffer")
						
					data2 = file(bench+"/NewHistoryBuffer/gemV_"+str(i))
					for line1 in data2:
						if "Non" in line1:
							f.write("NV\t")
						else:
							f.write("V\t")
				
		data2 = file(bench+"/FI_" + str(injectArch) + "_" + str(i))
		for line1 in data2:
			line2 = line1.strip().split('\t')
			if "NF" in line1:
				f.write("NF" + "\t" + line2[1] + "\t" + line2[2] + '\n')
			else:
				f.write("F" + "\t" + line2[1] + "\t" + line2[2] + '\n')
	f.close()
#f.close()