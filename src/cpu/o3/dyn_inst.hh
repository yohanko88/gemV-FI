/*
 * Copyright (c) 2010 ARM Limited
 * Copyright (c) 2013 Advanced Micro Devices, Inc.
 * All rights reserved
 *
 * The license below extends only to copyright in the software and shall
 * not be construed as granting a license to any other intellectual
 * property including but not limited to intellectual property relating
 * to a hardware implementation of the functionality of the software
 * licensed hereunder.  You may use the software subject to the license
 * terms below provided that you ensure that this notice is replicated
 * unmodified and in its entirety in all distributions of the software,
 * modified or unmodified, in source code or in binary form.
 *
 * Copyright (c) 2004-2006 The Regents of The University of Michigan
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met: redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer;
 * redistributions in binary form must reproduce the above copyright
 * notice, this list of conditions and the following disclaimer in the
 * documentation and/or other materials provided with the distribution;
 * neither the name of the copyright holders nor the names of its
 * contributors may be used to endorse or promote products derived from
 * this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 * OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * Authors: Kevin Lim
 */

#ifndef __CPU_O3_DYN_INST_HH__
#define __CPU_O3_DYN_INST_HH__

#include "arch/isa_traits.hh"
#include "config/the_isa.hh"
#include "cpu/o3/cpu.hh"
#include "cpu/o3/isa_specific.hh"
#include "cpu/base_dyn_inst.hh"
#include "cpu/inst_seq.hh"
#include "cpu/reg_class.hh"
#include "debug/FI.hh" //YOHAN: Debug flag for fault injection

class Packet;

/**
 * Mostly implementation & ISA specific AlphaDynInst. As with most
 * other classes in the new CPU model, it is templated on the Impl to
 * allow for passing in of all types, such as the CPU type and the ISA
 * type. The AlphaDynInst serves as the primary interface to the CPU
 * for instructions that are executing.
 */
template <class Impl>
class BaseO3DynInst : public BaseDynInst<Impl>
{
  public:
    /** Typedef for the CPU. */
    typedef typename Impl::O3CPU O3CPU;

    /** Binary machine instruction type. */
    typedef TheISA::MachInst MachInst;
    /** Extended machine instruction type. */
    typedef TheISA::ExtMachInst ExtMachInst;
    /** Logical register index type. */
    typedef TheISA::RegIndex RegIndex;
    /** Integer register index type. */
    typedef TheISA::IntReg   IntReg;
    typedef TheISA::FloatReg FloatReg;
    typedef TheISA::FloatRegBits FloatRegBits;
    
    //YOHAN: Flip a single bit in dynamic instruction
    int bitPC; //size of PC: 32 bits
    int bitSeqNum; // size of sequence number: 32 bits
    int bitDestRegs; //size of architectural detination register: 7 bits X 8
    int bitSrcRegs; // size of architectural destination register: 7 bits X 27
    int bitPSrcRegs; // size of physical source register: 8 bits X 8
    int bitPDestRegs; // size of physical destination register: 8 bits X 27
    
