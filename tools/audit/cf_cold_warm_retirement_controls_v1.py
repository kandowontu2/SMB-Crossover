"""Finite current cold/warm owner boundary ordering; no menu admission."""
from pathlib import Path
import collections,hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import cf_owner_retirement_coverage_v2 as V
from prepare_ff_current_component_v2 import qualified
T,C=V.T,V.C
J=R/'build/cf-cold-warm-source-v3/joint';P=R/'build/cf-owner-retirement-v2/joint';O=R/'build/cf-cold-warm-retirement-controls-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
BUNDLES={}

def select(root):
 if root not in BUNDLES:BUNDLES[root]=(qualified(root/'candidate.nes'),(root/'cf-stream.bin').read_bytes(),(root/'cf-cookie.bin').read_bytes())
 T.P=root.parent;T.B,T.PAYLOAD,T.COOKIE=BUNDLES[root]
V.select_bundle=select

def blank(m,raw,var=0,alts=0):
 T.put(m,SelectedCharacter=raw,FmGroups=var<<3,FmAlts=alts,FfVariant=0,OperMode=1,OperMode_Task=1,FamilyMainCommit=1,Mirror_PPUMASK=0,DisableScreenFlag=1,NmiDisable=255,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0,CurrentPlayer=0,GamePauseStatus=0)
 m.writes.clear();m.ram_writes.clear();m.executed_guest.clear()

def main():
 O.mkdir(exist_ok=False);q=dict(passed=False,native=False,CF_BT_pending=True,menu=[],foreign_scene=[],warm_scene=[],global_init=[])
 try:
  seeds={v:V.loaded(J,v)for v in range(4)}
  for var,slot in itertools.product(range(4),range(32)):
   m=C.clone(seeds[var]);T.put(m,SelectedCharacter=31,FmGroups=var<<3,CrossoverMenuIndex=slot,MarioVariant=0,FmAlts=0,OperMode=0,FamilyMainCommit=1)
   m.writes.clear();m.ram_writes.clear();z=V.call(m,'MenuResolveCharacter')
   writes=[e for e in z['events']if e['event']=='selected_write'];clear=[e for e in z['events']if e['event']=='C2_valid_write']
   assert writes and clear and clear[0]['value']==0 and clear[0]['step']<writes[0]['step']
   assert all(e['CF_valid']==0 for e in writes)and z['calls'].get('CfRetire')==1
   q['menu'].append(dict(variant=var,slot=slot,CPU=z['CPU'],first_clear=clear[0],first_publish=writes[0]))
  for var,raw,alts in itertools.product(range(4),[22,27],[0,8]):
   if raw==22 and alts:continue
   m=C.clone(seeds[var]);blank(m,raw,var,alts);z=V.call(m,'InitScreen')
   r=[e for e in z['events']if e['event']=='RAM3_write'];clear=[e for e in z['events']if e['event']=='C2_valid_write'];entry=[e for e in z['events']if e.get('name')=='CfRetire']
   assert r and clear and entry and entry[0]['step']<clear[0]['step']<r[0]['step']
   assert all(e['CF_valid']==0 for e in r)
   for n in['CfRetire','BwScene','S2InitScreenPrepare','QwSceneInit','ArGenSceneInit','FwSceneInit']:assert z['calls'].get(n)==1,(raw,alts,n,z['calls'])
   assert m.ram[3][0x1fe0:0x1fe2]==bytes([167,raw])
   T.put(m,SelectedCharacter=31,FmGroups=var<<3);m.executed_guest.clear();g=V.call(m,'CfOrBtCheck')
   assert not g['AXYP'][3]&1 and not m.executed_guest
   q['foreign_scene'].append(dict(variant=var,target=raw,form=alts,CPU=z['CPU'],calls=z['calls'],retire=entry[0],first_clear=clear[0],first_RAM3_write=r[0],RAM3_writes=len(r),guard_after=g['AXYP']))
  for var in range(4):
   m=C.clone(seeds[var]);blank(m,31,var)
   # First real scene is the constructor consumer, with an actual verified
   # loaded image. The following scene must retain it instead of copying.
   first=V.call(m,'InitScreen');assert m.ram[2][0x2e1]==1 and m.ram[2][0x1fe0]==167
   assert first['calls'].get('CfRetire',0)==0
   m.writes.clear();m.ram_writes.clear();m.executed_guest.clear();before=m.ppu_reads
   z=V.call(m,'InitScreen')
   assert m.ppu_reads==before and m.ram[2][0x1fe0]==167
   assert not[e for e in z['events']if e['event']=='C2_valid_write']
   assert not[e for e in z['events']if e['event']=='RAM3_write']
   assert z['calls'].get('CfRetire',0)==0
   q['warm_scene'].append(dict(variant=var,CPU=z['CPU'],calls=z['calls'],PPU_copy_reads=0,C2_valid_retained=True))
   m=C.clone(seeds[var]);T.put(m,SelectedCharacter=31,FmGroups=var<<3,NmiDisable=255,FamilyMainCommit=1)
   m.writes.clear();m.ram_writes.clear();z=V.call(m,'CrossoverInit')
   selected=[e for e in z['events']if e['event']=='selected_write'];clear=[e for e in z['events']if e['event']=='C2_valid_write']
   assert selected and clear and clear[0]['value']==0 and clear[0]['step']<selected[0]['step']and z['calls'].get('QwBoot')==1
   q['global_init'].append(dict(variant=var,calls=z['calls'],first_clear=clear[0],first_publish=selected[0]))
  q.update(passed=True,actual_menu_retire_before_publish=128,actual_foreign_scene_retire_before_all_A3_writes=12,actual_warm_CF_scenes=4,actual_global_clear_before_publish=4,
   scope='Current installed scene callers: inner FwLoad/BwLoad follow early foreign retire. Selected31 authenticates and retains valid warm payload. BT remains pending with no installed acquisition; direct API contract remains explicitly retired in frozen foundation. No menu readiness/native/palette admission.')
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 paths=[Path(__file__),Path(V.__file__),Path(C.__file__),Path(T.__file__),J/'source-stage.json',J/'candidate.nes',J/'candidate.dbg',J/'cf-stream.bin',J/'cf-cookie.bin',R/'build/cf-owner-retirement-coverage-v2/controls.json',R/'build/contra-force-cold-warm-rebind-v1/controls.json']
 q['bindings']={str(p.resolve()):sha(p)for p in paths};(O/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['menu','foreign_scene','warm_scene','global_init','bindings']}));assert q['passed']
if __name__=='__main__':main()
