import os
import sys
import random

arch = sys.argv[1]
bench = sys.argv[2]
injectArch = sys.argv[3]
start = sys.argv[4]
end = sys.argv[5]

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

os.system("mkdir " + str(bench))
#f = open(str(bench) + "/val_" + str(injectArch)+"_"+str(start)+"_"+str(end)+".txt", 'w') 

os.system("rm -rf " + str(bench) + "/val_" + str(injectArch)+"_"+str(start)+"_"+str(end)+".txt")

for i in range(int(start), int(end)):
	if (injectArch == "NO"):
		injectLoc = 0
	if (injectArch == "RF"):
		injectLoc = random.randrange(0,4096) #32: Data (128 integer RFs)
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
		os.system("./check.sh " + str(arch) + " " + str(bench) + " " + str(injectTime) + " " + str(injectLoc) + " " + str(i) + " " + str(injectArch))
		data2 = file(bench+"/"+injectArch+"/gemV_"+str(i))
		for line1 in data2:
			if "Non-Vulnerable" in line1:
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
				f.write("NF\t")
				f.write(str(injectTime) + "\t" + str(injectLoc) + "\n")

			elif "Vulnerable" in line1 or "Non-Decision" in line1:
				f.write("V\t")
				data3 = file(bench+"/FI_" + str(injectArch)+ "_" + str(i))
				
				for line2 in data3:
					line3 = line2.strip().split('\t')
					if "NF" in line2:
						f.write("NF\t")
						f.write(str(injectTime) + "\t" + str(injectLoc) + "\t")
						if(bench == 'susan') or (bench == 'jpeg'):
							os.system("./analysis_output.sh " +str(arch) + " " + str(bench) + " " + str(injectTime) + " " + str(injectLoc) + " " + str(runtime*2) + " " + injectArch + " " + str(i))
						else:
							os.system("./analysis.sh " +str(arch) + " " + str(bench) + " " + str(injectTime) + " " + str(injectLoc) + " " + str(runtime*2) + " " + injectArch)
						
						incorrectMemAddr = False
						incorrectBranch = False
						memTransfer = False
						numMemTrasfer = 0
						overwritten = False
						numOverwritten = 0
						compare = False
						numCompare = 0
						logical = False
						numLogical = 0
						faulty = False
						
						fi = file(str(bench) + "_trace/FI_" + str(injectTime) + "_" + str(injectLoc))
						for fi_line in fi:
							if "Incorrect Mem Addr" in fi_line:
								incorrectMemAddr = True
								break
								
							elif "Incorrect branch" in fi_line:
								incorrectBranch = True
								break
								
							elif "is faulty" in fi_line:
								faulty = True
								break
								
							elif "Masked by read-write (register and memory)" in fi_line:
								memTransfer = True
								
							elif "masked by overwritten" in fi_line:
								overwritten = True
								
							elif "masked by cmps" in fi_line:
								compare = True
								
							elif "masked by and" in fi_line or "masked by orr" in fi_line:
								logical = True
								
							elif "Bit Flip in" in fi_line:
								flip_line = fi_line.strip().split()
								f.write("r" + flip_line[4] + "\t"  + flip_line[len(flip_line)-2] + "\t")

						if(int(flip_line[4]) == 37 and int(injectLoc) % 32 > 1):
							f.write("\t\t\t\t\t\t\t" + "incorrect flag flip\n")
						elif(int(flip_line[4]) == 38 and int(injectLoc) % 32 > 0):
							f.write("\t\t\t\t\t\t\t" + "incorrect flag flip\n")
						elif(int(flip_line[4]) == 39 and int(injectLoc) % 32 > 0):
							f.write("\t\t\t\t\t\t\t" + "incorrect flag flip\n")
						elif(faulty):
							f.write("\t\t\t\t\t" + "faulty data\n")
						elif(incorrectBranch):
							f.write("\t\t\t\t" + "incorrect branch\n")
						elif(incorrectMemAddr):
							f.write("\t\t\t\t\t\t" + "incorrect memory address\n")

						else:
							if(memTransfer):
								f.write("memory trasfer" + "\t")
							else:
								f.write("\t")
							if(overwritten):
								f.write("overwritten" + "\t")
							else:
								f.write("\t")
							if(compare):
								f.write("compare" + "\t")
							else:
								f.write("\t")
							if(logical):
								f.write("logical" + "\t\n")
							else:
								f.write("\t\n")
						
					else:
						f.write("F\t")
						f.write(str(injectTime) + "\t" + str(injectLoc) + "\t\n")
						
	else:
		loop = True
		os.system("./check.sh " + str(arch) + " " + str(bench) + " " + str(injectTime) + " " + str(injectLoc) + " " + str(i) + " " + str(injectArch))
		data2 = file(bench+"/"+injectArch+"/gemV_"+str(i))
		for line1 in data2:
			if "Non-Vulnerable" in line1:
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
				f.write("NF\t")
				f.write(str(injectTime) + "\t" + str(injectLoc) + "\n")

			elif "Vulnerable" in line1 or "Non-Decision" in line1:
				f.write("V\t")
				data3 = file(bench+"/FI_" + str(injectArch)+ "_" + str(i))
				
				for line2 in data3:
					line3 = line2.strip().split('\t')
					if "NF" in line2:
						f.write("NF\t")
						f.write(str(injectTime) + "\t" + str(injectLoc) + "\t\n")
						os.system("./compare.sh " +str(arch) + " " + str(bench) + " " + str(injectTime) + " " + str(injectLoc) + " " + str(runtime*2) + " " + str(injectArch))
					else:
						f.write("F\t")
						f.write(str(injectTime) + "\t" + str(injectLoc) + "\t\n")
	f.close()