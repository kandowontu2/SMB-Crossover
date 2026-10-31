"""Actual f523 source/cart CF scene guard, warm/life/player/reset contracts."""
from pathlib import Path
import hashlib,itertools,json,re,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import contra_force_presentation_controls_v3 as V
J,C,T,D=V.J,V.C,V.T,V.D
P=R/'build/contra-force-lifecycle-cart-v4';K=R/'build/contra-force-lifecycle-kernel-v6';O=R/'build/contra-force-lifecycle-controls-v4'
J.P=D.P=C.P=T.P=P;T.B=T.qualified(P/'joint/candidate.nes');T.PAYLOAD=(P/'joint/cf-stream.bin').read_bytes();T.COOKIE=(P/'joint/cf-cookie.bin').read_bytes()
L={n:int(v,16)for v,n in re.findall(r'al ([0-9A-Fa-f]+) \.(\w+)',(K/'runtime.lbl').read_text())};V.L=L;V.P=P;V.K=K
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
FLAGS=[v for v in range(256)if v&0x30==0x30]

def context(m,player=0,status=0,lives=2):
 T.put(m,CurrentPlayer=player,NumberofLives=lives,PlayerStatus=status,GameEngineSubroutine=8,TimerControl=0,GamePauseStatus=0,MmDeathFlag=0,
  AreaType=1,PlayerSize=0,Player_X_Position=120,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,ScreenLeft_X_Pos=0,
  ScreenLeft_PageLoc=0,PlayerFacingDir=1,Player_State=0,Player_X_Speed=0,Player_Y_Speed=0,InjuryTimer=0,StarInvincibleTimer=0,
  SavedJoypadBits=0,CurrentOAMOffset=0,ObjectOffset=0,CrouchingFlag=0,SwimmingFlag=0,OperMode=1,FamilyMainCommit=1,
  Mirror_PPUMASK=0,DisableScreenFlag=1,NmiDisable=255)

def load(var):
 m=T.Bus();T.put(m,FmGroups=var<<3);c=T.cpu(m,public=True);T.finish(m,c);T.exact(m,var)
 context(m);return m

def public(m,service,p=0x30,hook=None):
 c=J.shared(m,service,p=p);return T.finish(m,c,hook=hook)

def own(m,label,p=0x30):return V.invoke(m,label,p=p)
def last(m):return m.ram[2][L['CfHostLastLife']&8191]
def gear(m,var):return m.ram[2][0x7f+var]

def guards(bases):
 rows=[];bad=[dict(SelectedCharacter=0),dict(OperMode=0),dict(FamilyMainCommit=0),dict(Mirror_PPUMASK=24),dict(DisableScreenFlag=0),dict(NmiDisable=0),dict(GamePauseStatus=1)]
 for var,p,vals in itertools.product(range(4),FLAGS,bad):
  m=C.clone(bases[var]);T.put(m,**vals);before=[bytes(b)for b in m.ram];z=own(m,'CfHostSceneEnsure',p=p)
  assert z['AXYP']==[0x57,2,3,p&0x7c],('invalid fullAXYP',var,p,vals,z)
  assert [bytes(b)for b in m.ram]==before,('invalid context source write',var,p,vals)
  rows.append([var,p,vals,z['CPU']])
 accepted=[]
 for var,player,tier,p in itertools.product(range(4),range(2),range(3),[0x30,0x79]):
  m=C.clone(bases[var]);context(m,player,tier);z=public(m,15,p=p)
  assert m.ram[2][0x2e1]==player+1 and gear(m,var)==16|tier and last(m)==2
  # Genuine SFC imposes N/Z from returned original A57; all other flags/XY/A
  # preserve the SceneEnsure fullAXYP API, with validity C set.
  expected=(p&0x7c)|1
  assert z['AXYP']==[0x57,2,3,expected],('actual shared scene flags',var,player,tier,p,z)
  accepted.append([var,player,tier,p,z['CPU']])
 return dict(rejected_all64_flags_context_cases=len(rows),no_guest_state_writes_on_invalid_context=True,accepted_full_shared_B020_scene_cases=len(accepted),rows=rows,accepted=accepted)

