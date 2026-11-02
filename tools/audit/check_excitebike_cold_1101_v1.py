"""Current-image contiguous cold-copy and actual disabled-NMI instruction cuts.

Fixtures stay in memory. Each distinct resident PC/stack/page boundary receives
the actual native NMI, including every upper-latch-to-low-register interval.
"""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
import check_hogan_current_bounded_v1 as M
from prepare_excitebike_host_1101_v1 import BASE,PIN
from prepare_excitebike_dispatch_1101_v1 import O,sha,save,labels
from compose_excitebike_current_1101_v1 import compose


def bundle():
    raw,_,_=compose(require_cpu=False);b=scoped_load(BASE);b['raw']=raw
    b['segs']['excitebike_resident']={'start':str(0xa000),'ooffs':str(16+65*8192)}
    for n,a in labels(O/'scene.lbl').items():
        b['syms'][n]={'val':str(a),'seg':'excitebike_resident'}
    for row in range(37):b['syms'][f'ExService{row}']={'val':str(0xb08c+3*row),'seg':'excitebike_resident'}
    return b


def seed(b):
    m=M.fresh(b)
    M.put(m,SelectedCharacter=37,OperMode=1,FamilyMainCommit=1,DisableScreenFlag=1,
          Mirror_PPUMASK=0,NmiDisable=255,Mirror_PPUCTRL=160,ReloadCHRBank=1)
    # A previous scene may leave any source-clock mailbox or pending atlas
    # publication armed. The disabled owner guard must precede those consumers.
    for name in ['GmClock','GmFresh','GmPending','ReloadCHRBank','X5ChrMode','SsChrActive','X5WideChrActive']:
        if name in b['syms']:m[address(b,name)]=255
    return m