    //YOHAN: Flip FetchQueue
    bool flipFQ (unsigned injectLoc) {
        if(injectLoc < bitPC) {
            Addr newPC = this->instAddr() ^ (1UL << injectLoc);
            DPRINTF(FI, "Bit Flip: FetchQueue PC %d: %#x to %#x\n", this->seqNum, this->instAddr(), newPC);
            this->pcState(newPC);
            return true;
        }
        else if(injectLoc >= bitPC && injectLoc < (bitPC + bitSeqNum)) {
            injectLoc -= bitPC;
            int newSeqNum = this->seqNum ^ (1UL << (injectLoc));
            DPRINTF(FI, "Bit Flip: FetchQueue SeqNum %d: %d to %d\n", this->seqNum, this->seqNum, newSeqNum);
            this->seqNum = newSeqNum;
            return true;
        }
        else if(injectLoc >= (bitPC + bitSeqNum) && injectLoc < (bitPC + bitSeqNum + bitDestRegs)) {
            injectLoc -= (bitPC + bitSeqNum);
            if((injectLoc/7) >= this->numDestRegs()) {
                DPRINTF(FI, "Bit Flip into Unused FetchQueue (DEST)\n");
                return true;
            }
            int injectTarget = (injectLoc/7);
            this->cpu->changeDest = true;
            this->cpu->oldDestReg = this->destRegIdx(injectTarget);
            this->cpu->oldDestIdx = injectTarget;
            this->cpu->oldPC = this->instAddr();
            this->cpu->oldInst = this->staticInst->disassemble(this->instAddr());
            if((int)this->destRegIdx(injectTarget) < TheISA::FP_Reg_Base) {
                int newDestRegs = this->destRegIdx(injectTarget) ^ (1UL << (injectLoc%5));
                DPRINTF(FI, "Bit Flip: FetchQueue DestArchReg %d: %d to %d\n", this->seqNum, this->destRegIdx(injectTarget), newDestRegs);
                this->setDestRegIdx(injectTarget, newDestRegs);
                return true;
            }
            else if ((int)this->destRegIdx(injectTarget) >= TheISA::FP_Reg_Base && (int)this->destRegIdx(injectTarget) < TheISA::CC_Reg_Base) {
                int newDestRegs = ((this->destRegIdx(injectTarget) - TheISA::FP_Reg_Base) ^ (1UL << (injectLoc%5))) + TheISA::FP_Reg_Base;
                DPRINTF(FI, "Bit Flip: FetchQueue DestArchReg %d: %d to %d\n", this->seqNum, this->destRegIdx(injectTarget), newDestRegs);
                this->setDestRegIdx(injectTarget, newDestRegs);
                return true;
            }
        }
        
        else if(injectLoc >= (bitPC + bitSeqNum + bitDestRegs)) {
            injectLoc -= (bitPC + bitSeqNum + bitDestRegs);
            if((injectLoc/7) >= this->numSrcRegs()) {
                DPRINTF(FI, "Bit Flip into Unused FetchQueue (SRC)\n");
                return true;
            }
            int injectTarget = (injectLoc/7);
            this->cpu->changeSrc = true;
            this->cpu->oldSrcReg = this->srcRegIdx(injectTarget);
            this->cpu->oldSrcIdx = injectTarget;
            this->cpu->oldPC = this->instAddr();
            this->cpu->oldInst = this->staticInst->disassemble(this->instAddr());
            if((int)this->srcRegIdx(injectTarget) < TheISA::FP_Reg_Base) {
                int newSrcRegs = this->srcRegIdx(injectTarget) ^ (1UL << (injectLoc%5));
                DPRINTF(FI, "Bit Flip: FetchQueue SrcArchReg %d: %d to %d\n", this->seqNum, this->srcRegIdx(injectTarget), newSrcRegs);
                this->setSrcRegIdx(injectTarget, newSrcRegs);
                return true;
            }
            else if ((int)this->srcRegIdx(injectTarget) >= TheISA::FP_Reg_Base && (int)this->srcRegIdx(injectTarget) < TheISA::CC_Reg_Base) {
                int newSrcRegs = ((this->srcRegIdx(injectTarget) - TheISA::FP_Reg_Base) ^ (1UL << (injectLoc%5))) + TheISA::FP_Reg_Base;
                DPRINTF(FI, "Bit Flip: FetchQueue SrcArchReg %d: %d to %d\n", this->seqNum, this->srcRegIdx(injectTarget), newSrcRegs);
                this->setSrcRegIdx(injectTarget, newSrcRegs);
                return true;
            }
        }
        return false;
    }
    
