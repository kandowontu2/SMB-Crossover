"""Preserve v3; qualify a real airborne pole approach and grounded A edge."""
from pathlib import Path
from argparse import Namespace
import csv,inspect,json
import current_smb3_powerups_prepare_v1 as prior
from current_smb3_pole_routes_prepare_v3 import columns
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
from current_roster_compact_11_v1 import ROOT,prepare,sha
ROM=ROOT/'build/roster-20261028-fixes.nes';EXPECTED='ee1152a49deae31e82d202159310fa3719cbcfd85de571fd1b9ac15a1cd2a7b3'
POLICY=ROOT/'tools/playthroughs/current_roster_smb3_pole_v4.lua'
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')

def campaign(b,cols,var,form,old):
 text=inspect.getsource(prior.campaign);anchor='    return dict(passed=True,native_run=False,mode=mode,variant=var,';assert text.count(anchor)==1
 text=text.replace(anchor,'    return q,main,dict(passed=True,native_run=False,mode=mode,variant=var,').replace("q.get('GameEngineSubroutine')==8,('No staged death/transition'","q.get('GameEngineSubroutine')in[4,8],('No staged death/transition'")
 env=dict(vars(prior));env['PLAN']=prior.PLAN[:11]if form==4 else prior.PLAN[:1];exec(compile(text,str(__file__)+'::real_airborne_prefix','exec'),env);q,main,prefix=env['campaign'](b,0,var)
 prior.arena(q,dict(kind='idle',form=form));q.put(Player_X_Position=192,Player_PageLoc=11,MmOldX=192,ScrollLock=1,ScreenLeft_X_Pos=228,ScreenLeft_PageLoc=11,ScreenRight_X_Pos=227,ScreenRight_PageLoc=12)
 # Source emits the early approach jump itself. No private velocity/InAir,
 # form, resource or jump outcome is installed.
 for col in range(176,208):
  for row,value in enumerate(cols[col]):q.set('Block_Buffer_1',value,(col%32//16)*208+row*16+col%16)
 end=address(b,'E_GroundArea2')-1;q.put(EnemyDataLow=end&255,EnemyDataHigh=end>>8,EnemyDataOffset=0)
 rows=[];early=False;holding=False;admissions=[];air_at_edge=None;v3_press=None
 for tick in range(240):
  x=q.get('Player_X_Position')+256*q.get('Player_PageLoc');y=q.get('Player_Y_Position');ground=q.get('Player_State')==0;prev=q.get('M3Previous');bits=65
  if x<3104:
   if x>=3030 and not early and ground and not prev&128:early=True
   if early:bits=193
  else:
   if x>=3120 and air_at_edge is None:air_at_edge=dict(update=tick,x=x,y=y,state=q.get('Player_State'),previous=prev)
   if x<3120:holding=False
   elif old:
    if not holding and not prev&128:holding=True;v3_press=dict(update=tick,x=x,y=y,state=q.get('Player_State'),previous=prev)
    if holding:bits=193
   elif holding:
    if ground and prev&128:holding=False
    else:bits=193
   elif ground and not prev&128:
    holding=True;bits=193;admissions.append(dict(update=tick,x=x,y=y,state=q.get('Player_State'),previous=prev))
  main(bits);z=dict(update=tick,buttons=bits,x=q.get('Player_X_Position')+256*q.get('Player_PageLoc'),y=q.get('Player_Y_Position'),state=q.get('Player_State'),vy=q.get('Player_Y_Speed'),engine=q.get('GameEngineSubroutine'),form=q.get('M3Form'),previous=q.get('M3Previous'));rows.append(z)
  assert q.get('M3Form')==form
  if z['engine']==4:break
 assert air_at_edge and air_at_edge['state']!=0,('Real airborne approach required',form,var,air_at_edge)
 if not old:assert admissions and all(a['state']==0 and not a['previous']&128 for a in admissions)and rows[-1]['engine']==4,('Grounded edge and pole entry',admissions,rows[-8:])
 return dict(old_v3=old,variant=var,mode=0,form=form,earned_prefix_calls=prefix['complete_GameLoop_calls'],calls=len(rows),air_at3120=air_at_edge,v3_first_A=v3_press,grounded_A=admissions,actual_terminal=rows[-1],rows=rows)

def main():
 assert sha(ROM)==EXPECTED;b=scoped_load(ROM);cols=columns(b);cases=[]
 for old,form,var in[(True,0,0)]+[(False,f,v)for f in[0,4]for v in[0,1]]:
  z=campaign(b,cols,var,form,old);cases.append(z);print(json.dumps({k:v for k,v in z.items()if k!='rows'}),flush=True)
 assert cases[0]['v3_first_A']['state']!=0 and cases[0]['actual_terminal']['engine']==8,'Preserved actual source v3 missed airborne edge counterexample'
 native=ROOT/'build/verification/compact-ee1152-mario3-easy-v3';rows=list(csv.DictReader((native/'trace.csv').open()));first=next(r for r in rows if r.get('mask')=='193'and r.get('x')and 3120<=int(r['x'])<3160);assert first['state']=='2'
 proof=ROOT/'build/current_smb3_pole_v4_source.json';assert not proof.exists();put(proof,dict(passed=True,native_run=False,Lua_VM_executed=False,ROM_sha256=EXPECTED,cases=cases,preserved_v3=dict(native_first_air_A=first,trace_sha256=sha(native/'trace.csv'),scope='Snapshot of actual in-progress/terminal v3 trace as read; no rewriting its ready/native files. v3 source v4 proof retains the missed-air-edge counterexample.'),scope='One actual earned-prefix source campaign per form/variant, then typed neutral player3008/Y176 and native parser cells. Actual earlier A jump produces airborne3120. Input-only v4 waits genuine ground/released M3Previous, then enters actual engine4; not exact unlogged native state reconstruction or full native clear.',bindings={str(p):sha(p)for p in[Path(__file__),POLICY,ROM,ROM.with_suffix('.dbg'),ROM.with_suffix('.lbl'),ROOT/'tools/audit/current_smb3_pole_routes_prepare_v3.py',ROOT/'tools/audit/current_smb3_powerups_prepare_v1.py',ROOT/'tools/playthroughs/current_roster_smb3_stair_v2.lua']}))
 outputs=[]
 for identity in['mario3','luigi3']:
  out=ROOT/('build/verification/compact-ee1152-'+identity+'-easy-v4');prepare(Namespace(identity=identity,mode='easy',rom=ROM,expected_sha256=EXPECTED,output=out,frames=8000,policy=POLICY,replay=None));rp=out/'ready.json';z=json.loads(rp.read_text());cmd=out/'command.json';put(cmd,z['command'])
  for p in[Path(__file__),POLICY,proof,ROOT/'tools/playthroughs/current_roster_smb3_stair_v2.lua',cmd]:z['bindings'][str(p.resolve())]=sha(p)
  z.update(native_run=False,input_only=True,source_proof_sha256=sha(proof),scope='Only ground/released-A pole takeoff and release/retry on landing. v2 stair/generic controller and strict8000 route/hardware/container/caps unchanged. Old v3 native/source air-edge failures retained.');put(rp,z);assert all(sha(Path(p))==h for p,h in z['bindings'].items());outputs.append(dict(identity=identity,ready=str(rp),sha256=sha(rp),command=str(cmd),bindings=len(z['bindings'])))
 put(ROOT/'build/current_smb3_pole_v4_handoff.json',dict(native_run=False,proof=str(proof),proof_sha256=sha(proof),readies=outputs));print(json.dumps(outputs),flush=True)
if __name__=='__main__':main()
