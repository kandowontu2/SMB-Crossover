"""Whole reset/new-life callers, genuine area Buffer2 and HUD catch-up controls."""
from pathlib import Path
import argparse,hashlib,itertools,json
from parodius_visibility_hud_cancel_cpu_v2 import setup,execute,nmi_prefix
from link_pit_rygar_sophia_audit_cpu import scoped_load,Arena
from check_tmnt_render_oa import address
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['baseline','candidate','output','builds']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);bs=[scoped_load(a.baseline),scoped_load(a.candidate)]
 assert sha(a.candidate)=='f35f0ec2f70d5dcb6eb1bbfcbd84359d9f6da68c39719d75217aed149edb0631'
 apps=list(range(0x100))+list(range(0x200,0x800))+list(range(0x5c00,0x8000));rows=[];case=None
 try:
  for name,mode,variant,kind in itertools.product(['VvReset','VvEnsure','PnHudNewLife'],[0,1],range(4),['clean','full','attr']):
   case=dict(kind='whole-cancel-caller',name=name,mode=mode,variant=variant,pending=kind);got=[]
   for b in bs:
    q=setup(b,mode,variant,1+2*variant);q.put(VvHudDirty=0)
    if kind=='full':q.put(InvHudActive=0,InvHudPhysical=0,VvHudDirty=1);q.invoke('PnHud')
    elif kind=='attr'and variant:
     q.array('VRAM_Buffer1',[0x20,0x40,3,7,8,9,0]);q.put(VRAM_Buffer1_Offset=6,VvHudDirty=1);q.invoke('PnHud')
    if kind in ['full','attr']and variant:
     size=q.get('VRAM_Buffer1_Offset');q.array('VRAM_Buffer1',[q.get('VRAM_Buffer1',i)for i in range(size)]+[0x20,0x60,1,11,0]);q.set('VRAM_Buffer1_Offset',size+4)
    before=[q.get('VRAM_Buffer1',i)for i in range(q.get('VRAM_Buffer1_Offset')+1)]
    if name=='VvEnsure':q.put(VvLife=255,NumberofLives=1)
    f=execute(q,name);got.append((q,f,before))
   (q,f,old),(r,g,prior)=got;assert f['regs']==g['regs']and f['banks']==g['banks'],('Whole caller public ABI',case,f['regs'],g['regs'])
   allowed=set(range(address(bs[0],'VRAM_Buffer1'),address(bs[0],'VRAM_Buffer1')+84))|{address(bs[0],'VRAM_Buffer1_Offset'),address(bs[0],'VvHudDirty')}
   assert all(f['ram'][i]==g['ram'][i]for i in apps if i not in allowed),('Nonstack nonqueue application RAM/OAM',case,[(i,f['ram'][i],g['ram'][i])for i in apps if i not in allowed and f['ram'][i]!=g['ram'][i]][:8])
   expected=prior[:]
   if variant and kind=='full':expected=prior[42:]
   elif variant and kind=='attr':expected=prior[:6]+prior[17:]
   actual=[r.get('VRAM_Buffer1',i)for i in range(r.get('VRAM_Buffer1_Offset')+1)]
   assert actual==expected,('Only owned queue segment removed',case,actual,expected)
   assert r.get('InvHudActive')==0 and r.get('X5HudChrUpper')&128==0
   rows.append(dict(case,full_AXYP_SP_banks_exact=True,all_nonstack_nonqueue_RAM_OAM_exact=True,native_queue_prefix_tail_terminator_exact=True,cycle_delta=g['cycles']-f['cycles']))
  for variant,column,cancel in itertools.product([1,2,3],[0,15],[False,True]):
   case=dict(kind='genuine-area-Buffer2-and-catchup',variant=variant,column=column,cancel=cancel)
   q=Arena(bs[1],18);q.put(AreaPointer=0x25,WorldNumber=0,LevelNumber=0,AreaType=1,AreaParserTaskNum=0,CurrentColumnPos=column,ColumnSets=0,CurrentNTAddr_High=0x20,CurrentNTAddr_Low=0x80+2*column,VRAM_Buffer2_Offset=0,VRAM_Buffer_AddrCtrl=6)
   q.invoke('GetAreaDataAddrs');q.invoke('AreaParserTaskHandler');q.invoke('AreaParserTaskHandler');assert q.get('VRAM_Buffer2_Offset')==29
   produced=[q.get('VRAM_Buffer2',i)for i in range(30)];assert produced[0]==32 and produced[2]==0x9a and produced[-1]==0
   q.put(CrossoverBehaviorVersion=0,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,DisableScreenFlag=0,PnInitialized=0x50,VvVariant=variant,PnBombCapturePending=0,PnBombPaletteReady=1,SmFreezePalettePending=0,InvHudActive=0,InvHudPhysical=0,X5HudChrUpper=1,VvHudDirty=1,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=6)
   q.array('VRAM_Buffer1',[0]*84);q.invoke('PnHud');assert q.get('VRAM_Buffer1_Offset')==42;full=[q.get('VRAM_Buffer1',i)for i in range(43)]
   if cancel:q.invoke('PnHudNewLife');assert q.get('VRAM_Buffer1_Offset')==0 and q.get('X5HudChrUpper')==1
   before={n:q.get(n)for n in ['InvHudActive','InvHudPhysical','X5HudChrUpper','VRAM_Buffer1_Offset']};held=nmi_prefix(q)
   assert [v for at,v in held['PPUDATA']]==produced[3:29]
   assert all(q.get(n)==v for n,v in before.items())and q.get('VRAM_Buffer2_Offset')==0 and q.get('VRAM_Buffer_AddrCtrl')==0
   if not cancel:assert[q.get('VRAM_Buffer1',i)for i in range(43)]==full
   else:q.invoke('PnHud');assert q.get('VRAM_Buffer1_Offset')==42
   caught=nmi_prefix(q);assert q.get('InvHudActive')==2*variant+1 and q.get('InvHudPhysical')==139+variant and caught['HUD_font']==395+variant
   assert[v for at,v in caught['PPUDATA']]==full[3:31]+full[34:42]
   rows.append(dict(case,actual_compiled_area_29B_producer=True,original_26ordered_Buffer2_data_exact=True,
                    no_cancel_holds_full_exact=not cancel,cancel_removes_only_owned_full=cancel,next_fresh_full_commit_exact=True,
                    first_NMI=held,second_NMI=caught,limits='Explicit isolated producer combination, not natural pipe/controller overlap.'))
  builds={}
  for mapper in ['mmc3','mmc5']:
   f=a.builds/('parent-'+mapper+'.nes');g=a.builds/('candidate-'+mapper+'.nes');assert f.read_bytes()==g.read_bytes();builds[mapper]=dict(parent_sha256=sha(f),candidate_sha256=sha(g),bytes=f.stat().st_size,flag_off_ROM_exact=True)
 except Exception as ex:
  (a.output/'failure.json').write_text(json.dumps(dict(passed=False,native_run=False,error=repr(ex),case=case,completed=rows),indent=2)+'\n');raise
 (a.output/'cases.json').write_text(json.dumps(rows,indent=2)+'\n');q=dict(passed=True,native_run=False,ROM_sha256=sha(a.candidate),baseline_ROM_sha256=sha(a.baseline),
          cases=len(rows),whole_caller_controls=72,actual_Buffer2_controls=12,ordinary_flag_off_builds=builds,
          tool_sha256=sha(Path(__file__)),cases_sha256=sha(a.output/'cases.json'),
          limits='Actual compiled reset/new-life caller continuations, real area packet producer and two modeled regular NMI prefixes through OAM CPU/InitBuffer. Isolated state combinations, no controller-reachable Buffer2 overlap/hardware DMA/raster/native difficulty or adoption claim. Full IRQ/NMI interference is a separate receipt.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