    //YOHAN: Flip DecodeQueue
    bool flipDQ (unsigned injectLoc) {
        if(injectLoc < bitPC) {
            Addr newPC = this->instAddr() ^ (1UL << injectLoc);
            DPRINTF(FI, "Bit Flip: DecodeQueue PC %d: %#x to %#x\n", this->seqNum, this->instAddr(), newPC);
            this->pcState(newPC);
            return true;
        }
        else if(injectLoc >= bitPC && injectLoc < (bitPC + bitSeqNum)) {
            injectLoc -= bitPC;
            int newSeqNum = this->seqNum ^ (1UL << (injectLoc));
            DPRINTF(FI, "Bit Flip: DecodeQueue SeqNum %d: %d to %d\n", this->seqNum, this->seqNum, newSeqNum);
            this->seqNum = newSeqNum;
            return true;
        }
        else if(injectLoc >= (bitPC + bitSeqNum) && injectLoc < (bitPC + bitSeqNum + bitDestRegs)) {
            injectLoc -= (bitPC + bitSeqNum);
            if((injectLoc/7) >= this->numDestRegs()) {
                DPRINTF(FI, "Bit Flip into Unused DecodeQueue (DEST)\n");
                return true;
            }
            int injectTarget = (injectLoc/7);
            this->cpu->changeDest = true;
            this->cpu->oldDestReg = this->destRegIdx(injectTarget);
            this->cpu->oldDestIdx = injectTarget;
            this->cpu->oldPC = this->instAddr();
            this->cpu->oldInst = this->staticInst->disassemble(this->instAddr());
            if((int)this->destRegIdx(injectTarget) < TheISA::FP_Reg_Base) {
                int newDestRegs = this->destRegIdx(injectTarget) ^ (1UL << (injectLoc%5));
                DPRINTF(FI, "Bit Flip: DecodeQueue DestArchReg %d: %d to %d\n", this->seqNum, this->destRegIdx(injectTarget), newDestRegs);
                this->setDestRegIdx(injectTarget, newDestRegs);
                return true;
            }
            else if ((int)this->destRegIdx(injectTarget) >= TheISA::FP_Reg_Base && (int)this->destRegIdx(injectTarget) < TheISA::CC_Reg_Base) {
                int newDestRegs = ((this->destRegIdx(injectTarget) - TheISA::FP_Reg_Base) ^ (1UL << (injectLoc%5))) + TheISA::FP_Reg_Base;
                DPRINTF(FI, "Bit Flip: DecodeQueue DestArchReg %d: %d to %d\n", this->seqNum, this->destRegIdx(injectTarget), newDestRegs);
                this->setDestRegIdx(injectTarget, newDestRegs);
                return true;
            }
        }
        
        else if(injectLoc >= (bitPC + bitSeqNum + bitDestRegs)) {
            injectLoc -= (bitPC + bitSeqNum + bitDestRegs);
            if((injectLoc/7) >= this->numSrcRegs()) {
                DPRINTF(FI, "Bit Flip into Unused DecodeQueue (SRC)\n");
                return true;
            }
            int injectTarget = (injectLoc/7);
            this->cpu->changeSrc = true;
            this->cpu->oldSrcReg = this->srcRegIdx(injectTarget);
            this->cpu->oldSrcIdx = injectTarget;
            this->cpu->oldPC = this->instAddr();
            this->cpu->oldInst = this->staticInst->disassemble(this->instAddr());
            if((int)this->srcRegIdx(injectTarget) < TheISA::FP_Reg_Base) {
                int newSrcRegs = this->srcRegIdx(injectTarget) ^ (1UL << (injectLoc%5));
                DPRINTF(FI, "Bit Flip: DecodeQueue SrcArchReg %d: %d to %d\n", this->seqNum, this->srcRegIdx(injectTarget), newSrcRegs);
                this->setSrcRegIdx(injectTarget, newSrcRegs);
                return true;
            }
            else if ((int)this->srcRegIdx(injectTarget) >= TheISA::FP_Reg_Base && (int)this->srcRegIdx(injectTarget) < TheISA::CC_Reg_Base) {
                int newSrcRegs = ((this->srcRegIdx(injectTarget) - TheISA::FP_Reg_Base) ^ (1UL << (injectLoc%5))) + TheISA::FP_Reg_Base;
                DPRINTF(FI, "Bit Flip: DecodeQueue SrcArchReg %d: %d to %d\n", this->seqNum, this->srcRegIdx(injectTarget), newSrcRegs);
                this->setSrcRegIdx(injectTarget, newSrcRegs);
                return true;
            }
        }
        return false;
    }
 
