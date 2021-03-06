# Copyright (c) 2005-2007 The Regents of The University of Michigan
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Authors: Kevin Lim

from m5.defines import buildEnv
from m5.params import *
from m5.proxy import *
from BaseCPU import BaseCPU
from FUPool import *
from O3Checker import O3Checker
from BranchPredictor import BranchPredictor

class DerivO3CPU(BaseCPU):
    type = 'DerivO3CPU'
    cxx_header = 'cpu/o3/deriv.hh'

    @classmethod
    def memory_mode(cls):
        return 'timing'

    @classmethod
    def require_caches(cls):
        return True

    @classmethod
    def support_take_over(cls):
        return True

    activity = Param.Unsigned(0, "Initial count")

    cachePorts = Param.Unsigned(200, "Cache Ports")

    decodeToFetchDelay = Param.Cycles(1, "Decode to fetch delay")
    renameToFetchDelay = Param.Cycles(1 ,"Rename to fetch delay")
    iewToFetchDelay = Param.Cycles(1, "Issue/Execute/Writeback to fetch "
                                   "delay")
    commitToFetchDelay = Param.Cycles(1, "Commit to fetch delay")
    fetchWidth = Param.Unsigned(8, "Fetch width")
    fetchBufferSize = Param.Unsigned(64, "Fetch buffer size in bytes")

    renameToDecodeDelay = Param.Cycles(1, "Rename to decode delay")
    iewToDecodeDelay = Param.Cycles(1, "Issue/Execute/Writeback to decode "
                                    "delay")
    commitToDecodeDelay = Param.Cycles(1, "Commit to decode delay")
    fetchToDecodeDelay = Param.Cycles(1, "Fetch to decode delay")
    decodeWidth = Param.Unsigned(8, "Decode width")

    iewToRenameDelay = Param.Cycles(1, "Issue/Execute/Writeback to rename "
                                    "delay")
    commitToRenameDelay = Param.Cycles(1, "Commit to rename delay")
    decodeToRenameDelay = Param.Cycles(1, "Decode to rename delay")
    renameWidth = Param.Unsigned(8, "Rename width")

    commitToIEWDelay = Param.Cycles(1, "Commit to "
               "Issue/Execute/Writeback delay")
    renameToIEWDelay = Param.Cycles(2, "Rename to "
               "Issue/Execute/Writeback delay")
    issueToExecuteDelay = Param.Cycles(1, "Issue to execute delay (internal "
              "to the IEW stage)")
    dispatchWidth = Param.Unsigned(8, "Dispatch width")
    issueWidth = Param.Unsigned(8, "Issue width")
    wbWidth = Param.Unsigned(8, "Writeback width")
    wbDepth = Param.Unsigned(1, "Writeback depth")
    fuPool = Param.FUPool(DefaultFUPool(), "Functional Unit pool")

    iewToCommitDelay = Param.Cycles(1, "Issue/Execute/Writeback to commit "
               "delay")
    renameToROBDelay = Param.Cycles(1, "Rename to reorder buffer delay")
    commitWidth = Param.Unsigned(8, "Commit width")
    squashWidth = Param.Unsigned(8, "Squash width")
    trapLatency = Param.Cycles(13, "Trap latency")
    fetchTrapLatency = Param.Cycles(1, "Fetch trap latency")

    backComSize = Param.Unsigned(5, "Time buffer size for backwards communication")
    forwardComSize = Param.Unsigned(5, "Time buffer size for forward communication")

    LQEntries = Param.Unsigned(32, "Number of load queue entries")
    SQEntries = Param.Unsigned(32, "Number of store queue entries")
    LSQDepCheckShift = Param.Unsigned(4, "Number of places to shift addr before check")
    LSQCheckLoads = Param.Bool(True,
        "Should dependency violations be checked for loads & stores or just stores")
    store_set_clear_period = Param.Unsigned(250000,
            "Number of load/store insts before the dep predictor should be invalidated")
    LFSTSize = Param.Unsigned(1024, "Last fetched store table size")
    SSITSize = Param.Unsigned(1024, "Store set ID table size")

    numRobs = Param.Unsigned(1, "Number of Reorder Buffers");

    numPhysIntRegs = Param.Unsigned(256, "Number of physical integer registers")
    numPhysFloatRegs = Param.Unsigned(256, "Number of physical floating point "
                                      "registers")
    # most ISAs don't use condition-code regs, so default is 0
    _defaultNumPhysCCRegs = 0
    if buildEnv['TARGET_ISA'] == 'x86':
        # For x86, each CC reg is used to hold only a subset of the
        # flags, so we need 4-5 times the number of CC regs as
        # physical integer regs to be sure we don't run out.  In
        # typical real machines, CC regs are not explicitly renamed
        # (it's a side effect of int reg renaming), so they should
        # never be the bottleneck here.
        _defaultNumPhysCCRegs = Self.numPhysIntRegs * 5
    numPhysCCRegs = Param.Unsigned(_defaultNumPhysCCRegs,
                                   "Number of physical cc registers")
    numIQEntries = Param.Unsigned(64, "Number of instruction queue entries")
    numROBEntries = Param.Unsigned(192, "Number of reorder buffer entries")

    smtNumFetchingThreads = Param.Unsigned(1, "SMT Number of Fetching Threads")
    smtFetchPolicy = Param.String('SingleThread', "SMT Fetch policy")
    smtLSQPolicy    = Param.String('Partitioned', "SMT LSQ Sharing Policy")
    smtLSQThreshold = Param.Int(100, "SMT LSQ Threshold Sharing Parameter")
    smtIQPolicy    = Param.String('Partitioned', "SMT IQ Sharing Policy")
    smtIQThreshold = Param.Int(100, "SMT IQ Threshold Sharing Parameter")
    smtROBPolicy   = Param.String('Partitioned', "SMT ROB Sharing Policy")
    smtROBThreshold = Param.Int(100, "SMT ROB Threshold Sharing Parameter")
    smtCommitPolicy = Param.String('RoundRobin', "SMT Commit Policy")

    branchPred = Param.BranchPredictor(BranchPredictor(numThreads =
                                                       Parent.numThreads),
                                       "Branch Predictor")
    needsTSO = Param.Bool(buildEnv['TARGET_ISA'] == 'x86',
                          "Enable TSO Memory model")
    #VUL
    vul_analysis = Param.Unsigned(1, "Enable/disable vulnerability analysis")
    fi_reg = Param.Unsigned(1, "Register number for fault injection")
    rob_vul_enable = Param.Unsigned(0, "Enable ROB vulnerability analysis")
    rf_vul_enable = Param.Unsigned(0, "Enable ROB vulnerability analysis")
    cache_vul_enable = Param.Unsigned(0, "Enable ROB vulnerability analysis")
    iq_vul_enable = Param.Unsigned(0, "Enable ROB vulnerability analysis")
    lsq_vul_enable = Param.Unsigned(0, "Enable ROB vulnerability analysis")
    pipeline_vul_enable = Param.Unsigned(0, "Enable ROB vulnerability analysis")
    rename_vul_enable = Param.Unsigned(0, "Enable ROB vulnerability analysis")
	
	#YOHAN: Add parameter for fault injection
    injectFaultROB = Param.Unsigned(0, "Inject a single-bit fault in ROB or not (0: NO, 1: YES)")
    injectFaultRF = Param.Unsigned(0, "Inject a single-bit fault in Register File or not (0: NO, 1: YES)")
    injectFaultFQ = Param.Unsigned(0, "Inject a single-bit fault in Fetch Queue or not (0: NO, 1: YES)")
    injectFaultDQ = Param.Unsigned(0, "Inject a single-bit fault in Decode Queue or not (0: NO, 1: YES)")
    injectFaultRQ = Param.Unsigned(0, "Inject a single-bit fault in Rename Queue or not (0: NO, 1: YES)")
    injectFaultRM = Param.Unsigned(0, "Inject a single-bit fault in Rename Map or not (0: NO, 1: YES)")
    injectFaultHB = Param.Unsigned(0, "Inject a single-bit fault in Rename History Buffer or not (0: NO, 1: YES)")
    injectFaultLSQ = Param.Unsigned(0, "Inject a single-bit fault in Load Store Queue or not (0: NO, 1: YES)")
    injectFaultIQ = Param.Unsigned(0, "Inject a single-bit fault in Instruction Queue or not (0: NO, 1: YES)")
    injectFaultI2EQ = Param.Unsigned(0, "Inject a single-bit fault in Instruction Queue or not (0: NO, 1: YES)")
    injectFaultIEWQ = Param.Unsigned(0, "Inject a single-bit fault in IEWQ or not (0: NO, 1: YES)")
    injectTime = Param.UInt64(0, "Time to inject fault")
    injectLoc = Param.Unsigned(0, "Bit location to inject fault")
    maxTraceInst = Param.Unsigned(0, "Max trace instruction after fault injection")
    traceFault = Param.Unsigned(0, "Trace corrupted registers and memory (0: NO, 1: YES)")
	
    checkFaultPipe = Param.Unsigned(0, "Check a single-bit fault in Piepeline or not (0: NO, 1: YES)")
    checkFaultROB = Param.Unsigned(0, "Check a single-bit fault in ROB or not (0: NO, 1: YES)")
    checkFaultRF = Param.Unsigned(0, "Check a single-bit fault in Register File or not (0: NO, 1: YES)")
    checkFaultRename = Param.Unsigned(0, "Check a single-bit fault in Rename Map or not (0: NO, 1: YES)")
    checkFaultI2EQ = Param.Unsigned(0, "Check a single-bit fault in Instruction Queue or not (0: NO, 1: YES)")
    checkFaultIEWQ = Param.Unsigned(0, "Check a single-bit fault in IEWQ or not (0: NO, 1: YES)")

    def addCheckerCpu(self):
        if buildEnv['TARGET_ISA'] in ['arm']:
            from ArmTLB import ArmTLB

            self.checker = O3Checker(workload=self.workload,
                                     exitOnError=False,
                                     updateOnError=True,
                                     warnOnlyOnLoadError=True)
            self.checker.itb = ArmTLB(size = self.itb.size)
            self.checker.dtb = ArmTLB(size = self.dtb.size)
            self.checker.cpu_id = self.cpu_id

        else:
            print "ERROR: Checker only supported under ARM ISA!"
            exit(1)
