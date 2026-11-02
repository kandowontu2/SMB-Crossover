"""Actual immutable helper ABI, queue publication and IRQ/lagNMI cuts."""
import json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import bubble_bobble_native_model_1101_v3 as B
N=B.N;O=B.O


def main():
 checks={};cases=0;b=B.scoped_load(B.BASE)
 for identity in[0,1]:
  for row in[1,18,26,30]:
   for mode in[0,1]:
    for offset in[0,44,45,63]:
     h=B.Host(identity,b);h.put(OperMode=mode,VRAM_Buffer1_Offset=offset)
     at=h.at('VRAM_Buffer1');h.m[at:at+84]=[119]*84;before=bytes(h.m[at:at+84]);scratch=bytes(h.m[3:11]);immutable=bytes(h.s[0x1000:0x1400])
     c=h.source(0xa000+row*3,a=85,x=71,y=109,p=0xf1)
     assert(c.a,c.x,c.y,c.p)==(85,71,109,0xf1),(identity,row,mode,offset,c.a,c.x,c.y,c.p)
     assert bytes(h.m[3:11])==scratch and bytes(h.s[0x1000:0x1400])==immutable
     if row==1:
      assert h.get('CurrentCHRBank',4)==185 and h.get('X5ChrMode',4)==129 and h.get('SsChrActive')==0 and h.get('X5WideChrActive')==1
      assert h.m[h.at('ObjectMetasprite')]==0 and h.get('SmPosePtr')+256*h.get('SmPosePtr',1)==h.at('ObjectMetasprite')
     elif offset>=45:assert bytes(h.m[at:at+84])==before and h.get('VRAM_Buffer1_Offset')==offset
     else:
      if row==26:expected=[63,17 if identity else 29,3]+([44,35,48]if identity else[42,38,48])
      else:
       name=[11,24 if identity else 30,11]
       expected=([35,40,16]+[36]*6+name+[36]*7)if mode==0 else([32,67,7]+name+[36]*4)
      assert list(h.m[at+offset:at+offset+len(expected)])==expected
      assert h.get('VRAM_Buffer1_Offset')==offset+len(expected)and h.m[at+offset+len(expected)]==0
     cases+=1
 checks['full_helper_AXYP_R0_7_immutable_queue_cases']=cases
 # Legal native Mario surface fixture for actual completed NMI publication;
 # this tests the helper packet/CHR mechanism, not raw39 owner admission.
 for identity in[0,1]:
  h=B.Host(identity,b);h.put(OperMode=1,VRAM_Buffer1_Offset=0)
  h.source(0xa003);h.source(0xa000+26*3);h.put(NmiDisable=0);N.consume(h.m)
  palette=0x3f11 if identity else 0x3f1d;expected=[44,35,48]if identity else[42,38,48]
  assert list(h.m.vram[palette:palette+3])==expected and h.m.chr_latches[4]==441
 checks['actual_completed_NMI_CHR_RGB_cases']=2
 native=N.NesMPU;total=0;by={};pcs=set();low=255
 for row,mode in[(1,1),(26,1),(30,1),(18,0),(17,1)]:
  seed=B.Host(1,b);seed.put(OperMode=mode,NmiDisable=1,VRAM_Buffer1_Offset=0,CurrentOAMOffset=0,GuestOamRotationActive=0);cuts=set()
  class Trace(native):
   def step(self):
    if self.memory.rawtags[2]==2 and 0xd320<=self.pc<0xd400:cuts.add((self.pc,self.sp))
    return native.step(self)
  N.NesMPU=Trace
  try:seed.source(0xa000+row*3,p=0x30)
  finally:N.NesMPU=native
  for kind in['IRQ','lagNMI']:
   for cut in sorted(cuts):
    h=B.Host(1,b);h.put(OperMode=mode,NmiDisable=1,VRAM_Buffer1_Offset=0,CurrentOAMOffset=0,GuestOamRotationActive=0);injected=False
    class Interrupt(native):
     def step(self):
      nonlocal injected,low
      mem=self.memory
      if not injected and mem.rawtags[2]==2 and(self.pc,self.sp)==cut:
       injected=True;regs=(self.a,self.x,self.y,self.p,self.sp,self.pc);maps=list(mem.rawtags);private=[bytes(mem.ram[k])for k in[2,3]];scratch=bytes(mem[3:11]);smc=bytes(mem[0x15a:0x17b])
       assert not self.p&4
       self.irq()if kind=='IRQ'else self.nmi()
       for _ in range(200000):
        low=min(low,self.sp)
        if self.pc==regs[5]and self.sp==regs[4]:break
        assert mem[self.pc]!=0,(kind,cut,hex(self.pc));native.step(self)
       else:raise AssertionError(('ISR return bound',kind,cut))
       assert regs==(self.a,self.x,self.y,self.p,self.sp,self.pc)and maps==mem.rawtags and mem.upper==0
       assert private==[bytes(mem.ram[k])for k in[2,3]]and scratch==bytes(mem[3:11])and smc==bytes(mem[0x15a:0x17b])
      return native.step(self)
    N.NesMPU=Interrupt
    try:h.source(0xa000+row*3,p=0x30)
    finally:N.NesMPU=native
    assert injected;total+=1;by[kind]=by.get(kind,0)+1;pcs.add(cut[0])
 checks['actual_IRQ_lagNMI']=dict(cuts=total,by_kind=by,distinct_helper_PCs=len(pcs),minimum_ISR_SP=low,exact_AXYP_SP_PC_scratch_SMC_maps_private=True)
 q=dict(passed=True,base_ROM_SHA256=B.PIN,ROM_written=False,shared_routing_installed=False,checks=checks,scope='Actual bound private vectors and real immutable helper6502. Original legal native surface fixture for actual NMI queue/CHR publication. Every distinct reached helper instruction/SP for IRQ and Main-busy NMI preserves actor/code/helper/foreground scratch and mapper context. No raw39 normal Main/menu/native emulator admission claim.',bindings={p.relative_to(R).as_posix():B.P.B.sha(p.read_bytes())for p in[Path(__file__),R/'tools/reference/bubble_bobble_helpers_1102_v1.inc',R/'tools/audit/prepare_bubble_bobble_helpers_1102_v1.py',O/'native-private.bin',O/'native-helper.chr',O/'native-helpers-layout.json']})
 (O/'native-helpers-CPU.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(passed=True,helper_cases=cases,actual_NMI_cases=2,IRQ_lagNMI_cuts=total,ROM_written=False)))


if __name__=='__main__':main()