    //YOHAN: Flip RenameQueue
    bool flipRQ (unsigned injectLoc) {
        if(injectLoc < bitPC) {
            Addr newPC = this->instAddr() ^ (1UL << injectLoc);
            DPRINTF(FI, "Bit Flip: RenameQueue PC %d: %#x to %#x\n", this->seqNum, this->instAddr(), newPC);
            this->pcState(newPC);
            return true;
        }
        else if(injectLoc >= bitPC && injectLoc < (bitPC + bitSeqNum)) {
            injectLoc -= bitPC;
            int newSeqNum = this->seqNum ^ (1UL << (injectLoc));
            DPRINTF(FI, "Bit Flip: RenameQueue SeqNum %d: %d to %d\n", this->seqNum, this->seqNum, newSeqNum);
            this->seqNum = newSeqNum;
            return true;
        }
        else if(injectLoc >= (bitPC + bitSeqNum) && injectLoc < (bitPC + bitSeqNum + bitPDestRegs)) {
            injectLoc -= (bitPC + bitSeqNum);
            if((injectLoc/8) >= this->numDestRegs()) {
                DPRINTF(FI, "Bit Flip into Unused RenameQueue (DEST)\n");
                return true;
            }
            int injectTarget = (injectLoc/8);
            int newDestReg = (this->_destRegIdx[injectTarget]) ^ (1UL << injectLoc%8);
            DPRINTF(FI, "Bit Flip: RenameQueue DestPhyReg %d: %d to %d\n", this->seqNum, this->_destRegIdx[injectTarget], newDestReg);
            this->_destRegIdx[injectTarget] = newDestReg;
            return true;
        }
        
        else if(injectLoc >= (bitPC + bitSeqNum + bitPDestRegs)) {
            injectLoc -= (bitPC + bitSeqNum + bitPDestRegs);
            if((injectLoc/8) >= this->numSrcRegs()) {
                DPRINTF(FI, "Bit Flip into Unused RenameQueue (SRC)\n");
                return true;
            }
            int injectTarget = (injectLoc/8);
            int newSrcReg = (this->_srcRegIdx[injectTarget]) ^ (1UL << injectLoc%8);
            DPRINTF(FI, "Bit Flip: RenameQueue SrcPhyReg %d: %d to %d\n", this->seqNum, this->_srcRegIdx[injectTarget], newSrcReg);
            this->_srcRegIdx[injectTarget] = newSrcReg;
            return true;
        }
        return false;
    }
    
    //YOHAN: Flip I2EQueue
    bool flipI2EQ (unsigned injectLoc) {
        if(injectLoc < bitPC) {
            Addr newPC = this->instAddr() ^ (1UL << injectLoc);
            DPRINTF(FI, "Bit Flip: I2EQueue PC %d: %#x to %#x\n", this->seqNum, this->instAddr(), newPC);
            this->pcState(newPC);
            return true;
        }
        else if(injectLoc >= bitPC && injectLoc < (bitPC + bitSeqNum)) {
            injectLoc -= bitPC;
            int newSeqNum = this->seqNum ^ (1UL << (injectLoc));
            DPRINTF(FI, "Bit Flip: I2EQueue SeqNum %d: %d to %d\n", this->seqNum, this->seqNum, newSeqNum);
            this->seqNum = newSeqNum;
            return true;
        }
        else if(injectLoc >= (bitPC + bitSeqNum) && injectLoc < (bitPC + bitSeqNum + bitPDestRegs)) {
            injectLoc -= (bitPC + bitSeqNum);
            if((injectLoc/8) >= this->numDestRegs()) {
                DPRINTF(FI, "Bit Flip into Unused I2EQueue (DEST)\n");
                return true;
            }
            int injectTarget = (injectLoc/8);
            int newDestReg = (this->_destRegIdx[injectTarget]) ^ (1UL << injectLoc%8);
            DPRINTF(FI, "Bit Flip: I2EQueue DestPhyReg %d: %d to %d\n", this->seqNum, this->_destRegIdx[injectTarget], newDestReg);
            this->_destRegIdx[injectTarget] = newDestReg;
            return true;
        }
        
        else if(injectLoc >= (bitPC + bitSeqNum + bitPDestRegs)) {
            injectLoc -= (bitPC + bitSeqNum + bitPDestRegs);
            if((injectLoc/8) >= this->numSrcRegs()) {
                DPRINTF(FI, "Bit Flip into Unused I2EQueue (SRC)\n");
                return true;
            }
            int injectTarget = (injectLoc/8);
            int newSrcReg = (this->_srcRegIdx[injectTarget]) ^ (1UL << injectLoc%8);
            DPRINTF(FI, "Bit Flip: I2EQueue SrcPhyReg %d: %d to %d\n", this->seqNum, this->_srcRegIdx[injectTarget], newSrcReg);
            this->_srcRegIdx[injectTarget] = newSrcReg;
            return true;
        }
        return false;
    }
    
