"""Actual IRQ/lag-NMI cuts throughout changed current Arthur code."""
import json
import prepare_arthur_auth_fast_1101_v2 as P
import check_hogan_current_bounded_v1 as M
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location

def main():
 b=scoped_load(P.O/'candidate.nes');seed=M.fresh(b)
 sig=b['raw'][location(b,'ArCacheSignature'):location(b,'ArCacheSignature')+16]
 seed.ram[2][0x1fe0:0x1ff0]=sig
 M.put(seed,SelectedCharacter=32,OperMode=1,GameEngineSubroutine=8,ArHostReady=167,FamilyMainCommit=1,NmiDisable=255)
 cls=M.NesMPU;old=cls.step;cuts=[];record=True
 def state(c):return (c.pc,c.a,c.x,c.y,c.p,c.sp)
 def probe(c):
  if record and c.pc>=0x8000 and c.memory.rawtags[(c.pc-0x8000)//8192]==198 and (0xbd00<=c.pc<0xbf7a or 0xc7b9<=c.pc<0xc7e3 or 0xdf10<=c.pc<0xdf7a):
   cuts.append((M.fork(c.memory),state(c)))
  return old(c)
 cls.step=probe
 try:
  for name in ['HuVisible','HuBody','HuAdder','HuBox','HuUi','HuWeaponTail']:
   M.invoke(M.fork(seed),name,p=0x31)
 finally:cls.step=old
 # Deduplicate only identical PCs and stack depths; exercise both the SMC
 # early-write and the shadow/hardware mapper seam at their real callers.
 unique={}
 for m,s in cuts:unique.setdefault((s[0],s[-1]),(m,s))
 rows=[]
 for kind in ['IRQ','lag-NMI']:
  for m0,s in unique.values():
   m=M.fork(m0);c=cls(memory=m,pc=s[0]);c.pc,c.a,c.x,c.y,c.p,c.sp=s
   before=state(c);smc=bytes(m[0x15a:0x17b]);live=bytes(m[0x101+c.sp:0x200]);maps=m.rawtags[:]
   shadows=[M.get(m,'CurrentBank'),M.get(m,'CurrentBankC')]
   for slot,n,op in [(1,'CurrentBank',b'\x8d\x15\x51'),(2,'CurrentBankC',b'\x8d\x16\x51')]:
    if kind=='lag-NMI' and maps[slot]!=M.get(m,n):
     assert bytes(m[c.pc:c.pc+3])==op;maps[slot]=M.get(m,n)
   if kind=='IRQ':c.irq()
   else:c.nmi()
   for i in range(100000):
    if state(c)==before:break
    assert m[c.pc]!=0,(kind,hex(before[0]),'BRK',hex(c.pc),m.rawtags)
    c.step()
   else:raise AssertionError((kind,hex(before[0]),'ISR return timeout',state(c)))
   assert bytes(m[0x15a:0x17b])==smc,(kind,hex(before[0]),'SMC')
   assert bytes(m[0x101+c.sp:0x200])==live,(kind,hex(before[0]),'live stack')
   assert m.rawtags==maps and [M.get(m,'CurrentBank'),M.get(m,'CurrentBankC')]==shadows,(kind,hex(before[0]),'mapping')
   for n in ['ArTemp','ArTempHi','R0','R1']:
    assert M.get(m,n)==M.get(m0,n),(kind,hex(before[0]),n)
   assert m.ram==m0.ram,(kind,hex(before[0]),'WRAM')
   rows.append(dict(kind=kind,pc=before[0],SP=before[-1],cycles=c.processorCycles))
 q=dict(passed=True,cuts=len(rows),unique_boundaries=len(unique),ROM_sha256=P.sha(P.O/'candidate.nes'),scope='Actual native IRQ and lag-NMI at every reached changed policy/auth instruction, foreground AXYP/PC/SP, live stack,33SMC bytes,maps,ArTemp/R0/R1 and allWRAM retained. Warm source clock mailbox inactive in this fixture; controller test exercises actual clock.',rows=rows)
 (P.O/'ISR.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items() if k!='rows'}))
if __name__=='__main__':main()
