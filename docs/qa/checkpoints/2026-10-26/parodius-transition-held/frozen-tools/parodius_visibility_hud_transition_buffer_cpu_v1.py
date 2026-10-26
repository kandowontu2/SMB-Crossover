"""Compiled area producer, pending HUD, real Buffer2 NMI and Buffer1 catch-up."""
from pathlib import Path
import argparse,hashlib,json
from link_pit_rygar_sophia_audit_cpu import scoped_load,Arena
from check_nmi_vram_fast_cpu_v1 import Bus
from check_tmnt_render_oa import address
from verify_native_relocation import NesMPU

sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
SHA='5354161f339548f2e12b955f5fc1481b9956fe83a63263a04f4b2816edbbdf30'


def nmi_prefix(q):
 b=q.b;m=Bus(b)
 for i in range(0x8000):m.put(i,q.m[i])
 m.page(1,77);m.page(2,88);m.palette=[(i*17+3)&63 for i in range(32)]
 values=dict(CurrentBank=205,CurrentBankC=216,NmiDisable=0,Mirror_PPUCTRL=0xa0,Mirror_PPUMASK=30,Sprite0HitDetectFlag=1,ReloadCHRBank=1,X5WideChrActive=1,SsChrActive=0,HorizontalScroll=0)
 for n,v in values.items():m.put(address(b,n),v)
 for i,v in enumerate([0x80,0,0,0,0,0,0x81,0x81,0,0,0,0]):m.put(address(b,'X5ChrMode')+i,v);m.put(address(b,'CurrentCHRBank')+i,i*7&255)
 m.put(0x2002,0x80);m.writes=[];c=NesMPU(memory=m,pc=address(b,'NonMaskableInterrupt'));c.a,c.x,c.y,c.p,c.sp=0x55,3,7,0x34,0xfd
 prefix_cycles=None
 for _ in range(50000):
  if c.pc==address(b,'OAMandReadJoypad')and prefix_cycles is None:prefix_cycles=c.processorCycles
  if c.pc==address(b,'AudioUpdate'):break
  c.step()
 else:raise AssertionError(('prefix timeout',hex(c.pc),m.banks))
 q.m=m
 return dict(cycles_to_OAM_entry=prefix_cycles,cycles_to_Audio_entry_without_DMA_hardware_stall=c.processorCycles,ordered_PPUDATA=[v for at,v in m.writes if at==0x2007],actual_C=m.banks[2],shadow_C=m[address(b,'CurrentBankC')],SP_at_OAM=c.sp)


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);assert sha(a.rom)==SHA;b=scoped_load(a.rom);rows=[]
 try:
  for variant in [1,2,3]:
   for column in [0,15]:
    q=Arena(b,18);q.put(AreaPointer=0x25,WorldNumber=0,LevelNumber=0,AreaType=1,AreaParserTaskNum=0,CurrentColumnPos=column,ColumnSets=0,CurrentNTAddr_High=0x20,CurrentNTAddr_Low=0x80+2*column,VRAM_Buffer2_Offset=0,VRAM_Buffer_AddrCtrl=6)
    q.invoke('GetAreaDataAddrs');q.invoke('AreaParserTaskHandler');q.invoke('AreaParserTaskHandler');size=q.get('VRAM_Buffer2_Offset');assert size==29
    produced=[q.get('VRAM_Buffer2',i)for i in range(size+1)];assert produced[-1]==0 and produced[0]==0x20 and produced[2]==0x9a
    q.put(CrossoverBehaviorVersion=0,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,DisableScreenFlag=0,PnInitialized=0x50,VvVariant=variant,PnBombCapturePending=0,PnBombPaletteReady=1,SmFreezePalettePending=0,InvHudActive=0,InvHudPhysical=0,X5HudChrUpper=1,VvHudDirty=1,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=6)
    q.array('VRAM_Buffer1',[0]*84);q.invoke('PnHud');assert q.get('VRAM_Buffer1_Offset')==42 and q.get('X5HudChrUpper')==0x81+variant*4
    full=[q.get('VRAM_Buffer1',i)for i in range(43)];before={n:q.get(n)for n in ['InvHudActive','InvHudPhysical','X5HudChrUpper','VRAM_Buffer1_Offset']}
    held=nmi_prefix(q);assert held['ordered_PPUDATA']==produced[3:29] and len(held['ordered_PPUDATA'])==26
    assert all(q.get(n)==v for n,v in before.items())and[q.get('VRAM_Buffer1',i)for i in range(43)]==full
    assert q.get('VRAM_Buffer2_Offset')==q.get('VRAM_Buffer2')==q.get('VRAM_Buffer_AddrCtrl')==0 and q.get('InvHudActive')==0
    caught=nmi_prefix(q)
    assert q.get('InvHudActive')==variant*2+1 and q.get('InvHudPhysical')==139+variant and q.get('X5HudChrUpper')==1 and q.get('VRAM_Buffer1_Offset')==0
    assert caught['ordered_PPUDATA']==full[3:31]+full[34:42]
    assert held['actual_C']==caught['actual_C']==116 and held['shadow_C']==caught['shadow_C']==216
    rows.append(dict(variant=variant,column=column,actual_compiled_area_producer='AreaParserTaskHandler core then one genuine column render task',actual_Buffer2_PPUDATA_writes=26,produced_Buffer2_offset=size,produced_Buffer2_bytes=produced,pending_full42_exact_retained=True,first_NMI_Buffer2_cleared=True,first_NMI_HUD_inactive=True,mid_NMI_C116_owner_foreground_shadow88=True,next_NMI_Buffer1_font_tag_committed=True,second_NMI_ordered36_HUD_data_exact=True,hold_prefix=held,catchup_prefix=caught,limits='Isolated CPU source chronology intentionally combines valid producer/owner states. This does NOT establish natural controller overlap, physical DMA/PPU or DMC timing.'))
 except Exception as ex:
  (a.output/'failure.json').write_text(json.dumps(dict(passed=False,native_run=False,error=repr(ex),completed=rows),indent=2)+'\n');raise
 (a.output/'cases.json').write_text(json.dumps(rows,indent=2)+'\n');proof=dict(passed=True,native_run=False,ROM_sha256=SHA,cases=len(rows),cases_sha256=sha(a.output/'cases.json'),tool_sha256=sha(Path(__file__)),limits='Actual assembled area producer and two regular NMI paths through actual OAM CPU and resident InitBuffer, stopping at AudioUpdate entry. No external hooks skipped. Explicit source-level state combination, not controller-reachable Buffer2/HUD overlap or a native pass; actual capture and hold/catch-up coverage remain required.')
 (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2))


if __name__=='__main__':main()