    //YOHAN: Flip IEWQueue
    bool flipIEWQ (unsigned injectLoc) {
        if(injectLoc < bitPC) {
            Addr newPC = this->instAddr() ^ (1UL << injectLoc);
            DPRINTF(FI, "Bit Flip: IEWQueue PC %d: %#x to %#x\n", this->seqNum, this->instAddr(), newPC);
            this->pcState(newPC);
            return true;
        }
        
        else if(injectLoc >= bitPC) {
            injectLoc -= bitPC;
            if((injectLoc/8) >= this->numDestRegs()) {
                DPRINTF(FI, "Bit Flip into Unused IEWQueue (DEST)\n");
                return true;
            }
            int injectTarget = (injectLoc/8);
            int newDestReg = (this->_destRegIdx[injectTarget]) ^ (1UL << injectLoc%8);
            DPRINTF(FI, "Bit Flip: IEWQueue DestPhyReg %d: %d to %d\n", this->seqNum, this->_destRegIdx[injectTarget], newDestReg);
            this->_destRegIdx[injectTarget] = newDestReg;
            return true;
        }
        return false;
    }
    
    //YOHAN: Flip IQ
    bool flipIQ (unsigned injectLoc) {
        if(injectLoc < bitPDestRegs) {
            if((injectLoc/8) >= this->numDestRegs()) {
                DPRINTF(FI, "Bit Flip into Unused IQ\n");
                return true;
            }
            int injectTarget = (injectLoc/8);
            int newDestReg = this->_destRegIdxIQ[injectTarget] ^ (1UL << injectLoc%8);
            DPRINTF(FI, "Bit Flip: IQ DestReg %d: %d to %d\n", this->seqNum, this->_destRegIdxIQ[injectTarget], newDestReg);
            this->_destRegIdxIQ[injectLoc/8] = newDestReg;
            return true;
        }
        else if(injectLoc >= bitPDestRegs && injectLoc < (bitPDestRegs + bitSrcRegs)) {
            injectLoc -= bitPDestRegs;
            if(((injectLoc)/8) >= this->numSrcRegs()) {
                DPRINTF(FI, "Bit Flip into Unused IQ\n");
                return true;
            }
            int injectTarget = ((injectLoc)/8);
            int newSrcReg = this->_srcRegIdxIQ[injectTarget] ^ (1UL << (injectLoc)%8);
            DPRINTF(FI, "Bit Flip: IQ SrcReg %d: %d to %d\n", this->seqNum, this->_srcRegIdxIQ[injectTarget], newSrcReg);
            this->_srcRegIdxIQ[(injectLoc)/8] = newSrcReg;
            return true;
        }
        else if(injectLoc >= (bitPDestRegs + bitSrcRegs)) {
            injectLoc -= (bitPDestRegs + bitSrcRegs);
            int newSeqNum = this->seqNumIQ ^ (1UL << (injectLoc));
            DPRINTF(FI, "Bit Flip: IQ SeqNum %d: %d to %d\n", this->seqNum, this->seqNumIQ, newSeqNum);
            this->seqNumIQ = newSeqNum;
            return true;
        }
        return false;
    }

    //YOHAN: Flip ROB
    bool flipROB (unsigned injectLoc) {
        int newSeqNum = this->seqNumROB ^ (1UL << (injectLoc));
        DPRINTF(FI, "Bit Flip: ROB SeqNum %d: %d to %d\n", this->seqNum, this->seqNumROB, newSeqNum);
        this->seqNumROB = newSeqNum;
        return true;
    }
    
#ifdef ISA_HAS_CC_REGS
    typedef TheISA::CCReg   CCReg;
#endif
    /** Misc register index type. */
    typedef TheISA::MiscReg  MiscReg;

    enum {
        MaxInstSrcRegs = TheISA::MaxInstSrcRegs,        //< Max source regs
        MaxInstDestRegs = TheISA::MaxInstDestRegs       //< Max dest regs
    };


  public:
    /** BaseDynInst constructor given a binary instruction. */
    BaseO3DynInst(StaticInstPtr staticInst, StaticInstPtr macroop,
                  TheISA::PCState pc, TheISA::PCState predPC,
                  InstSeqNum seq_num, O3CPU *cpu);

    /** BaseDynInst constructor given a static inst pointer. */
    BaseO3DynInst(StaticInstPtr _staticInst, StaticInstPtr _macroop);

    ~BaseO3DynInst();

    /** Executes the instruction.*/
    Fault execute();

    /** Initiates the access.  Only valid for memory operations. */
    Fault initiateAcc();

    /** Completes the access.  Only valid for memory operations. */
    Fault completeAcc(PacketPtr pkt);

