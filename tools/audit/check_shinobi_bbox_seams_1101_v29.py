"""Header, injury-compaction and actual interrupt seams for bbox design."""
import json
import check_shinobi_bbox_design_1101_v29 as C
import check_hogan_current_bounded_v1 as M
from check_tmnt_render_oa import address


def seed(b,labels):
 b['segs']['shinobi_rom']={'start':str(0xa800),'ooffs':str(16+65*8192+0x800)}
 for n,a in labels.items():
  if n.startswith('Sh')and 0xa800<=a<0xae00:b['syms'][n]={'val':str(a),'seg':'shinobi_rom'}
 m=M.fresh(b);M.put(m,SelectedCharacter=36,OperMode=1,FamilyMainCommit=1,DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255,Mirror_PPUCTRL=160,Player_X_Position=120,Player_Y_Position=176,Player_Y_HighPos=1,Player_Rel_XPos=120,Player_Rel_YPos=176,Player_BoundBoxCtrl=1)
 M.invoke(m,'ShScene');return m


def main():
 old,new,k=C.proposal();P=C.P
 oldlab=P.S.labels(P.O/'resident-original.lbl');lab=P.S.labels(P.O/'resident-design.lbl')
 before,after=seed(old,oldlab),seed(new,lab);injury=0
 cases=[dict(hp=hp,face=face)for hp in range(7)for face in [0,4]]+[{name:value}for name,value in [('state',10),('state',16),('flag',2),('magic_lo',1),('magic_hi',1),('death',2)]]
 for case in cases:
  for flags in [0x30,0x31,0x70,0xf1]:
   pair=[]
   for s in [before,after]:
    m=M.fork(s)
    for at,value in {0x539:case.get('hp',6),0x363:case.get('face',0),0x413:case.get('state',0),0x460:case.get('flag',0),0x54c:case.get('magic_lo',0),0x54d:case.get('magic_hi',0),0x38:case.get('death',0)}.items():m.ram[2][at]=value
    m[3:11]=bytes(range(0xa1,0xa9));r=M.invoke(m,'HuInjury',a=0x55,x=3,y=0x57,p=flags)
    pair.append((tuple(r[n]for n in ['A','X','Y','P']),bytes(m[:256]),bytes(m[0x200:0x800]),bytes(m.ram[2][:0x1000]),m.rawtags,[M.get(m,n)for n in ['CurrentBank','CurrentBankC']]))
   assert pair[0]==pair[1],('Injury compaction',case,flags);injury+=1
 rejected=0
 for bank in [2,3]:
  for byte in range(16):
   m=M.fork(after);m.ram[bank][0x1fe0+byte]^=1;state=bytes(m.ram[2][:0x1000]);M.invoke(m,'LmBoundingBoxGate',a=0x55,x=0,y=0,p=0x31)
   assert list(m[address(new,'BoundingBox_UL_Corner'):address(new,'BoundingBox_UL_Corner')+4])==[123,196,133,208]
   assert bytes(m.ram[2][:0x1000])==state;rejected+=1
 # Probe each reached changed instruction immediately, retaining only one
 # interrupt fixture in memory. No per-case/frame artifacts or snapshots.
 cls=M.NesMPU;step=cls.step;active=True;seen=set();cut_count=0;minimum=255;cycles=[]
 def state(c):return(c.pc,c.a,c.x,c.y,c.p,c.sp)
 def probe(c):
  nonlocal active,cut_count,minimum
  pc=c.pc;m0=c.memory;tag=m0.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else None
  changed=tag==193 and(lab['ShInjury']<=pc<lab['ShColors']or lab['ShBBoxIngress']<=pc<0xadfe)or tag==3 and 0xbaf8<=pc<0xbbbA or 0x15a<=pc<0x17b
  key=(pc,c.sp,tag)
  if active and changed and key not in seen:
   seen.add(key);active=False
   try:
    for kind in ['IRQ','lag-NMI']:
     m=M.fork(m0);s=state(c);z=cls(memory=m,pc=pc);z.pc,z.a,z.x,z.y,z.p,z.sp=s
     smc=bytes(m[0x15a:0x17b]);live=bytes(m[0x101+z.sp:0x200]);maps=m.rawtags[:];shadows=[M.get(m,n)for n in ['CurrentBank','CurrentBankC']]
     for slot,name,lo in [(1,'CurrentBank',0x15),(2,'CurrentBankC',0x16)]:
      if kind=='lag-NMI'and maps[slot]!=M.get(m,name):
       assert m[z.pc]in [0x8c,0x8d,0x8e]and m[z.pc+1:z.pc+3]==[lo,0x51],('Mapper seam',hex(z.pc),maps,shadows)
       maps[slot]=M.get(m,name)
     if kind=='IRQ':z.irq()
     else:z.nmi()
     for _ in range(100000):
      minimum=min(minimum,z.sp)
      if state(z)==s:break
      assert m[z.pc],(kind,hex(pc),'ISR BRK',hex(z.pc),m.rawtags)
      step(z)
     else:raise AssertionError((kind,hex(pc),'ISR bound',state(z)))
     assert bytes(m[0x15a:0x17b])==smc and bytes(m[0x101+z.sp:0x200])==live,(kind,hex(pc),'SMC/live stack')
     assert m.rawtags==maps and[M.get(m,n)for n in ['CurrentBank','CurrentBankC']]==shadows,(kind,hex(pc),'mapping')
     assert bytes(m[3:11])==bytes(m0[3:11])and m.ram==m0.ram,(kind,hex(pc),'foreground/WRAM')
     cut_count+=1;cycles.append(z.processorCycles)
   finally:active=True
  return step(c)
 cls.step=probe
 try:
  for owner in [0,19,35,36]:
   m=M.fork(after);M.put(m,SelectedCharacter=owner);M.invoke(m,'LmBoundingBoxGate',a=0x55,x=0,y=0,p=0x31)
  for hp in [6,0]:
   m=M.fork(after);m.ram[2][0x539]=hp;M.invoke(m,'HuInjury',a=0x55,x=3,y=0x57,p=0x31)
 finally:cls.step=step
 q=dict(passed=True,ROM_written=False,baseline_sha256=P.S.sha(getattr(P,'CURRENT_BASE',P.BASE)),ROM_sha256=P.S.sha(P.CANDIDATE)if hasattr(P,'CANDIDATE')else None,injury_compaction_cases=injury,both_header_fallback_cases=rejected,interrupt_cuts=cut_count,unique_PC_SP_bank_boundaries=len(seen),minimum_standalone_ISR_SP=minimum,ISR_cycles=[min(cycles),max(cycles)],scope='In-memory assembly proposal or exact specified candidate. Exact source injury/health/death/immunity comparison; all32 full-header poisons use genuine native small-body fallback without private state writes. Real native IRQ and lag-NMI at reached new gate/worker/compacted injury/FarCall boundaries preserve foreground AXYP/PC/SP, live stack,33SMC bytes, R0..7, maps/bank shadows and all PRGRAM. No actual Main nested-stack/native video/controller claim.')
 (getattr(P,'CHECK_OUTPUT',P.O)/'seams-CPU.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))


if __name__=='__main__':main()
