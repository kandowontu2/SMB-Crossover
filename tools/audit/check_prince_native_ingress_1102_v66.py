"""Actual complete native pickup/body ingresses with the granted rare gate."""
from pathlib import Path
import hashlib,inspect,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prepare_prince_native_manifest_1102_v65 as M
import check_prince_current_ingress_1102_v61 as F
O=M.O


def main():
 text=inspect.getsource(F.main);changes={
  'current-ingress-negative-v61.json':'native-ingress-negative-v66.json',
  'current-ingress-CPU-v61.json':'native-ingress-CPU-v66.json',
  "O/'collision-manifest-v59.json'":"O/'native-manifest-v65.json'",
  'actual_HuFullBox=True,actual_PowerUpObjHandler_pickup_episodes=episodes':'actual_HuFullBox=True,actual_PowerUpObjHandler_pickup_episodes=episodes,actual_body_contact_episodes=body_cases',
  'finally:N.NesMPU=actual':''' for sword in [0,1,2]:
   for action in [0,62,69,74]:
    n=N.fork(native_seed);n.ram[2][0x6ee]=sword;n.ram[2][0x6cf]=5;n.ram[2][0x616]=action;n.ram[2][0x617]=171;slot=0;N.put(n,ObjectOffset=slot,TimerControl=0,FrameCounter=0)
    for field,value in dict(Enemy_Flag=1,Enemy_ID=6,Enemy_State=0,Enemy_X_Position=48,Enemy_PageLoc=0,Enemy_Y_Position=184,Enemy_Y_HighPos=1,Enemy_BoundBoxCtrl=3,Enemy_MovingDir=2).items():n[address(new,field)+slot]=value
    for native in ['RelativeEnemyPosition','GetEnemyOffscreenBits','GetEnemyBoundBox']:N.invoke(n,native,a=83,x=slot,y=0,p=0x21)
    before=dict(calls);out=N.invoke(n,'PlayerEnemyCollision',a=83,x=slot,y=0,p=0x21);delta={k:v-before.get(k,0)for k,v in calls.items()if v!=before.get(k,0)}
    assert delta.get('GuestBodyContactBridge')==1 and delta.get('PpNativeContact')==1,(sword,action,delta,out)
    expect=5 if action in [62,69,74]else 4 if sword==2 else 0
    assert n.ram[2][0x6cf]==expect and N.get(n,'NumberofLives')==2 and N.get(n,'GameEngineSubroutine')==8,(sword,action,n.ram[2][0x6cf],expect)
    body_cases.append(dict(sword=sword,action=action,original_HP=expect,CPU=out['CPU'],minimum_SP=out['minimum_SP'],actual_ingress_calls=delta))
 finally:N.NesMPU=actual''',
  'N.NesMPU=Trace;episodes=[]':'N.NesMPU=Trace;episodes=[];body_cases=[]',
 }
 for old,new in changes.items():assert old in text,old;text=text.replace(old,new)
 env=dict(F.__dict__,M=M,__file__=str(Path(__file__)));exec(compile(text,str(Path(__file__)),'exec'),env);env['main']()
 file=O/'native-ingress-CPU-v66.json';q=json.loads(file.read_text());assert q['passed'];q.update(private_execution_granted=True,qualified_fixture_SHA256=hashlib.sha256(text.encode()).hexdigest(),new_execution_granted=True,scope='Actual current16a9 private granted image: complete resident cold, HuFullBox, real PowerUpObjHandler→maturity→native rectangle overlap→Prince pickup all4types, real PlayerEnemyCollision→GuestBodyContactBridge→original source defender gate all3swordmodes×4actions. Exact cookie rejects and raw256 selector closed. Explicit CPU actors only, no emulator RAM seeding or playable/fullstage/menu/install claim. Head/side/lifecycle/render/actual native play still require qualification. Audio mixer/mapping incomplete.')
 q['bindings'].update({p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),O/'native-manifest-v65.json',O/'native-nr-gate-proposal-v64.json',O/'current-ingress-negative-v61.json',R/'docs/qa/allocations/prince-native-rare-gate-1102-v64.json']});file.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q[k]for k in ['passed','successor_memory_SHA256','Prince_bad_header_byte_rejections','raw256_three_cookie_selector_cases','actual_PowerUpObjHandler_pickup_episodes','actual_body_contact_episodes']}))


if __name__=='__main__':main()