  private:
    /** Initializes variables. */
    void initVars();

  protected:
    /** Values to be written to the destination misc. registers. */
    MiscReg _destMiscRegVal[TheISA::MaxMiscDestRegs];

    /** Indexes of the destination misc. registers. They are needed to defer
     * the write accesses to the misc. registers until the commit stage, when
     * the instruction is out of its speculative state.
     */
    short _destMiscRegIdx[TheISA::MaxMiscDestRegs];

    /** Number of destination misc. registers. */
    uint8_t _numDestMiscRegs;


  public:
#if TRACING_ON
    /** Tick records used for the pipeline activity viewer. */
    Tick fetchTick;         // instruction fetch is completed.
    int32_t decodeTick;  // instruction enters decode phase
    int32_t renameTick;  // instruction enters rename phase
    int32_t dispatchTick;
    int32_t issueTick;
    int32_t completeTick;
    int32_t commitTick;
    int32_t storeTick;
#endif

    /** Reads a misc. register, including any side-effects the read
     * might have as defined by the architecture.
     */
    MiscReg readMiscReg(int misc_reg)
    {
        return this->cpu->readMiscReg(misc_reg, this->threadNumber);
    }

    /** Sets a misc. register, including any side-effects the write
     * might have as defined by the architecture.
     */
    void setMiscReg(int misc_reg, const MiscReg &val)
    {
        /** Writes to misc. registers are recorded and deferred until the
         * commit stage, when updateMiscRegs() is called. First, check if
         * the misc reg has been written before and update its value to be
         * committed instead of making a new entry. If not, make a new
         * entry and record the write.
         */
        for (int idx = 0; idx < _numDestMiscRegs; idx++) {
            if (_destMiscRegIdx[idx] == misc_reg) {
               _destMiscRegVal[idx] = val;
               return;
            }
        }

        assert(_numDestMiscRegs < TheISA::MaxMiscDestRegs);
        _destMiscRegIdx[_numDestMiscRegs] = misc_reg;
        _destMiscRegVal[_numDestMiscRegs] = val;
        _numDestMiscRegs++;
    }

    /** Reads a misc. register, including any side-effects the read
     * might have as defined by the architecture.
     */
    TheISA::MiscReg readMiscRegOperand(const StaticInst *si, int idx)
    {
        return this->cpu->readMiscReg(
                si->srcRegIdx(idx) - TheISA::Misc_Reg_Base,
                this->threadNumber);
    }

    /** Sets a misc. register, including any side-effects the write
     * might have as defined by the architecture.
     */
    void setMiscRegOperand(const StaticInst *si, int idx,
                                     const MiscReg &val)
    {
        int misc_reg = si->destRegIdx(idx) - TheISA::Misc_Reg_Base;
        setMiscReg(misc_reg, val);
    }

    /** Called at the commit stage to update the misc. registers. */
    void updateMiscRegs()
    {
        // @todo: Pretty convoluted way to avoid squashing from happening when
        // using the TC during an instruction's execution (specifically for
        // instructions that have side-effects that use the TC).  Fix this.
        // See cpu/o3/dyn_inst_impl.hh.
        bool no_squash_from_TC = this->thread->noSquashFromTC;
        this->thread->noSquashFromTC = true;

        for (int i = 0; i < _numDestMiscRegs; i++)
            this->cpu->setMiscReg(
                _destMiscRegIdx[i], _destMiscRegVal[i], this->threadNumber);

        this->thread->noSquashFromTC = no_squash_from_TC;
    }

    void forwardOldRegs()
    {

        for (int idx = 0; idx < this->numDestRegs(); idx++) {
            PhysRegIndex prev_phys_reg = this->prevDestRegIdx(idx);
            TheISA::RegIndex original_dest_reg =
                this->staticInst->destRegIdx(idx);
            switch (regIdxToClass(original_dest_reg)) {
              case IntRegClass:
                this->setIntRegOperand(this->staticInst.get(), idx,
                                       this->cpu->readIntReg(prev_phys_reg));
                break;
              case FloatRegClass:
                this->setFloatRegOperandBits(this->staticInst.get(), idx,
                                             this->cpu->readFloatRegBits(prev_phys_reg));
                break;
              case CCRegClass:
                this->setCCRegOperand(this->staticInst.get(), idx,
                                      this->cpu->readCCReg(prev_phys_reg));
                break;
              case MiscRegClass:
                // no need to forward misc reg values
                break;
            }
        }
    }
    /** Calls hardware return from error interrupt. */
    Fault hwrei();
    /** Traps to handle specified fault. */
    void trap(Fault fault);
    bool simPalCheck(int palFunc);

