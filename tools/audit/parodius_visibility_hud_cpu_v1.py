"""Actual linked CPU HUD pending/commit/cancel chronology; source-only."""
from pathlib import Path
import argparse,hashlib,itertools,json,shutil
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address
from check_nmi_vram_fast_cpu_v1 import Bus,run
from parodius_visibility_hud_design_v1 import apply,packet_without_labels
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);shutil.copy2(Path(__file__),a.output/Path(__file__).name)
 b=scoped_load(a.candidate);old=scoped_load(a.base/'baseline-rebuild-v2/candidate.nes');rows=[];counts={};selective='PnHudBufferClear'not in b['syms'];resume=13 if selective else 6
 def case(kind,**v):counts[kind]=counts.get(kind,0)+1;rows.append(dict(kind=kind,**v))
 def arena(**v):
  q=Arena(b,18);q.put(DisableScreenFlag=0,VvVariant=1,VvMeter=0,VvHudDirty=1,InvHudActive=0,X5HudChrUpper=1,VRAM_Buffer1_Offset=0,ReloadCHRBank=0,PnInitialized=0x50,PnBombPaletteReady=1,PnBombCapturePending=0,VRAM_Buffer_AddrCtrl=0);q.array('VRAM_Buffer1',[0]*84);q.put(**v);return q
 def getpacket(q):return [q.get('VRAM_Buffer1',i)for i in range(q.get('VRAM_Buffer1_Offset')+1)]
 def commit(q):
  q.m.page(2,116);q.set('NmiR0',(address(b,'VRAM_Buffer1')+q.get('VRAM_Buffer1_Offset'))&255);q.set('NmiR1',(address(b,'VRAM_Buffer1')+q.get('VRAM_Buffer1_Offset'))>>8)
  return run(b,q.m,address(b,'PnHudCommitAfterVram'),address(b,'PnPaletteScreenUpdate')+resume,0xa5,0x37,0x92,0x75)
 def gateway(q):
  pointer=address(b,'VRAM_Buffer2'if q.get('VRAM_Buffer_AddrCtrl')==6 else 'VRAM_Buffer1')
  q.m.page(2,88);q.set('CurrentBankC',216);q.set('NmiR0',pointer&255);q.set('NmiR1',pointer>>8);q.m[0x1fe]=0xff;q.m[0x1ff]=1
  return run(b,q.m,address(b,'SamusFreezeUpdateScreen'),0x0200,0xa5,0x37,0x92,0x75)
 def clear_after_commit(q,ctrl):
  if not selective:q.invoke('PnHudBufferClear',a=0,x=address(b,'VRAM_Buffer2_Offset')-address(b,'VRAM_Buffer1_Offset')if ctrl==6 else 0)
  else:run(b,q.m,address(b,'InitBuffer'),address(b,'InitBuffer')+14,0xa5,37,int(ctrl==6),0x75)
 # Real original full-label payloads are the oracle for all meter values.
 oracle={}
 for variant,meter in itertools.product([1,2,3],range(256)):
  q=Arena(old,18);q.put(DisableScreenFlag=0,VvVariant=variant,VvMeter=meter,VvHudDirty=1,InvHudActive=1,VRAM_Buffer1_Offset=0);q.array('VRAM_Buffer1',[0]*84);q.invoke('PnHud');oracle[variant,meter]=getpacket(q)
 for variant,meter,offset in itertools.product([1,2,3],range(256),[0,1,39,40,72,83]):
  q=arena(VvVariant=variant,VvMeter=meter,VRAM_Buffer1_Offset=offset);q.array('VRAM_Buffer1',[0x24]*84);q.set('VRAM_Buffer1',0,offset);before=bytes(q.m);cpu,_=q.invoke('PnHud')
  assert q.get('InvHudActive')==0 and q.m.banks[2]==88 and q.get('CurrentBankC')==216
  if offset==0:
   expected=oracle[variant,meter];assert getpacket(q)[offset:]==expected
   assert q.get('VRAM_Buffer1_Offset')==offset+42 and q.get('InvHudPhysical')==offset and q.get('X5HudChrUpper')==0x81+variant*4 and q.get('VvHudDirty')==0
   # Catch-up UI before a normal NMI must not queue duplicate labels or lease font.
   pending=getpacket(q);q.set('VvHudDirty',1);q.invoke('PnHud');assert getpacket(q)==pending and q.get('VvHudDirty')==1 and q.get('InvHudActive')==0
   result=commit(q);assert q.get('InvHudActive')==variant*2+1 and q.get('InvHudPhysical')==139+variant and q.get('X5HudChrUpper')==1 and q.get('ReloadCHRBank')==1 and q.get('VvHudDirty')==1
   assert result['state'][0:3]==(1 if selective else 18,0x37,0x92)and result['state'][4]==0xfd
  else:assert q.get('VRAM_Buffer1_Offset')==offset and q.get('VvHudDirty')==1 and q.get('ReloadCHRBank')==0
  case('full_admission_catchup_commit',variant=variant,meter=meter,offset=offset,foreground_cycles=cpu.processorCycles)
 # Cached labels permit only attribute appends; exact whole PPU image under
 # a valid label premise and native table data, including both boundary edges.
 for variant,meter,offset in itertools.product([1,2,3],range(256),[0,1,20,31,32,72,73,83]):
  q=arena(VvVariant=variant,VvMeter=meter,InvHudActive=variant*2+1,VRAM_Buffer1_Offset=offset);q.array('VRAM_Buffer1',[0x24]*84);q.set('VRAM_Buffer1',0,offset);cpu,_=q.invoke('PnHud')
  assert q.get('InvHudActive')==variant*2+1 and q.get('InvHudPhysical')==139+variant
  if offset<32:
   assert q.get('X5HudChrUpper')==0x81+4*offset
   assert getpacket(q)[offset:]==packet_without_labels(oracle[variant,meter])and q.get('VvHudDirty')==0
   prior=bytearray((i*71+29)&255 for i in range(16384));prior[0x2022:0x203e]=bytes(oracle[variant,meter][3:31]);v1=prior.copy();v2=prior.copy();apply(oracle[variant,meter],v1);apply(getpacket(q)[offset:],v2);assert v1==v2
  else:assert q.get('VRAM_Buffer1_Offset')==offset and q.get('VvHudDirty')==1 and q.get('X5HudChrUpper')==1
  case('cached_attributes',variant=variant,meter=meter,offset=offset,foreground_cycles=cpu.processorCycles)
 # Explicit pre-Ensure/first capture guard, not merely capturePending==0.
 for variant,init,ready,capture,dirty in itertools.product([1,2,3],[0,0x50],[0,1],[0,1],[0,1]):
  if init==0x50 and ready==1:continue
  q=arena(VvVariant=variant,PnInitialized=init,PnBombPaletteReady=ready,PnBombCapturePending=capture,VvHudDirty=dirty);q.invoke('PnHud');assert q.get('VRAM_Buffer1_Offset')==0 and q.get('InvHudActive')==0 and q.get('VvHudDirty')==1
  case('cold_preensure_defer',variant=variant,init=init,ready=ready,capture=capture,dirty=dirty)
 # Header, extent, consumed pointer, mode/owner, variant and reset rejection.
 mutations=[('SelectedCharacter',0),('SelectedCharacter',17),('OperMode',0),('GameEngineSubroutine',6),('DisableScreenFlag',1),('PnInitialized',0),('PnBombPaletteReady',0),('VvVariant',0),('VvVariant',4),('InvHudPhysical',40),('VRAM_Buffer1_Offset',41),('VRAM_Buffer1_Offset',84),('VRAM_Buffer_AddrCtrl',1),('VRAM_Buffer_AddrCtrl',5),('VRAM_Buffer_AddrCtrl',7)]
 for variant,offset in itertools.product([1,2,3],[0]):
  for name,value in mutations+[(f'header{i}',i)for i in range(6)]+[('pointerlow',0),('pointerhigh',0),('variantflip',0)]:
   q=arena(VvVariant=variant,VRAM_Buffer1_Offset=offset);q.invoke('PnHud');extent=q.get('VRAM_Buffer1_Offset');ptr=address(b,'VRAM_Buffer1')+extent;q.set('NmiR0',ptr&255);q.set('NmiR1',ptr>>8)
   if name.startswith('header'):
    at=[0,1,2,31,32,33][value];q.set('VRAM_Buffer1',q.get('VRAM_Buffer1',offset+at)^1,offset+at)
   elif name=='pointerlow':q.set('NmiR0',(ptr+1)&255)
   elif name=='pointerhigh':q.set('NmiR1',(ptr>>8)^1)
   elif name=='variantflip':q.set('VvVariant',variant%3+1)
   else:q.set(name,value)
   q.m.page(2,116);r=run(b,q.m,address(b,'PnHudCommitAfterVram'),address(b,'PnPaletteScreenUpdate')+resume,0xa5,0x37,0x92,0x75)
   assert q.get('InvHudActive')==0 and q.get('X5HudChrUpper')&128==0 and q.get('VvHudDirty')==1 and q.get('ReloadCHRBank')==0,(variant,offset,name,value)
   assert r['state'][1:3]==(0x37,0x92)and r['state'][4]==0xfd
   case('commit_reject',variant=variant,offset=offset,mutation=name,value=value,cycles=r['cycles'])
 # Buffer2 deferral preserves pending even after a UI catchup; actual Buffer1
 # discard cancels even when a fixed/ROM control was selected.
 for variant,offset,ctrl in itertools.product([1,2,3],[0],range(8)):
  q=arena(VvVariant=variant,VRAM_Buffer1_Offset=offset);q.invoke('PnHud');q.set('VRAM_Buffer_AddrCtrl',ctrl);r=commit(q)
  if ctrl==6:
   assert q.get('X5HudChrUpper')&128 and q.get('InvHudActive')==0
   q.m.page(2,116);clear_after_commit(q,ctrl);assert q.get('X5HudChrUpper')&128
   q.invoke('PnHud');assert q.get('VRAM_Buffer1_Offset')==offset+42
   q.set('VRAM_Buffer_AddrCtrl',0);commit(q);assert q.get('InvHudActive')==variant*2+1
  elif ctrl==0:
   clear_after_commit(q,ctrl);assert q.get('InvHudActive')==variant*2+1 and q.get('VRAM_Buffer1_Offset')==0
  else:
   clear_after_commit(q,ctrl);assert q.get('InvHudActive')==0 and q.get('VvHudDirty')==1 and q.get('VRAM_Buffer1_Offset')==0
  case('flush_ctrl_chronology',variant=variant,offset=offset,ctrl=ctrl,cycles=r['cycles'])
 # Attribute markers retain the already-published font and carry offset0..31.
 # Exercise actual gateway, original clear, Buffer2 retention and catch-up.
 for variant,offset,ctrl,dirty in itertools.product([1,2,3],[0,4,20,31],range(8),[0,1]):
  q=arena(VvVariant=variant,InvHudActive=2*variant+1,VRAM_Buffer1_Offset=offset)
  if offset:q.array('VRAM_Buffer1',[0x21,0x10,offset-3]+[0x55]*(offset-3)+[0])
  q.array('VRAM_Buffer2',[0]);q.set('VRAM_Buffer2_Offset',0);q.invoke('PnHud');packet=getpacket(q);upper=q.get('X5HudChrUpper');assert upper==0x81+4*offset
  q.set('VvHudDirty',dirty);q.invoke('PnHud');assert getpacket(q)==packet and q.get('VvHudDirty')==dirty
  q.set('VRAM_Buffer_AddrCtrl',ctrl);r=gateway(q);assert q.get('InvHudActive')==2*variant+1
  if ctrl==6:
   assert q.get('X5HudChrUpper')==upper and q.get('VvHudDirty')==dirty
   q.m.page(2,116);clear_after_commit(q,ctrl);assert getpacket(q)==packet
   q.invoke('PnHud');assert getpacket(q)==packet
   q.set('VRAM_Buffer_AddrCtrl',0);gateway(q);assert q.get('X5HudChrUpper')==1 and q.get('VvHudDirty')==(dirty if offset+11<=31 else 1)
  else:
   assert q.get('X5HudChrUpper')==1 and q.get('VvHudDirty')==(dirty if ctrl==0 and offset+11<=31 else 1)
   q.m.page(2,116);clear_after_commit(q,ctrl);assert q.get('VRAM_Buffer1_Offset')==0
  case('attribute_ctrl_clear_catchup_chronology',variant=variant,offset=offset,ctrl=ctrl,later_dirty=dirty,cycles=r['cycles'])
 if not selective:
  for pending,x in itertools.product([0,1],[0,address(b,'VRAM_Buffer2_Offset')-address(b,'VRAM_Buffer1_Offset')]):
   q=arena(X5HudChrUpper=0x85 if pending else 1,InvHudActive=0,VvHudDirty=0);q.set('VRAM_Buffer1_Offset',42);q.invoke('PnHudBufferClear',a=0,x=x)
   assert q.get('X5HudChrUpper')==(1 if x==0 else(0x85 if pending else 1))and q.get('VvHudDirty')==int(pending and x==0)
   case('actual_discard_owner',pending=pending,x=x)
 # Inventory/newlife hooks preserve the native entry inputs and cancel leases.
 for routine,active,upper in itertools.product(['PnHudCancelLife','PnHudNewLife','SamusFreezeInit','InventoryInit','VvReset','VvDeathStart','VvEnsure'],[0,3],[0x85,0xfd]):
  q=arena(X5HudChrUpper=upper,InvHudActive=active,VvInitialized=0,NumberofLives=2,VvLife=3);q.invoke(routine,a=0,x=17,y=193);assert q.get('X5HudChrUpper')==1
  case('reset_owner',routine=routine,initial_active=active,initial_upper=upper)
 for mode,routine in itertools.product([0,1],['CrossoverInit','KbFreshGameInit']):
  q=arena(CrossoverBehaviorVersion=mode);q.invoke('PnHud');q.invoke(routine);assert q.get('X5HudChrUpper')&128==0 and q.get('InvHudActive')==0
  case('whole_global_and_fresh_init',mode=mode,routine=routine)
 for variant,producer in itertools.product([1,2,3],['ColorRotation','PnQueueBombPalette']):
  q=arena(VvVariant=variant,FrameCounter=0,ColorRotateOffset=0,AreaType=1);q.invoke('PnHud');labels=[q.get('VRAM_Buffer1',i)for i in range(42)];q.invoke(producer);assert [q.get('VRAM_Buffer1',i)for i in range(42)]==labels and q.get('X5HudChrUpper')&128
  extent=q.get('VRAM_Buffer1_Offset');gateway(q);assert q.get('InvHudActive')==0 and q.get('X5HudChrUpper')==1 and q.get('VvHudDirty')==1
  assert [q.get('VRAM_Buffer1',i)for i in range(42)]==labels
  case('actual_later_append_defers_first_full_preserves_payload',variant=variant,producer=producer,extent=extent)
 # Numeric difficulty readback controls share exactly the same owner: HUD
 # code has no difficulty branch, but fixture mode remains an explicit byte.
 for mode,variant in itertools.product([0,1],[1,2,3]):
  q=arena(CrossoverBehaviorVersion=mode,VvVariant=variant);q.invoke('PnHud');assert q.get('CrossoverBehaviorVersion')==mode and q.get('InvHudActive')==0;commit(q);assert q.get('InvHudActive')==2*variant+1
  case('numeric_difficulty_control',mode=mode,variant=variant)
 # The active warp-zone text owner overwrites Buffer1 instead of appending.
 # Its entry hook must cancel before replaying the original native ABI.
 for value,flags,pending in itertools.product(range(256),[0x30,0x31,0x74,0x7d,0xff],[0,1]):
  results=[]
  for bundle in [old,b]:
   m=Bus(bundle);m.page(1,3);m.put(address(bundle,'X5HudChrUpper'),0x85 if pending else 1);m.put(address(bundle,'VvHudDirty'),0);r=run(bundle,m,address(bundle,'WriteGameText'),address(bundle,'WriteGameText')+3,value,37,193,flags);results.append((r,m))
  assert results[0][0]['state']==results[1][0]['state']and results[0][0]['banks']==results[1][0]['banks']
  assert results[1][1][address(b,'X5HudChrUpper')]==1 and results[1][1][address(b,'VvHudDirty')]==pending
  case('text_overwrite_entry_ABI',A=value,flags=flags,pending=pending)
 for variant,offset,message in itertools.product([1,2,3],[0],range(8)):
  q=arena(VvVariant=variant,VRAM_Buffer1_Offset=offset);q.invoke('PnHud');q.invoke('WriteGameText',a=message);assert q.get('X5HudChrUpper')==1 and q.get('VvHudDirty')==1 and q.get('InvHudActive')==0
  commit(q);assert q.get('InvHudActive')==0
  case('whole_text_overwrite_cancels_pending',variant=variant,offset=offset,message=message)
 for variant,offset,message in itertools.product([1,2,3],[0,4,20,31],range(8)):
  q=arena(VvVariant=variant,InvHudActive=2*variant+1,VRAM_Buffer1_Offset=offset);q.invoke('PnHud');q.invoke('WriteGameText',a=message);assert q.get('X5HudChrUpper')==1 and q.get('VvHudDirty')==1 and q.get('InvHudActive')==2*variant+1
  case('whole_text_overwrite_cancels_attribute_marker_keeps_font',variant=variant,offset=offset,message=message)
 # Vic Viper variant0 keeps its original behavior, including its older
 # pre-admission Active protocol. It is an unchanged control, not repaired.
 for meter,offset in itertools.product(range(256),[0,1,47,48,72,83]):
  results=[]
  for bundle in [old,b]:
   q=Arena(bundle,18);q.put(DisableScreenFlag=0,VvVariant=0,VvMeter=meter,VvHudDirty=1,InvHudActive=0,VRAM_Buffer1_Offset=offset,ReloadCHRBank=0);q.array('VRAM_Buffer1',[0x24]*84);c,_=q.invoke('VvHud');results.append(((c.a,c.x,c.y,c.p&0xcf,c.sp),[q.get(n)for n in ['InvHudActive','InvHudPhysical','X5HudChrUpper','VvHudDirty','VRAM_Buffer1_Offset','ReloadCHRBank']],[q.get('VRAM_Buffer1',i)for i in range(84)]))
  assert results[0]==results[1]
  case('unchanged_vic_viper_variant0',meter=meter,offset=offset)
 # Cheap path for every identity: no pending state, same original post-LDA ABI.
 for identity,upper,x,y,flags in itertools.product(range(256),[0,1,2,3],[0,255],[0,255],[0x30,0x75,0xff]):
  q=arena(SelectedCharacter=identity,X5HudChrUpper=upper);q.m.page(2,116);r=run(b,q.m,address(b,'PnHudCommitAfterVram'),address(b,'PnPaletteScreenUpdate')+resume,0xa5,x,y,flags)
  assert r['state'][0:3]==(1 if selective else identity,x,y)and r['state'][4]==0xfd and not r['writes']
  assert (r['state'][3]&0x4d)==(flags&0x4d)
  case('no_pending_all_selector_bytes_abi',selector=identity,upper=upper,helper_cycles=r['cycles'],hook_JMP_cycles=3,extra_vs_original_LDA=r['cycles']+3-4)
 if selective:
  assert b['raw'][address(b,'PnPaletteScreenUpdate')%8192+16+116*8192:address(b,'PnPaletteScreenUpdate')%8192+16+116*8192+10]==old['raw'][address(old,'PnPaletteScreenUpdate')%8192+16+116*8192:address(old,'PnPaletteScreenUpdate')%8192+16+116*8192+10]
  for selector,flags in itertools.product([n for n in range(256)if n!=18],[0x30,0x31,0x74,0x7d,0xff]):
   results=[]
   for bundle in [old,b]:
    m=Bus(bundle);m.put(address(bundle,'SelectedCharacter'),selector);results.append(run(bundle,m,address(bundle,'PnPaletteScreenUpdate')+3,address(bundle,'PnPaletteScreenUpdate::Samus'),0xa5,37,193,flags))
   assert all(results[0][key]==results[1][key]for key in ['state','writes','reads','ram','banks','cycles'])
   case('all_nonship_selectors_zero_HUD_hook_overhead',selector=selector,flags=flags,extra_cycles=0)
 (a.output/'cases.json').write_text(json.dumps(rows,separators=(',',':'))+'\n',encoding='utf-8');proof=dict(passed=True,native_run=False,goal_complete=False,ROM_sha256=sha(a.candidate),script_sha256=sha(Path(__file__)),counts=counts,total_cases=len(rows),cases_sha256=sha(a.output/'cases.json'),scope='Actual linked foreground append/whole helper branches, pending/catchup/commit/discard/reset components. CPU fixture writes are isolated setup, not native acquisitions or PPU timing. Full NMI budget/IRQ and hardware rendering remain required.')
 (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(json.dumps(proof,indent=2))
if __name__=='__main__':main()
