"""Inject actual lag NMI at each private foreground instruction boundary."""
from pathlib import Path
import argparse,hashlib,json
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address
from verify_native_relocation import NesMPU
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);b=scoped_load(a.rom);rows=[]
 smc=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2]
 def setup(active,dirty):
  q=Arena(b,18);q.put(DisableScreenFlag=0,VvVariant=1,VvMeter=0x55,VvHudDirty=dirty,InvHudActive=active,X5HudChrUpper=1,VRAM_Buffer1_Offset=0,ReloadCHRBank=0,PnInitialized=0x50,PnBombPaletteReady=1,PnBombCapturePending=0,VRAM_Buffer_AddrCtrl=0,NmiDisable=255,Mirror_PPUCTRL=0xa0,Sprite0HitDetectFlag=1);q.array('VRAM_Buffer1',[0]*84);q.m.page(1,77);q.set('CurrentBank',205);q.m.writes=[];c=NesMPU(memory=q.m,pc=address(b,'PnHud'));c.sp=0xfd;c.p=0x30;c.stPushWord(0x5aff);return q,c
 for active,dirty in [(0,1),(3,1),(3,0)]:
  q,c=setup(active,dirty);trace=[]
  while c.pc!=0x5b00:
   assert len(trace)<2000;trace.append(c.pc);c.step()
  expected=([q.get('VRAM_Buffer1',i)for i in range(84)],[q.get(n)for n in ['InvHudActive','InvHudPhysical','X5HudChrUpper','VvHudDirty','VRAM_Buffer1_Offset','VvTemp','VvTemp2']])
  for boundary in range(len(trace)):
   q,c=setup(active,dirty)
   for _ in range(boundary):c.step()
   pc,sp=c.pc,c.sp;regs=(c.a,c.x,c.y,c.p);smcbefore=[q.m[i]for i in smc];shadow=q.get('CurrentBankC');actual=q.m.banks[2];writes=len(q.m.writes);start=c.processorCycles;c.nmi();nmi_steps=0
   while not(c.pc==pc and c.sp==sp):
    assert nmi_steps<60000,('NMI timeout',hex(c.pc),q.m.banks)
    c.step();nmi_steps+=1
   assert (c.a,c.x,c.y,c.p)==regs,('NMI foreground ABI',boundary,hex(pc),regs,(c.a,c.x,c.y,c.p))
   assert [q.m[i]for i in smc]==smcbefore and q.get('CurrentBankC')==shadow and q.m.banks[2]==(shadow&127)
   # The only accepted initial mismatch is precisely an A77 STA$5116 about
   # to finish the adjacent shadow-before-hardware convention.
   if actual!=(shadow&127):assert q.m[pc:pc+3]==[0x8d,0x16,0x51]and q.m.banks[1]==77
   assert not any(at==0x4014 for at,v in q.m.writes[writes:]),'Lag NMI cannot flush an incomplete foreground queue'
   nmi_cycles=c.processorCycles-start
   for remaining in range(5000):
    if c.pc==0x5b00:break
    c.step()
   else:raise AssertionError('Foreground did not resume')
   assert q.m.banks[2]==88 and q.get('CurrentBankC')==216
   assert expected==([q.get('VRAM_Buffer1',i)for i in range(84)],[q.get(n)for n in ['InvHudActive','InvHudPhysical','X5HudChrUpper','VvHudDirty','VRAM_Buffer1_Offset','VvTemp','VvTemp2']]),('resumed HUD queue differs',active,dirty,boundary)
   rows.append(dict(active=active,dirty=dirty,boundary=boundary,pc=pc,initial_actualC=actual,shadowC=shadow,permitted_adjacent_mapping_gap=actual!=(shadow&127),nmi_steps=nmi_steps,nmi_cycles=nmi_cycles,SP=sp))
 q=dict(passed=True,native_run=False,ROM_sha256=sha(a.rom),tool_sha256=sha(Path(__file__)),actual_compiled_NMI_cases=len(rows),fiveSMC_exact=True,foreground_AXYP_SP_exact_across_NMI=True,only_documented_shadow_hardware_gap=True,no_lag_DMA=True,rows=rows,limits='Synthetic CPU interrupt boundaries execute actual compiled lag NMI/audio and continuation, using cleared native audio state. No PPU scanline/IRQ timing, actual native controller, or full NMI budget claim.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in q.items()if k!='rows'},indent=2))
if __name__=='__main__':main()