    /** Emulates a syscall. */
    void syscall(int64_t callnum);

  public:

    // The register accessor methods provide the index of the
    // instruction's operand (e.g., 0 or 1), not the architectural
    // register index, to simplify the implementation of register
    // renaming.  We find the architectural register index by indexing
    // into the instruction's own operand index table.  Note that a
    // raw pointer to the StaticInst is provided instead of a
    // ref-counted StaticInstPtr to redice overhead.  This is fine as
    // long as these methods don't copy the pointer into any long-term
    // storage (which is pretty hard to imagine they would have reason
    // to do).

    uint64_t readIntRegOperand(const StaticInst *si, int idx)
    {
        //VUL_TRACKER REGISTER_FILE
        //this->vulT.vulOnRead(ST_REGFILE, RF_REGISTER, this->_srcRegIdx[idx]);
        if(this->cpu->rfVulEnable)
            this->cpu->regVulCalc.vulOnRead(this->_srcRegIdx[idx], this->seqNum);
        
        //VUL_TRACKER
        if(this->accessor == this->INST_Q)
            return this->cpu->readIntReg(this->_srcRegIdxIQ[idx]);
        else if(this->accessor == this->LS_Q)
            return this->cpu->readIntReg(this->_srcRegIdxLSQ[idx]);

        return this->cpu->readIntReg(this->_srcRegIdx[idx]);
    }

    FloatReg readFloatRegOperand(const StaticInst *si, int idx)
    {
        //VUL_TRACKER REGISTER_FILE
        //this->vulT.vulOnRead(ST_REGFILE, RF_REGISTER, this->_srcRegIdx[idx]);
        if(this->cpu->rfVulEnable)
            this->cpu->regVulCalc.vulOnRead(this->_srcRegIdx[idx], this->seqNum);
        
        //VUL_TRACKER
        if(this->accessor == this->INST_Q)
            return this->cpu->readFloatReg(this->_srcRegIdxIQ[idx]);
        else if(this->accessor == this->LS_Q)
            return this->cpu->readFloatReg(this->_srcRegIdxLSQ[idx]);

        return this->cpu->readFloatReg(this->_srcRegIdx[idx]);
    }

    FloatRegBits readFloatRegOperandBits(const StaticInst *si, int idx)
    {
        //VUL_TRACKER REGISTER_FILE
        //this->vulT.vulOnRead(ST_REGFILE, RF_REGISTER, this->_srcRegIdx[idx]);
        if(this->cpu->rfVulEnable)
            this->cpu->regVulCalc.vulOnRead(this->_srcRegIdx[idx], this->seqNum);
        
        //VUL_TRACKER
        if(this->accessor == this->INST_Q)
            return this->cpu->readFloatRegBits(this->_srcRegIdxIQ[idx]);
        else if(this->accessor == this->LS_Q)
            return this->cpu->readFloatRegBits(this->_srcRegIdxLSQ[idx]);

        return this->cpu->readFloatRegBits(this->_srcRegIdx[idx]);
    }

    uint64_t readCCRegOperand(const StaticInst *si, int idx)
    {
        //VUL_TRACKER REGISTER_FILE
        //this->vulT.vulOnRead(ST_REGFILE, RF_REGISTER, this->_srcRegIdx[idx]);
        if(this->cpu->rfVulEnable)
            this->cpu->regVulCalc.vulOnRead(this->_srcRegIdx[idx], this->seqNum);
        
        //VUL_TRACKER
        if(this->accessor == this->INST_Q)
            return this->cpu->readCCReg(this->_srcRegIdxIQ[idx]);
        else if(this->accessor == this->LS_Q)
            return this->cpu->readCCReg(this->_srcRegIdxLSQ[idx]);

        return this->cpu->readCCReg(this->_srcRegIdx[idx]);
    }

