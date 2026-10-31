"""Actual menu publication and native scene-to-loader retirement ordering."""
from pathlib import Path
import collections,hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import contra_force_a2_router_controls_v3 as C
from prepare_ff_current_component_v2 import qualified
T=C.T
P=R/'build/cf-bt-shared-transport-v3';J=R/'build/cf-owner-retirement-v2/joint';O=R/'build/cf-owner-retirement-coverage-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def select_bundle(root):
 T.P=root.parent;T.B=qualified(root/'candidate.nes');T.PAYLOAD=(root/'cf-stream.bin').read_bytes();T.COOKIE=(root/'cf-cookie.bin').read_bytes()
def loaded(root,var):
 select_bundle(root);m=T.Bus();T.put(m,FmGroups=var<<3,NumberofLives=2,CurrentPlayer=0,GamePauseStatus=0,GameEngineSubroutine=8,TimerControl=0)
 # The new loader owns its checkpoint. Old parent explicitly requires one.
 if root==P/'joint':T.checkpoint(m)
 c=T.cpu(m,public=True);T.finish(m,c);T.exact(m,var)
 assert m.ram[2][0x1fe0]==0xa7
 m.writes.clear();m.ram_writes.clear();m.executed_guest.clear();return m
def call(m,name,**kw):
 bank=(T.location(T.B,name)-16)//8192|128;c=C.start(m,T.address(T.B,name),bank,**kw)
 points={}
 for n in['CfRetire','BwScene','S2InitScreenPrepare','QwSceneInit','ArGenSceneInit','FwSceneInit','MoveAllSpritesOffscreen','FwLoad','BwLoad','BtLoad','QwBoot','BwMenuResolve']:
  try:points[(T.address(T.B,n),(T.location(T.B,n)-16)//8192|128)]=n
  except KeyError:pass
 events=[];rw=0;wr=0;selected=T.address(T.B,'SelectedCharacter');calls=[]
 def watch(cpu,step):
  nonlocal rw,wr
  if cpu.pc>=0x8000:
   k=(cpu.pc,m.rawtags[(cpu.pc-0x8000)//8192])
   if k in points:calls.append(points[k]);events.append(dict(step=step,event='entry',name=points[k],CF_valid=m.ram[2][0x1fe0]))
  for bank,at,value in m.ram_writes[rw:]:
   if bank==2 and at==0x1fe0:events.append(dict(step=step,event='C2_valid_write',value=value))
   if bank==3:events.append(dict(step=step,event='RAM3_write',offset=at,value=value,CF_valid=m.ram[2][0x1fe0]))
  rw=len(m.ram_writes)
  for at,value in m.writes[wr:]:
   if at==selected:events.append(dict(step=step,event='selected_write',value=value,CF_valid=m.ram[2][0x1fe0]))
  wr=len(m.writes)
 z=T.finish(m,c,watch);watch(c,z['steps'])
 return dict(**z,calls=dict(collections.Counter(calls)),events=events)
def main():
 O.mkdir(exist_ok=False);q=dict(passed=False,source_CPU=True,native=False,menu=[],scene=[],global_init=[],direct_BT_contract=[])
 try:
  seeds={v:loaded(J,v)for v in range(4)}
  for var,slot in itertools.product(range(4),range(32)):
   m=C.clone(seeds[var]);T.put(m,SelectedCharacter=31,FmGroups=var<<3,CrossoverMenuIndex=slot,MarioVariant=0,FmAlts=0,OperMode=0,FamilyMainCommit=1)
   m.writes.clear();m.ram_writes.clear();z=call(m,'MenuResolveCharacter')
   writes=[e for e in z['events']if e['event']=='selected_write'];clear=[e for e in z['events']if e['event']=='C2_valid_write']
   assert writes and clear and clear[0]['value']==0 and clear[0]['step']<writes[0]['step']
   assert all(e['CF_valid']==0 for e in writes)and z['calls'].get('CfRetire')==1
   q['menu'].append(dict(variant=var,slot=slot,CPU=z['CPU'],minimum_SP=z['minimum_SP'],first_clear=clear[0],first_publish=writes[0]))
  for var,raw,alts in itertools.product(range(4),[22,27],[0,8]):
   if raw==22 and alts:continue
   m=C.clone(seeds[var]);T.put(m,SelectedCharacter=raw,FmGroups=var<<3,FmAlts=alts,FfVariant=0,OperMode=1,OperMode_Task=1,FamilyMainCommit=1,Mirror_PPUMASK=0,DisableScreenFlag=1,NmiDisable=255,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0,CurrentPlayer=var&1)
   m.writes.clear();m.ram_writes.clear();z=call(m,'InitScreen')
   r=[e for e in z['events']if e['event']=='RAM3_write'];clear=[e for e in z['events']if e['event']=='C2_valid_write'];entry=[e for e in z['events']if e.get('name')=='CfRetire']
   assert r and clear and entry and entry[0]['step']<clear[0]['step']<r[0]['step']
   assert all(e['CF_valid']==0 for e in r)
   for n in['CfRetire','BwScene','S2InitScreenPrepare','QwSceneInit','ArGenSceneInit','FwSceneInit','MoveAllSpritesOffscreen']:
    assert z['calls'].get(n)==1,(raw,alts,n,z['calls'])
   assert m.ram[3][0x1fe0:0x1fe2]==bytes([167,raw])
   # Check actual external auth after a foreign replacement, without ever
   # executing even the first untrusted A2 opcode.
   T.put(m,SelectedCharacter=31,FmGroups=var<<3);m.executed_guest.clear();g=call(m,'CfOrBtCheck')
   assert not g['AXYP'][3]&1 and not m.executed_guest
   q['scene'].append(dict(variant=var,target=raw,form=alts,CPU=z['CPU'],minimum_SP=z['minimum_SP'],calls=z['calls'],retire=entry[0],first_clear=clear[0],first_RAM3_write=r[0],RAM3_writes=len(r),guard_after=g['AXYP']))
  for var in range(4):
   m=C.clone(seeds[var]);T.put(m,SelectedCharacter=31,FmGroups=var<<3,NmiDisable=255,FamilyMainCommit=1)
   m.writes.clear();m.ram_writes.clear();z=call(m,'CrossoverInit')
   selected=[e for e in z['events']if e['event']=='selected_write'];clear=[e for e in z['events']if e['event']=='C2_valid_write']
   assert selected and clear and clear[0]['value']==0 and clear[0]['step']<selected[0]['step']and z['calls'].get('QwBoot')==1
   q['global_init'].append(dict(variant=var,calls=z['calls'],first_clear=clear[0],first_publish=selected[0]))
  # BT has no installed caller in this inert leaf. Its exported loader API
  # requires explicit retirement, demonstrated as a REAL source sequence.
  for var in range(4):
   m=C.clone(seeds[var]);T.put(m,SelectedCharacter=33,FmGroups=var<<3,OperMode=1,FamilyMainCommit=1,Mirror_PPUMASK=0,DisableScreenFlag=1,NmiDisable=255)
   call(m,'CfRetire');assert m.ram[2][0x1fe0]==0
   z=call(m,'BtLoad');assert z['AXYP'][3]&1 and m.ram[3][0x1fe1]==33
   assert all(e['CF_valid']==0 for e in z['events']if e['event']=='RAM3_write')
   q['direct_BT_contract'].append(dict(variant=var,CPU=z['CPU'],explicit_retire_required=True))
  # Preserve the concrete old unsafe transition as an immutable-parent
  # witness: its scene overwritesA3 while leavingCF's C2 valid cookie live.
  m=loaded(P/'joint',0);T.put(m,SelectedCharacter=27,FmAlts=8,OperMode=1,OperMode_Task=1,FamilyMainCommit=1,Mirror_PPUMASK=0,DisableScreenFlag=1,NmiDisable=255)
  z=call(m,'InitScreen');assert m.ram[3][0x1fe1]==27 and m.ram[2][0x1fe0]==167
  T.put(m,SelectedCharacter=31,FmGroups=0);m.executed_guest.clear();g=call(m,'CfOrBtCheck');assert g['AXYP'][3]&1 and not m.executed_guest
  q['old_parent_negative']=dict(candidate=sha(P/'joint/candidate.nes'),CF_cookie_stale_A7=True,A3_family=27,ROM_guard_wrongly_accepts_stale_CF=True,no_guest_opcode_executed=True)
  q.update(passed=True,actual_menu_retire_before_publish=128,actual_native_scene_CF_to_FF_BW=12,actual_global_before_publish=4,actual_direct_BT_explicit_contract=4,
   installed_call_coverage='FwLoad sole FwSceneInit caller, BwLoad sole BwScene caller, both after early sceneCfRetire. BtLoad has no installed caller; directAPI explicitly requires retire. QwBoot clearsC2 before globalSelected publication.',
   limits='CF andBT remainpending. No natural CF cold/load/Main, warmCF health/player semantics or all-soundtest-selected stores claim. Direct FW/BW/BTloader API users must honor retirement contract; worker existence is not a global hook.')
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 paths=[Path(__file__),Path(C.__file__),Path(T.__file__),J/'candidate.nes',J/'candidate.dbg',J/'cf-stream.bin',J/'cf-cookie.bin',J/'source-stage.json',P/'joint/candidate.nes',P/'joint/candidate.dbg']
 q['bindings']={str(p.resolve()):sha(p)for p in paths};(O/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['menu','scene','global_init','direct_BT_contract','bindings']}));assert q['passed']
if __name__=='__main__':main()
