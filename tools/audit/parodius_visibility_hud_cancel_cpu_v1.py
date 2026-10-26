"""Actual-CPU lifecycle/queue/font controls for private HUD cancellation repair."""
from pathlib import Path
import argparse,hashlib,itertools,json
from link_pit_rygar_sophia_audit_cpu import scoped_load,Arena
from check_tmnt_render_oa import address,location
from check_nmi_vram_fast_cpu_v1 import Bus
from verify_native_relocation import NesMPU
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def execute(q,name,flags=0x30,x=37,y=193):
 b=q.b;at=location(b,name);pc=address(b,name);w=(pc-0x8000)//8192;q.m.page(w,(at-16)//8192)
 if w in [1,2]:q.set('CurrentBank'if w==1 else'CurrentBankC',q.m.banks[w]|128)
 c=NesMPU(memory=q.m,pc=pc);c.a,c.x,c.y,c.p,c.sp=0,x,y,flags,0xfd;c.stPushWord(0x5aff);q.m.writes=[]
 for _ in range(100000):
  if c.pc==0x5b00:break
  c.step()
 else:raise AssertionError(('CPU timeout',name,c.pc,q.m.banks))
 assert c.sp==0xfd
 return dict(regs=[c.a,c.x,c.y,c.p,c.sp],cycles=c.processorCycles,banks=q.m.banks[:],ram=bytes(q.m[:0x8000]),writes=q.m.writes[:])


def setup(b,mode=0,variant=1,active=0):
 q=Arena(b,18);q.put(VvVariant=variant,CrossoverBehaviorVersion=mode,VvInitialized=0x76,VvLife=2,VvAlive=1,NumberofLives=2,
                    PnInitialized=0x50,PnType=1,PnActive=128,PnDrawFlags=1,PnSkin=variant,PnX=104,PnY=136,
                    VvObjX=104,VvObjY=136,VvNeedEntry=0,PnBombPaletteReady=1,PnBombCapturePending=0,
                    OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,DisableScreenFlag=0,NmiDisable=255,
                    InvHudActive=active,InvHudPhysical=139+variant,X5HudChrUpper=1,VvHudDirty=1)
 return q