    /** @todo: Make results into arrays so they can handle multiple dest
     *  registers.
     */
    void setIntRegOperand(const StaticInst *si, int idx, uint64_t val)
    {
        //VUL_TRACKER REGISTER_FILE
        //this->vulT.vulOnWrite(ST_REGFILE, RF_REGISTER, this->_destRegIdx[idx]);
        if(this->cpu->rfVulEnable)
            this->cpu->regVulCalc.vulOnWrite(this->_destRegIdx[idx], this->seqNum);

        //VUL_TRACKER
        if(this->accessor == this->INST_Q)
            this->cpu->setIntReg(this->_destRegIdxIQ[idx], val);
        else if(this->accessor == this->LS_Q)
            this->cpu->setIntReg(this->_destRegIdxLSQ[idx], val);
        else
            this->cpu->setIntReg(this->_destRegIdx[idx], val);

        BaseDynInst<Impl>::setIntRegOperand(si, idx, val);
    }

    void setFloatRegOperand(const StaticInst *si, int idx, FloatReg val)
    {
        //VUL_TRACKER REGISTER_FILE
        //this->vulT.vulOnWrite(ST_REGFILE, RF_REGISTER, this->_destRegIdx[idx]);
        if(this->cpu->rfVulEnable)
            this->cpu->regVulCalc.vulOnWrite(this->_destRegIdx[idx], this->seqNum);

        //VUL_TRACKER
        if(this->accessor == this->INST_Q)
            this->cpu->setFloatReg(this->_destRegIdxIQ[idx], val);
        else if(this->accessor == this->LS_Q)
            this->cpu->setFloatReg(this->_destRegIdxLSQ[idx], val);
        else
            this->cpu->setFloatReg(this->_destRegIdx[idx], val);

        BaseDynInst<Impl>::setFloatRegOperand(si, idx, val);
    }

    void setFloatRegOperandBits(const StaticInst *si, int idx,
                                FloatRegBits val)
    {
        //VUL_TRACKER REGISTER_FILE
        //this->vulT.vulOnWrite(ST_REGFILE, RF_REGISTER, this->_destRegIdx[idx]);
        if(this->cpu->rfVulEnable)
            this->cpu->regVulCalc.vulOnWrite(this->_destRegIdx[idx], this->seqNum);

        //VUL_TRACKER
        if(this->accessor == this->INST_Q)
            this->cpu->setFloatRegBits(this->_destRegIdxIQ[idx], val);
        else if(this->accessor == this->LS_Q)
            this->cpu->setFloatRegBits(this->_destRegIdxLSQ[idx], val);
        else
            this->cpu->setFloatRegBits(this->_destRegIdx[idx], val);

        BaseDynInst<Impl>::setFloatRegOperandBits(si, idx, val);
    }

    void setCCRegOperand(const StaticInst *si, int idx, uint64_t val)
    {
        //VUL_TRACKER REGISTER_FILE
        //this->vulT.vulOnWrite(ST_REGFILE, RF_REGISTER, this->_destRegIdx[idx]);
        if(this->cpu->rfVulEnable)
            this->cpu->regVulCalc.vulOnWrite(this->_destRegIdx[idx], this->seqNum);

        //VUL_TRACKER
        if(this->accessor == this->INST_Q)
            this->cpu->setCCReg(this->_destRegIdxIQ[idx], val);
        else if(this->accessor == this->LS_Q)
            this->cpu->setCCReg(this->_destRegIdxLSQ[idx], val);
        else
            this->cpu->setCCReg(this->_destRegIdx[idx], val);

        BaseDynInst<Impl>::setCCRegOperand(si, idx, val);
    }

#if THE_ISA == MIPS_ISA
    uint64_t readRegOtherThread(int misc_reg)
    {
        panic("MIPS MT not defined for O3 CPU.\n");
        return 0;
    }

    void setRegOtherThread(int misc_reg, const TheISA::MiscReg &val)
    {
        panic("MIPS MT not defined for O3 CPU.\n");
    }
#endif

  public:
    /** Calculates EA part of a memory instruction. Currently unused,
     * though it may be useful in the future if we want to split
     * memory operations into EA calculation and memory access parts.
     */
    Fault calcEA()
    {
        return this->staticInst->eaCompInst()->execute(this, this->traceData);
    }

    /** Does the memory access part of a memory instruction. Currently unused,
     * though it may be useful in the future if we want to split
     * memory operations into EA calculation and memory access parts.
     */
    Fault memAccess()
    {
        return this->staticInst->memAccInst()->execute(this, this->traceData);
    }
};

#endif // __CPU_O3_ALPHA_DYN_INST_HH__