def source_snapshot(m):
 # The genuine A2 importer intentionally leaves its current target pointer /
 # raw bank at02EC..EE. They are declared transport, not original source fields.
 # Compare every OTHER original state byte; verify those outputs separately.
 return bytes(m.ram[2][i]for i in range(0x500)if i not in[0x2ec,0x2ed,0x2ee])
def scene_target(m):
 assert bytes(m.ram[2][0x2ec:0x2ef])==bytes([L['CfHostSceneEnsure']&255,L['CfHostSceneEnsure']>>8,3])

def warm(bases):
 rows=[]
 for var,player,tier in itertools.product(range(4),range(2),range(3)):
  m=C.clone(bases[var]);context(m,player,tier);public(m,15)
  m.ram[2][0x7f+var]=0x20|tier # arbitrary original HP nibble: retention only, not gameplay HP claim
  before=source_snapshot(m);public(m,15);scene_target(m)
  assert source_snapshot(m)==before and gear(m,var)==0x20|tier
  rows.append([var,player,tier,'same life source fields exact'])
 # One actual native deferred1up, rather than manufacturing a life marker.
 m=C.clone(bases[0]);context(m,0,2);public(m,15);m.ram[2][0x7f]=0x22
 T.put(m,FloateyNum_Control=11,FloateyNum_Timer=43);V.invoke(m,'FloateyNumbersCore',x=0)
 assert T.get(m,'NumberofLives')==3
 before=source_snapshot(m);public(m,15);scene_target(m)
 assert source_snapshot(m)==before and gear(m,0)==0x22 and last(m)==3
 return dict(same_player_life_gear_HP_retention_cases=len(rows),actual_native_deferred_1up_preserves_gear=True,rows=rows)

def native_lives(bases):
 rows=[]
 for players in [0,1]:
  m=C.clone(bases[0]);context(m,0,2);T.put(m,NumberOfPlayers=players,OffScr_NumberofLives=5,WorldNumber=0,LevelNumber=0,AreaNumber=0)
  public(m,15);assert gear(m,0)==18
  V.invoke(m,'PlayerLoseLife',x=0)
  assert T.get(m,'PlayerStatus')==0
  expected_player=players;expected_life=5 if players else 1
  assert T.get(m,'CurrentPlayer')==expected_player and T.get(m,'NumberofLives')==expected_life
  # Genuine PlayerLoseLife called TransposePlayers/ContinueGame; these
  # explicit blank-scene entry inputs model the later admitted scene boundary.
  T.put(m,FamilyMainCommit=1,Mirror_PPUMASK=0,DisableScreenFlag=1,NmiDisable=255,GamePauseStatus=0)
  public(m,15)
  assert m.ram[2][0x2e1]==expected_player+1 and gear(m,0)==16 and last(m)==expected_life
  rows.append(dict(players=players+1,CurrentPlayer=expected_player,lives=expected_life,sourcegear=gear(m,0),native_status=0))
 return dict(actual_PlayerLoseLife_TransposePlayers_ContinueGame_cases=rows,status_reset_by_native_not_swapped_gear=True,one_native_life_injury_limit=True)

def native_app(m):
 skip=set(range(0x100,0x200))|set(range(0x2000,0x5c00))
 skip|={T.address(T.B,n)for n in ['CurrentBank','CurrentBankC']}
 return bytes(m[i]for i in range(0x8000)if i not in skip)