def nmi_prefix(q):
 b=q.b;m=Bus(b)
 for i in range(0x8000):m.put(i,q.m[i])
 m.page(1,77);m.page(2,88);m.palette=[(i*17+3)&63 for i in range(32)]
 for n,v in dict(CurrentBank=205,CurrentBankC=216,NmiDisable=0,Mirror_PPUCTRL=0xa8,Mirror_PPUMASK=30,Sprite0HitDetectFlag=1,ReloadCHRBank=1,X5WideChrActive=1,SsChrActive=0,HorizontalScroll=0).items():m.put(address(b,n),v)
 for i in range(12):m.put(address(b,'X5ChrMode')+i,0);m.put(address(b,'CurrentCHRBank')+i,0)
 m.put(0x2002,0x80);m.writes=[];c=NesMPU(memory=m,pc=address(b,'NonMaskableInterrupt'));c.a,c.x,c.y,c.p,c.sp=0x55,3,7,0x34,0xfd
 before=None
 for _ in range(50000):
  if c.pc==address(b,'OAMandReadJoypad')and before is None:before=c.processorCycles
  if c.pc==address(b,'AudioUpdate'):break
  c.step()
 else:raise AssertionError(('NMI timeout',c.pc))
 q.m=m;upper=0;font=None;hi=None;dest=0;ctrl=0;data=[]
 for at,v in m.writes:
  if at==0x5130:upper=v&3
  elif at==0x5128:font=v+256*upper
  elif at==0x2000:ctrl=v
  elif at==0x2006:
   if hi is None:hi=v
   else:dest=(hi*256+v)&0x3fff;hi=None
  elif at==0x2007:data.append([dest,v]);dest=(dest+(32 if ctrl&4 else 1))&0x3fff
 return dict(cycles_to_OAM=before,cycles_to_Audio_without_hardware_DMA=c.processorCycles,HUD_font=font,PPUDATA=data,SP=c.sp,banks=m.banks[:])


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['baseline','candidate','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);bs=[scoped_load(a.baseline),scoped_load(a.candidate)]
 assert sha(a.baseline)=='5354161f339548f2e12b955f5fc1481b9956fe83a63263a04f4b2816edbbdf30'
 assert sha(a.candidate)=='f35f0ec2f70d5dcb6eb1bbfcbd84359d9f6da68c39719d75217aed149edb0631'
 rows=[];case=None;apps=list(range(0x100))+list(range(0x200,0x800))+list(range(0x5c00,0x8000))
 def exact(f,g,allowed=()):
  assert f['regs']==g['regs']and f['banks']==g['banks'],('Public AXYP/SP/banks',case,f['regs'],g['regs'],f['banks'],g['banks'])
  assert all(f['ram'][i]==g['ram'][i]for i in apps if i not in allowed),('Application RAM/OAM',case,[(i,f['ram'][i],g['ram'][i])for i in apps if i not in allowed and f['ram'][i]!=g['ram'][i]][:20])
 try:
  # All actual callers supply A0. Nonexistent public inputs are not invented.
  for variant,bank,bits in itertools.product(range(4),[76,88,116,117],range(64)):
   flags=0x30|(bits&3)|((bits&4)<<0)|((bits&8)<<0)|((bits&16)<<2)|((bits&32)<<2);case=dict(kind='nonpending-helper',variant=variant,bank=bank,flags=flags);got=[]
   for b in bs:
    q=setup(b,variant=variant,active=1+2*variant);q.m.page(2,bank);q.set('CurrentBankC',bank|128);got.append(execute(q,'PnHudCancelLife',flags))
   exact(*got);rows.append(dict(case,public_and_all_application_state_exact=True,cycle_delta=got[1]['cycles']-got[0]['cycles']))
  tailshapes=[[],[0x20,0x64,3,7,8,9],[0x3f,0x10,4,15,48,21,8],[0x20,0x64,1,9,0x20,0x65,2,10,11]]
  for variant,mode,tail in itertools.product([1,2,3],[0,1],tailshapes):
   case=dict(kind='full-pending-cancel',variant=variant,mode=mode,tail=tail);q=setup(bs[1],mode,variant);q.invoke('PnHud');assert q.get('VRAM_Buffer1_Offset')==42
   full=[q.get('VRAM_Buffer1',i)for i in range(42)];q.array('VRAM_Buffer1',full+tail+[0]);q.set('VRAM_Buffer1_Offset',42+len(tail));q.array('VRAM_Buffer2',[0x20,0x80,0x9a]+[i&255 for i in range(26)]+[0]);buffer2=bytes(q.m[address(q.b,'VRAM_Buffer2'):address(q.b,'VRAM_Buffer2')+30])
   out=execute(q,'PnHudNewLife');assert q.get('VRAM_Buffer1_Offset')==len(tail)and[q.get('VRAM_Buffer1',i)for i in range(len(tail)+1)]==tail+[0]
   assert q.get('InvHudActive')==0 and q.get('X5HudChrUpper')==1 and q.get('VvHudDirty')==1 and buffer2==bytes(q.m[address(q.b,'VRAM_Buffer2'):address(q.b,'VRAM_Buffer2')+30])
   rows.append(dict(case,only_owned42B_removed=True,native_tail_and_terminator_exact=True,Buffer2_exact=True,cycles=out['cycles']))
  for prefix_len,tail in itertools.product([0]+list(range(4,32)),tailshapes):
   case=dict(kind='attr-pending-cancel',prefix=prefix_len,tail=tail);q=setup(bs[1],active=3)
   prefix=[]if prefix_len==0 else[0x20,0x40,prefix_len-3]+list(range(prefix_len-3));attr=[0x23,0xc0,8]+[170]*8
   q.array('VRAM_Buffer1',prefix+attr+tail+[0]);q.put(VRAM_Buffer1_Offset=len(prefix)+11+len(tail),X5HudChrUpper=0x81+prefix_len*4)
   out=execute(q,'PnHudNewLife');assert q.get('VRAM_Buffer1_Offset')==len(prefix)+len(tail)and[q.get('VRAM_Buffer1',i)for i in range(len(prefix)+len(tail)+1)]==prefix+tail+[0]
   assert q.get('InvHudActive')==0 and q.get('X5HudChrUpper')==1
   rows.append(dict(case,only_owned11B_removed=True,native_prefix_tail_and_terminator_exact=True,cycles=out['cycles']))
  for variant,mode,kind in itertools.product(range(4),[0,1],['clean','attr','full']):
   case=dict(kind='complete-death-caller',variant=variant,mode=mode,pending=kind);got=[]
   for b in bs:
    q=setup(b,mode,variant,1+2*variant)
    if kind=='full':
     q.put(InvHudActive=0,InvHudPhysical=0);q.invoke('PnHud')
    elif kind=='attr'and variant:
     q.invoke('PnHud')
    f=execute(q,'VvDeathStart');got.append((q,f))
   (q,f),(r,g)=got;allowed={address(bs[0],n)for n in ['InvHudActive','X5HudChrUpper','VvHudDirty','VRAM_Buffer1_Offset']};allowed.update(range(address(bs[0],'VRAM_Buffer1'),address(bs[0],'VRAM_Buffer1')+84));exact(f,g,allowed)
   if variant and kind!='full':assert r.get('InvHudActive')==1+2*variant
   else:assert r.get('InvHudActive')==0
   if kind=='full'and variant:assert r.get('VRAM_Buffer1_Offset')==0
   old_nmi=nmi_prefix(q);new_nmi=nmi_prefix(r)
   if variant and kind!='full':assert old_nmi['HUD_font']==0 and new_nmi['HUD_font']==395+variant
   if variant and kind=='full':assert not any(0x2022<=at<=0x203d for at,v in new_nmi['PPUDATA'])
   rows.append(dict(case,full_public_AXYP_banks_exact=True,only_intended_HUD_queue_state_deltas=True,baseline_NMI=old_nmi,candidate_NMI=new_nmi))
  # Reproduce actual UI-before-new-life order from811, then the real capture NMI.
  for variant,mode in itertools.product([1,2,3],[0,1]):
   case=dict(kind='actual-order-UI-Ensure-draw-capture',variant=variant,mode=mode);got=[]
   for b in bs:
    q=setup(b,mode,variant);q.put(VvLife=255,NumberofLives=1,ScreenLeft_PageLoc=0,ScreenLeft_X_Pos=0,Player_PageLoc=0,Player_X_Position=40,Player_Y_Position=176,SavedJoypadBits=128)
    q.invoke('PnHud');assert q.get('VRAM_Buffer1_Offset')==42
    q.invoke('VvMovement');q.invoke('VvDraw');assert q.get('PnBombPaletteReady')==0 and q.get('PnBombCapturePending')==1
    before=dict(offset=q.get('VRAM_Buffer1_Offset'),upper=q.get('X5HudChrUpper'),active=q.get('InvHudActive'))
    n=nmi_prefix(q);got.append((q,before,n))
   (q,f,n),(r,g,k)=got;assert f['offset']==42 and g['offset']==0
   assert any(at==0x2022 for at,v in n['PPUDATA'])and not any(0x2022<=at<=0x203d for at,v in k['PPUDATA'])
   assert r.get('PnBombPaletteReady')==1 and r.get('InvHudActive')==0
   r.invoke('PnHud');assert r.get('VRAM_Buffer1_Offset')==42 and r.get('X5HudChrUpper')==0x81+variant*4
   caught=nmi_prefix(r);assert r.get('InvHudActive')==variant*2+1 and caught['HUD_font']==395+variant
   rows.append(dict(case,stale_full_removed_before_capture=True,original_capture_order_preserved=True,first_prelease_no_custom_label_write=True,following_fresh_full_commit=True,baseline=n,candidate=k,caught=caught))
 except Exception as ex:
  (a.output/'failure.json').write_text(json.dumps(dict(passed=False,native_run=False,error=repr(ex),case=case,completed=rows),indent=2)+'\n');raise
 (a.output/'cases.json').write_text(json.dumps(rows,indent=2)+'\n')
 q=dict(passed=True,native_run=False,baseline_ROM_sha256=sha(a.baseline),ROM_sha256=sha(a.candidate),cases=len(rows),tool_sha256=sha(Path(__file__)),cases_sha256=sha(a.output/'cases.json'),
        limits='Isolated actual CPU/explicit real producer/caller states, modeled ordered PPU writes and regular NMI through OAM CPU/InitBuffer stopping at AudioUpdate entry. No hardware DMA stalls/physical PPU/IRQ injection/native replay or all-build verdict. Interrupt controls are a separate required gate; no native grant/adoption.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
