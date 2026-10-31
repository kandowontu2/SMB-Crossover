"""Actual CF->BT scene/cold-color call order before first A3 overwrite."""
from pathlib import Path
import itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import cf_cold_warm_retirement_controls_v1 as V
T,C=V.T,V.C;J=R/'build/bt-jmp-row-cold-source-v1/joint';O=R/'build/bt-jmp-cold-retirement-controls-v1'

def main():
 O.mkdir(exist_ok=False);q=dict(passed=False,native=False,CF_BT_pending=True,menu=[],cold=[],active_reject=[],direct_contract=[])
 try:
  V.select(J);seeds={v:V.V.loaded(J,v)for v in range(4)}
  for var,player,variant in itertools.product(range(4),range(2),range(2)):
   m=C.clone(seeds[var]);V.blank(m,33,0,0);T.put(m,FmGroups=variant<<5,CurrentPlayer=player,ScreenRoutineTask=0,NumberofLives=2,GameEngineSubroutine=8,PlayerStatus=0,Player_X_Position=120,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,PlayerFacingDir=1)
   assert m.ram[2][0x1fe0]==167
   scene=V.V.call(m,'InitScreen');clear=[e for e in scene['events']if e['event']=='C2_valid_write']
   assert scene['calls'].get('CfRetire')==1 and clear and clear[0]['value']==0
   assert not[e for e in scene['events']if e['event']=='RAM3_write'],('raw33 scene must not copy before colors',scene['calls'])
   for n in['BwScene','S2InitScreenPrepare','QwSceneInit','ArGenSceneInit','FwSceneInit','MoveAllSpritesOffscreen']:assert scene['calls'].get(n)==1,(n,scene['calls'])
   assert T.get(m,'ScreenRoutineTask')==1 and m.ram[2][0x1fe0]==0
   m.writes.clear();m.ram_writes.clear();color=V.V.call(m,'SetupIntermediate')
   writes=[e for e in color['events']if e['event']=='RAM3_write']
   assert color['calls'].get('BtLoad')==1 and writes and all(e['CF_valid']==0 for e in writes)
   assert m.ram[3][0x1fe0:0x1ff0]==(J/'bt/cookie.bin').read_bytes()
   assert m.ram[3][T.address(T.B,'BtHostReady')&8191]==1 and T.get(m,'ScreenRoutineTask')==2
   assert writes[0]['offset']==0x1fe0 and writes[0]['value']==0 and writes[-1]['offset']!=0x1fe0 # Ensure writes source state after valid publication.
   pubs=[e for e in writes if e['offset']==0x1fe0];assert pubs[-1]['value']==167
   reads=m.ppu_reads;m.writes.clear();m.ram_writes.clear();warm=V.V.call(m,'GetPlayerColors')
   assert m.ppu_reads==reads and not[e for e in warm['events']if e['event']=='RAM3_write']
   q['cold'].append(dict(CF_class=var,player=player,BT_variant=variant,scene_calls=scene['calls'],clear_before_setup=clear[0],setup_calls=color['calls'],first_A3_write=writes[0],A3_writes=len(writes),source_ready=True,actual_CopyReads=reads,warm_no_copy=True))
  # Real menu publication clears foreign C2 while old Selected is still31.
  for var,variant in itertools.product(range(4),range(2)):
   m=C.clone(seeds[var]);T.put(m,SelectedCharacter=31,FmGroups=variant<<5,CrossoverMenuIndex=23,OperMode=0,FamilyMainCommit=1)
   m.writes.clear();m.ram_writes.clear();z=V.V.call(m,'MenuResolveCharacter');publish=[e for e in z['events']if e['event']=='selected_write'];clear=[e for e in z['events']if e['event']=='C2_valid_write']
   assert publish and clear and clear[0]['step']<publish[0]['step'] and publish[0]['value']==33 and all(e['CF_valid']==0 for e in publish)
   q['menu'].append(dict(CF_class=var,BT_variant=variant,first_clear=clear[0],first_publish=publish[0]))
  # Existing color callers in title or active rendering may queue colors;
  # they cannot overwrite A3, even when presented with a stale CF C2 lease.
  for context,values in[('title',dict(OperMode=0)),('active',dict(Mirror_PPUMASK=30,DisableScreenFlag=0)),('notbusy',dict(FamilyMainCommit=0)),('normal',dict(NmiDisable=0))]:
   m=C.clone(seeds[0]);V.blank(m,33);T.put(m,**values);before=[bytes(x)for x in m.ram];m.writes.clear();m.ram_writes.clear();reads=m.ppu_reads
   z=V.V.call(m,'GetPlayerColors');assert not m.ram_writes and [bytes(x)for x in m.ram]==before and m.ppu_reads==reads
   q['active_reject'].append(dict(context=context,calls=z['calls'],no_A3_or_C2_write=True))
  # The direct exported API is not silently globalized: this bounded witness
  # documents its existing explicit-retirement requirement. Production screen
  # callers above satisfy it before this worker is reached.
  m=C.clone(seeds[0]);V.blank(m,33);before=m.ram[2][0x1fe0];z=V.V.call(m,'BtLoad')
  assert before==167 and m.ram[2][0x1fe0]==167 and m.ram[3][0x1fe1]==33
  q['direct_contract']=dict(exported_BtLoad_does_not_retire_CF=True,explicit_prior_CfRetire_required=True,stale_C2_witness_retained=True,not_a_production_hook=True)
  q.update(passed=True,actual_CF_to_BT_screen_setup_pairs=len(q['cold']),actual_retire_before_Selected33=len(q['menu']),source_context_rejections=len(q['active_reject']),scope='Actual InitScreen -> earlyCfRetire -> native scene chain once; actual next SetupIntermediate -> GetPlayerColors -> ROM26 -> BtAcquire -> verified load+Ensure. No pending gate bypass or manually staged BT payload. This call-order fixture is not yet whole cold parser/admission; direct loader contract remains explicit.')
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 files=[Path(__file__),Path(V.__file__),Path(V.V.__file__),Path(C.__file__),Path(T.__file__),J/'source-stage.json',J/'candidate.nes',J/'candidate.dbg',J/'bt/loader.s',J/'bt/preview.s',J/'bt/cookie.bin',J/'cf-cookie.bin']
 q['bindings']={str(p.resolve()):V.sha(p)for p in files};(O/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['menu','cold','bindings']}),flush=True);assert q['passed'],q.get('error')
if __name__=='__main__':main()