def reset(bases):
 rows=[];jn=T.address(T.B,'JnResetDispatch');bank=(T.location(T.B,'JnResetDispatch')-16)//8192|128
 assert T.address(T.B,'JnResetDispatch')==L['JnResetDispatch'] and L['CfNativeResetBank']==bank
 for var,p in itertools.product(range(4),FLAGS):
  base=C.clone(bases[var]);context(base,0,2);public(base,15);base.ram[2][0x7f+var]=0x22
  native=C.clone(base);z=V.invoke(native,'JnResetDispatch',p=p)
  m=C.clone(base);hits=[]
  def hook(c,i):
   if c.pc==jn and m.rawtags[(c.pc-32768)//8192]==bank:hits.append(c.sp)
  r=public(m,19,p=p,hook=hook)
  assert len(hits)==1 and r['AXYP']==z['AXYP'],('actual reset once/AXYP',var,p,hits,r,z)
  assert native_app(m)==native_app(native),('native reset application delta',var,p)
  assert gear(m,var)==0x22 and last(m)==2 and m.ram[2][0x2e1]==1
  assert m.ram[2][0x382]==10 and m.ram[2][0x482]==46 and m.ram[2][0x4d2]==1
  assert all(m.ram[2][i]==0 for i in range(0x383,0x39c)) # no lingering projectiles
  assert m.rawtags==base.rawtags and bytes(m[0x1e1:0x200])==bytes(base[0x1e1:0x200])
  rows.append([var,p,r['CPU'],z['CPU']])
 return dict(actual_B020_reset_JnReset_once_all64_flags=len(rows),native_AXYP_application_and_maps_exact=True,own_motion_projectiles_reset_gear_retained=True,rows=rows)

def presentation(bases):
 active=[]
 for var in range(4):
  m=C.clone(bases[var]);context(m);public(m,15);T.put(m,SavedJoypadBits=0);public(m,0)
  assert m.ram[2][0x31a]==[25,75,117,159][var];active.append(m)
 return dict(native_world=V.world(active),title_lives_portraits=V.portraits(active))

def main():
 assert not O.exists();O.mkdir();d=dict(passed=False,native=False,actual_natural_cold_or_Main=False,checks={})
 try:
  for p,h in json.loads((P/'source-stage.json').read_text())['bindings'].items():assert sha(p)==h,p
  bases=[load(v)for v in range(4)]
  for n,f in [('scene_context_guards',guards),('warm_and_1up',warm),('actual_native_life_and_player',native_lives),('native_reset_once',reset),('presentation_rebind',presentation)]:d['checks'][n]=f(bases);print('CF lifecycle',n,'PASS',flush=True)
  d['retained_source_v3_negative']='V3 new kernel replaced the old transformed host-runtime with raw reference and omitted genuine existing C2 CfHostCallInput/Body gates. Presentation caught an A3 nearcall into A1 targetPC data. V4 uses source v9 restoring these genuine gates; all frozen earlier leaves unchanged.'
  d['retained_v2_negative']='V2 warm check wrongly included the intentionally changed A2 transport target02EC..EE. V3 compares every other original state byte and separately asserts the exact current SceneEnsure pointer/raw3 output; no source product change.'
  d['retained_fixture_negative']='V1 compared originalN/Z across genuine SFC, which intentionally reloads returnedA57 and clearsN/Z. V2 expects genuine outerSFCN/Z; sourceSceneEnsure and all own-state assertions unchanged.'
  d['passed']=True
 except Exception as e:d.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  files=[Path(__file__),Path(V.__file__),Path(J.__file__),Path(C.__file__),Path(T.__file__),P/'source-stage.json',P/'joint/candidate.nes',P/'joint/candidate.dbg',P/'joint/cf-stream.bin',P/'joint/cf-cookie.bin',K/'build-proof.json',K/'runtime.lbl',R/'build/contra-force-lifecycle-controls-v1/controls.json',R/'build/contra-force-lifecycle-controls-v2/controls.json',R/'build/contra-force-lifecycle-controls-v3/controls.json',R/'build/cf-owner-retirement-v2/handoff.json']
  d['bindings']={str(p.resolve()):sha(p)for p in files};p=O/'controls.json';p.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(dict(path=str(p),sha256=sha(p),passed=d['passed'],error=d.get('error'))),flush=True)
if __name__=='__main__':main()
