"""Exact f35 whole HUD callers and regular NMI prefix versus CV3 composition."""
from pathlib import Path
import argparse,hashlib,itertools,json
from parodius_visibility_hud_cancel_cpu_v2 import setup,execute,nmi_prefix
from link_pit_rygar_sophia_audit_cpu import scoped_load,Arena
from check_tmnt_render_oa import address
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--parent',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--expected-sha256',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);assert sha(a.parent)=='f35f0ec2f70d5dcb6eb1bbfcbd84359d9f6da68c39719d75217aed149edb0631'and sha(a.candidate)==a.expected_sha256;bs=[scoped_load(x)for x in[a.parent,a.candidate]];rows=[];apps=list(range(0x100))+list(range(0x200,0x800))+list(range(0x5c00,0x8000));case=None
 try:
  for name,mode,variant,kind in itertools.product(['VvReset','VvEnsure','PnHudNewLife'],[0,1],range(4),['clean','full','attr']):
   case=dict(path=name,mode=mode,variant=variant,pending=kind);values=[]
   for b in bs:
    q=setup(b,mode,variant,1+2*variant);q.put(VvHudDirty=0)
    if kind=='full':q.put(InvHudActive=0,InvHudPhysical=0,VvHudDirty=1);q.invoke('PnHud')
    elif kind=='attr'and variant:q.array('VRAM_Buffer1',[0x20,0x40,3,7,8,9,0]);q.put(VRAM_Buffer1_Offset=6,VvHudDirty=1);q.invoke('PnHud')
    if kind in['full','attr']and variant:
     size=q.get('VRAM_Buffer1_Offset');q.array('VRAM_Buffer1',[q.get('VRAM_Buffer1',i)for i in range(size)]+[0x20,0x60,1,11,0]);q.set('VRAM_Buffer1_Offset',size+4)
    if name=='VvEnsure':q.put(VvLife=255,NumberofLives=1)
    out=execute(q,name);values.append((q,out))
   (q,x),(r,y)=values;assert x['regs']==y['regs']and x['cycles']==y['cycles']and x['banks']==y['banks'];assert all(x['ram'][i]==y['ram'][i]for i in apps);assert x['writes']==y['writes'];rows.append(dict(case,full_public_regs_RAM_APU_mapper_and_cycles_exact=True))
  for mode,variant,column,cancel in itertools.product([0,1],[1,2,3],[0,15],[False,True]):
   case=dict(path='actual-area-producer-two-NMI-prefix',mode=mode,variant=variant,column=column,cancel=cancel);values=[]
   for b in bs:
    q=Arena(b,18);q.put(AreaPointer=0x25,WorldNumber=0,LevelNumber=0,AreaType=1,AreaParserTaskNum=0,CurrentColumnPos=column,ColumnSets=0,CurrentNTAddr_High=0x20,CurrentNTAddr_Low=0x80+2*column,VRAM_Buffer2_Offset=0,VRAM_Buffer_AddrCtrl=6);q.invoke('GetAreaDataAddrs');q.invoke('AreaParserTaskHandler');q.invoke('AreaParserTaskHandler');assert q.get('VRAM_Buffer2_Offset')==29
    q.put(CrossoverBehaviorVersion=mode,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,DisableScreenFlag=0,PnInitialized=0x50,VvVariant=variant,PnBombCapturePending=0,PnBombPaletteReady=1,SmFreezePalettePending=0,InvHudActive=0,InvHudPhysical=0,X5HudChrUpper=1,VvHudDirty=1,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=6);q.array('VRAM_Buffer1',[0]*84);q.invoke('PnHud');assert q.get('VRAM_Buffer1_Offset')==42
    if cancel:q.invoke('PnHudNewLife')
    first=nmi_prefix(q)
    if cancel:q.invoke('PnHud')
    second=nmi_prefix(q);assert q.get('InvHudActive')==2*variant+1 and second['HUD_font']==395+variant;values.append((first,second,bytes(q.m[i]for i in apps),q.m.banks[:]))
   assert values[0]==values[1];rows.append(dict(case,actual_area_Buffer2_and_foreign_queue_font_NMI_prefix_exact=True))
  for mode,variant in itertools.product([0,1],[1,2,3]):
   case=dict(path='committed-font-real-death-owner',mode=mode,variant=variant);values=[]
   for b in bs:
    q=setup(b,mode,variant);q.invoke('PnHud');before=nmi_prefix(q);assert before['HUD_font']==395+variant;out=execute(q,'VvDeathStart');assert q.get('InvHudActive')==2*variant+1 and q.get('X5HudChrUpper')&3==1;values.append((out['regs'],out['cycles'],out['banks'],bytes(q.m[i]for i in apps),out['writes']))
   assert values[0]==values[1];rows.append(dict(case,actual_death_font_lease_and_all_public_state_exact=True))
 except Exception as ex:
  (a.output/'failure.json').write_text(json.dumps(dict(passed=False,native_executed=False,error=repr(ex),case=case,completed=rows),indent=2)+'\n');raise
 (a.output/'cases.json').write_text(json.dumps(rows,indent=2)+'\n');result=dict(passed=True,native_executed=False,ROM_sha256=sha(a.candidate),parent_ROM_sha256=sha(a.parent),whole_lifecycle_callers=72,actual_Buffer2_double_NMI_prefix_controls=24,actual_committed_font_death_controls=6,total_cases=len(rows),all_AXYP_SP_RAM_APU_queue_font_cycles_and_mapping_exact=True,cases_sha256=sha(a.output/'cases.json'),tool_sha256=sha(__file__),scope='Exact current-f35 versus private combined source CPU. Real compiled lifecycle caller/area packet/death owner and modeled NMI prefix comparisons; setup is explicit source-component state, not controller-reachable pipe/death/native DMA/raster evidence. Does not relabel incomplete f35 sixth native aggregate as qualified.')
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
