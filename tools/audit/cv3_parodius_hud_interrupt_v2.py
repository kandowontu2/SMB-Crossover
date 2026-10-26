"""Inject exact-composition lag NMI/IRQ at retained Parodius helper boundaries."""
from pathlib import Path
import argparse,hashlib,json
from parodius_visibility_hud_cancel_cpu_v2 import setup
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--expected-sha256',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 assert sha(a.rom)==a.expected_sha256;b=scoped_load(a.rom)
 smc=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2]
 ranges=[(77,address(b,'PnHudCancelLife'),address(b,'PnHudNewLife')),(77,address(b,'PnHudCancelGateway'),address(b,'PnHudCancelGateway')+15),(116,address(b,'PnHudCancelWork'),address(b,'PnHudCancelWork')+int(b['syms']['PnHudCancelWork']['size'],0))]
 ownernames=['InvHudActive','InvHudPhysical','X5HudChrUpper','VvHudDirty','VRAM_Buffer1_Offset','VRAM_Buffer2_Offset','VRAM_Buffer_AddrCtrl']
 rows=[];case=None
 def make(kind):
  q=setup(b,active=3);q.put(Mirror_PPUMASK=30,Mirror_PPUCTRL=0xa8,Sprite0HitDetectFlag=1,NmiDisable=255)
  name='VvDeathStart'if kind=='death-hold'else'VvReset'if kind=='reset-full'else'VvEnsure'if kind=='ensure-full'else'PnHudNewLife'
  if kind!='death-hold':
   if kind=='newlife-attr':q.invoke('PnHud')
   else:q.put(InvHudActive=0,InvHudPhysical=0);q.invoke('PnHud');tail=[0x20,0x40,3,7,8,9];q.array('VRAM_Buffer1',[q.get('VRAM_Buffer1',i)for i in range(42)]+tail+[0]);q.set('VRAM_Buffer1_Offset',48)
  if kind=='ensure-full':q.put(VvLife=255,NumberofLives=1)
  if kind=='reset-full':q.put(OperMode_Task=0,DisableScreenFlag=1)
  at=location(b,name);pc=address(b,name);w=(pc-0x8000)//8192;q.m.page(w,(at-16)//8192)
  q.set('CurrentBank'if w==1 else'CurrentBankC',q.m.banks[w]|128)
  c=NesMPU(memory=q.m,pc=pc);c.a,c.x,c.y,c.p,c.sp=0,37,193,0x30,0xfd;c.stPushWord(0x5aff)
  return q,c,name
 def HUD(q):return({n:q.get(n)for n in ownernames},bytes(q.m[address(b,'VRAM_Buffer1'):address(b,'VRAM_Buffer1')+84]),bytes(q.m[address(b,'VRAM_Buffer2'):address(b,'VRAM_Buffer2')+84]))
 try:
  for kind in ['death-hold','newlife-full','newlife-attr','reset-full','ensure-full']:
   q,c,name=make(kind);boundaries=[];step=0
   while c.pc!=0x5b00:
    bank=q.m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
    if any(bank==bk and lo<=c.pc<hi for bk,lo,hi in ranges):boundaries.append((step,c.pc,bank))
    c.step();step+=1;assert step<100000
   final=HUD(q);regs=(c.a,c.x,c.y,c.p,c.sp);banks=q.m.banks[:]
   for interrupt in ['nmi','irq']:
    for boundary,pc,bank in boundaries:
     case=dict(path=kind,interrupt=interrupt,boundary=boundary,PC=pc,bank=bank);r,d,_=make(kind)
     for _ in range(boundary):d.step()
     assert d.pc==pc
     before=HUD(r);shadows=(r.get('CurrentBank'),r.get('CurrentBankC'));physical=r.m.banks[:];fields=[r.m[i]for i in smc];state=(d.a,d.x,d.y,d.p,d.sp);at=d.pc
     pending=physical[2]!=(shadows[1]&127)
     if pending:assert r.m[at:at+3]==[0x8d,0x16,0x51],'Only exact adjacent shadow-to-5116 transition'
     if interrupt=='irq':r.m[0x5204]=0x80
     before_writes=len(r.m.writes);start_cycles=d.processorCycles;getattr(d,interrupt)();minimum=d.sp;steps=0
     while not(d.pc==at and d.sp==state[4]):
      d.step();minimum=min(minimum,d.sp);steps+=1;assert steps<100000,('Interrupt timeout',case,d.pc)
     assert steps>0 and(d.a,d.x,d.y,d.p,d.sp)==state,('Interrupt AXYP/SP',case,state,(d.a,d.x,d.y,d.p,d.sp))
     assert(shadows==(r.get('CurrentBank'),r.get('CurrentBankC'))and fields==[r.m[i]for i in smc])
     expected=physical[:]
     if interrupt=='nmi'and pending:expected[2]=shadows[1]&127
     assert r.m.banks==expected,('Actual bank return',case,physical,shadows,r.m.banks)
     assert HUD(r)==before,('Interrupt changed live HUD queue ownership',case)
     # The real IRQ intentionally writes2006 for native scroll. It does not
     # write tile data. Lag NMI also leaves the VRAM address transaction alone.
     forbidden=[0x2006,0x2007]if interrupt=='nmi'else[0x2007]
     assert not any(p in forbidden for p,v in r.m.writes[before_writes:]),'No interleaved lag-NMI/IRQ VRAM data command'
     handler=d.processorCycles-start_cycles
     for _ in range(100000):
      if d.pc==0x5b00:break
      d.step()
     else:raise AssertionError('Full caller failed after interrupt')
     assert HUD(r)==final and(d.a,d.x,d.y,d.p,d.sp)==regs and r.m.banks==banks,('Full caller continuation',case)
     rows.append(dict(case,actual_handler_instructions=steps,handler_cycles=handler,min_SP=minimum,
                      same_AXYP_SP_fiveSMC_shadows=True,physical_pending_transition=pending,only_proven_NMI_shadow_commit=True,
                      exact_HUD_queue_state_across_handler=True,whole_caller_HUD_queue_register_bank_continuation_exact=True))
 except Exception as ex:
  (a.output/'failure.json').write_text(json.dumps(dict(passed=False,native_run=False,error=repr(ex),case=case,completed=rows),indent=2)+'\n');raise
 (a.output/'cases.json').write_text(json.dumps(rows,indent=2)+'\n');q=dict(passed=True,native_run=False,ROM_sha256=sha(a.rom),cases=len(rows),
          min_SP=min(x['min_SP']for x in rows),pending_transition_controls=sum(x['physical_pending_transition']for x in rows),tool_sha256=sha(Path(__file__)),cases_sha256=sha(a.output/'cases.json'),
          limits='Actual linked handlers at every executed new helper/gate/restore instruction boundary on five synthetic real foreground callers. NmiDisable255 models the real private GameLoop owner. Handler audio/timer RAM changes are their normal native effects, not claimed absent; exact HUD queues/metadata/AXYP/SP/banks/fiveSMC and full caller continuation are checked. No physical PPU/DMA/raster/DMC/native-replay guarantee.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
