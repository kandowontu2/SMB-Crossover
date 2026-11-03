"""Final owned strike consumer: admission, stale actors, repeat and reset."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_owned_drop_ack_1102_v121 as V
C,N,O=V.C,V.N,V.O


def helpers():
 source=Path(V.__file__);text=source.read_text().replace('v120','v122');env=dict(__file__=str(Path(__file__)),__name__='prince_strike_lifetime_helpers');exec(compile(text,str(source),'exec'),env);return env


def main():
 h=helpers();e,_=h['environment']();b,seed,_=C.loaded();lab=h['inject'](seed);inv=C.address(b,'InvDropEnemy');count=0;valid=0;repeats=0;types=['valid','sourceHP1','sourceDead84','inactiveUID','UID6','absent','foreignFlag','ID7','ID46','alreadyDefeated']
 for slot in range(6):
  for ID in range(7):
   for shape in types:
    m=N.fork(seed);m.ram[2][0x6d0]=1 if shape=='sourceHP1'else 0;m.ram[2][0x6de]=84 if shape=='sourceDead84'else 85;m.ram[2][0x61c]=0 if shape=='inactiveUID'else 134 if shape=='UID6'else 128|slot;m.ram[2][0x6e0]=1
    m[inv]=0xa5
    for i in range(6):m[C.address(b,'Enemy_Flag')+i]=0
    for name,value in dict(Enemy_Flag=0 if shape=='absent'else 2 if shape=='foreignFlag'else 1,Enemy_ID=7 if shape=='ID7'else 46 if shape=='ID46'else ID,Enemy_State=32 if shape=='alreadyDefeated'else 0,Enemy_X_Position=80,Enemy_PageLoc=0,Enemy_Y_Position=184,Enemy_Y_HighPos=1,Enemy_MovingDir=2,Enemy_BoundBoxCtrl=3).items():m[C.address(b,name)+slot]=value
    native=bytes(m[0x200:0x800])+bytes(m[0x5fe0:0x8000]);out=e['run'](m,'HuWeapons',lab);calls=out['native_calls'].get('ShellOrBlockDefeat',0);assert not out['regs'][3]&1 and not out['native_calls'].get('KillPlayer')
    if shape=='valid':
     assert calls==1 and m[C.address(b,'Enemy_State')+slot]&32 and m[inv]==slot and m.ram[2][0x61c]==m.ram[2][0x6e0]==0,(slot,ID,shape,out['native_calls'],m[C.address(b,'Enemy_State')+slot],m[inv],m.ram[2][0x61c],m.ram[2][0x6e0]);valid+=1
     native=bytes(m[0x200:0x800])+bytes(m[0x5fe0:0x8000]);again=e['run'](m,'HuWeapons',lab);assert not again['native_calls'].get('ShellOrBlockDefeat')and native==bytes(m[0x200:0x800])+bytes(m[0x5fe0:0x8000]);repeats+=1
    else:assert not calls and m[inv]==0xa5 and native==bytes(m[0x200:0x800])+bytes(m[0x5fe0:0x8000]),(slot,ID,shape)
    count+=1
 resets=[]
 for reset in ['Fresh','Retire']:
  m=N.fork(seed);m.ram[2][0x6d0]=0;m.ram[2][0x6de]=85;m.ram[2][0x61c]=128;m.ram[2][0x6e0]=1;m[inv]=0xa5
  N.put(m,Enemy_Flag=1,Enemy_ID=6,Enemy_State=0)
  target=0xb08c+3*36 if reset=='Fresh'else 0xae0b;out=C.C.C.I.invoke(m,193,target)
  native=bytes(m[0x200:0x800])+bytes(m[0x5fe0:0x8000]);after=e['run'](m,'HuWeapons',lab);assert not after['native_calls'].get('ShellOrBlockDefeat')and m[inv]==0xa5 and native==bytes(m[0x200:0x800])+bytes(m[0x5fe0:0x8000]);resets.append(reset)
 q=dict(passed=True,CPU_only=True,ROM_written=False,source_code_injected=True,changed_full_cold_qualified=False,consumer_cases=count,valid_native_defeats=valid,invalid_no_native_effect_cases=count-valid,repeated_exactly_once_cases=repeats,native_slots=6,native_IDs=list(range(7)),source_and_native_rejection_shapes=types[1:],fresh_and_authenticated_retire_cancelled_pending_actor=resets,all_row34_returns_C0_without_nativeKill=True,source_request='GuardHP0/dead85/activeUID are explicit typed-consumer preconditions in this finite matrix; native actor fields are fixture inputs. Actual source-earned strike/old-new GameLoop equivalence is separately established by123, rather than inferred from these predicate cases.',ordering='All guard/UID/flag/state/ID checks precede STX InvDropEnemy and nativeSuffix. No source tick/actor birth occurs between movement and row34; GameCore calls it before EnemiesAndLoopsCore. Native fireball defeat/erase may only invalidate the existing flag/state gate before delivery. NativeKill query follows completed ProxyOut in every row34 path.',scope='Final122 source prototype. Complete authenticated97 cold occurs before private image replacement; changed backing/cookie/cold and native emulator are not qualified. No shared/native ROM mutation or new state allocation.',bindings={p.relative_to(R).as_posix():C.C.C.M.sha(p.read_bytes())for p in [Path(__file__),Path(V.__file__),O/'deferred-strike-measurement-v122.json',O/'native-drop-policy-CPU-v119.json',*[O/f'native-{n}-v122.bin'for n in ['runtime','metadata','state']],O/'native-labels-v122.json',R/'src/game.s',R/'src/object.s']})
 (O/'strike-lifetime-CPU-v125.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':
 try:main()
 except Exception as error:
  (O/'strike-lifetime-negative-v125.json').write_text(json.dumps(dict(passed=False,CPU_only=True,source_injected=True,exception=repr(error)),indent=2)+'\n');raise