def checked(m,*,interrupts=False,irq=False):
    native=M.NesMPU;cuts=set();isr_count=0;critical=0;pagewrites=[];sei_seen=False
    class Check(native):
        def step(self):
            nonlocal isr_count,critical,sei_seen
            mem=self.memory
            resident=mem.rawtags[1]==193 and 0xae00<=self.pc<0xb061
            # The copy and verify sites call MapRow with the same SP/page.
            # Include their actual stacked return PC so neither callsite is
            # deduplicated into the other one's high/low latch proof.
            caller=mem[0x100+((self.sp+1)&255)]+256*mem[0x100+((self.sp+2)&255)]
            key=(self.pc,self.sp,mem[address(b,'R2')],caller)
            if interrupts and resident and key not in cuts and(not irq or(not sei_seen and not self.p&4)):
                cuts.add(key)
                # Match continuation registers, stack, mapper state, CHR latch,
                # PPU buffered-read state, native scratch and farcall operands.
                regs=(self.a,self.x,self.y,self.p,self.sp,self.pc)
                maps=list(mem.rawtags);logical_c=mem[address(b,'CurrentBankC')]
                chrstate=(mem.upper,list(mem.chr_latches),mem.lastset)
                ppustate=(mem.ppu_addr,mem.toggle,mem.buffer,mem.ppuctrl,mem.ppu_reads)
                scratch=bytes(mem[address(b,'R0'):address(b,'R7')+1])
                smc=bytes(mem[0x15a:0x17b]);ram=[bytes(z)for z in mem.ram]
                start=len(mem.writes);pc,sp=self.pc,self.sp
                if mem.upper==2:critical+=1
                if irq:self.irq()
                else:self.nmi()
                for _ in range(200000):
                    if self.pc==pc and self.sp==sp:break
                    assert mem[self.pc]!=0,('NMI BRK',key,hex(self.pc))
                    if self.pc>=0x8000:
                        assert mem.rawtags[(self.pc-0x8000)//8192]&128,('NMI called conditional RAM',key,hex(self.pc))
                    native.step(self)
                else:raise AssertionError(('NMI return bound',key))
                assert regs==(self.a,self.x,self.y,self.p,self.sp,self.pc),('NMI registers',key)
                # Native NMI restores CurrentBankC. A cut between a loader's
                # shadow write and its immediately following $5116 write may
                # legitimately complete that same mapping one instruction early.
                if not irq:maps[2]=logical_c
                assert maps==mem.rawtags,('ISR PRG mapper',irq,key,maps,mem.rawtags)
                if not irq:
                    assert chrstate==(mem.upper,list(mem.chr_latches),mem.lastset),('NMI CHR mapper',key)
                    assert ppustate==(mem.ppu_addr,mem.toggle,mem.buffer,mem.ppuctrl,mem.ppu_reads),('NMI PPU',key)
                assert scratch==bytes(mem[address(b,'R0'):address(b,'R7')+1])and smc==bytes(mem[0x15a:0x17b]),('NMI scratch/SMC',key)
                assert ram==[bytes(z)for z in mem.ram],('NMI private RAM',key)
                writes=[(i,v)for i,v in mem.writes[start:]if 0x5120<=i<=0x5130]
                if irq:assert mem.upper==0 and all(i==0x5128 and v==0 for i,v in writes),('IRQ font only, latch zero',key,writes)
                else:assert not writes,('NMI CHR write',key)
                isr_count+=1
            op=mem[self.pc]
            if resident and op==0x78:sei_seen=True
            # Capture actual low-register latch consumption from the actual
            # source selector, not its expected arithmetic in the test.
            if resident and op==0x8d and mem[self.pc+1]==0x23 and mem[self.pc+2]==0x51:
                pagewrites.append(self.a+256*mem.upper)
            return native.step(self)
    M.NesMPU=Check
    try:z=M.invoke(m,'ExLoad',p=0x31)
    finally:M.NesMPU=native
    assert z['P']&1 and m.ppu_reads==16400
    assert bytes(m.ram[3][:6144])==(O/'host-kernel.bin').read_bytes()
    assert bytes(m.ram[2][0x1000:0x1800])==(O/'host-metadata.bin').read_bytes()
    assert not any(m.ram[2][:0x1000])and not any(m.ram[2][0x1800:0x1fe0])
    cookie=(O/'host-cookie.bin').read_bytes()
    assert all(bytes(m.ram[k][0x1fe0:0x1ff0])==cookie for k in [2,3])
    assert pagewrites==[p for p in range(728,736)for _ in [0,1]],pagewrites
    assert m.upper==0 and m.ppuctrl==160 and m.toggle==0
    assert m.ppu_log[-2:]==[(0x2005,0),(0x2005,0)]
    assert M.get(m,'ReloadCHRBank')==255 and M.get(m,'NmiDisable')==255
    before=([bytes(z)for z in m.ram],m.ppu_reads,list(m.chr_latches),m.upper,list(m.rawtags))
    warm=M.invoke(m,'ExLoad',p=0x30)
    assert warm['P']&1
    assert before==([bytes(z)for z in m.ram],m.ppu_reads,list(m.chr_latches),m.upper,list(m.rawtags))
    return dict(cold_cycles=z['CPU'],warm_cycles=warm['CPU'],actual_disabled_NMI_cuts=isr_count,
                upper_latch_live_NMI_cuts=critical,actual_copy_verify_pages=pagewrites,
                PPU_reads=m.ppu_reads,final_upper_latch=m.upper)


def main():
    global b
    b=bundle();plain=checked(seed(b));cuts=checked(seed(b),interrupts=True)
    irq=checked(seed(b),interrupts=True,irq=True)
    assert cuts['actual_disabled_NMI_cuts']>100 and cuts['upper_latch_live_NMI_cuts']==80
    q=dict(passed=True,base_ROM_SHA256=PIN,memory_candidate_SHA256=hashlib.sha256(b['raw']).hexdigest(),
           plain=plain,interrupted=cuts,pre_SEI_IRQ=irq,copy_and_readback_all_8192_bytes=True,
           cookie_both_complete_headers=True,no_NMI_CHR_writes_or_RAM_callbacks=True,
           pending_scene_and_mailbox_armed=True,final_upper_latch_zero=True,
           IRQ_masked_by_original_SEI_in_cold_copy=True,native=False,installed=False,
           scope='Actual current binary loader and disabled-native NMI at every distinct resident PC/SP/page boundary, including all sixteen high-to-low latch sequences. Mapper/PPU peripheral model; physical cold start remains required.',
           bindings={p.relative_to(R).as_posix():sha(p)for p in [Path(__file__),O/'scene-assembly.json',O/'host-assembly.json',O/'router-assembly.json',BASE]})
    save('cold-CPU.json',q);print(json.dumps(q))

if __name__=='__main__':main()
