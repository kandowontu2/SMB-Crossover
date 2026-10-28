"""Finite actual-source pole jump, unchanged stair2 and strict route guards."""
from pathlib import Path
from argparse import Namespace
import csv,inspect,json
import current_smb3_powerups_prepare_v1 as prior
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address
from current_roster_compact_11_v1 import ROOT,prepare,sha
ROM=ROOT/'build/roster-20261028-fixes.nes';EXPECTED='ee1152a49deae31e82d202159310fa3719cbcfd85de571fd1b9ac15a1cd2a7b3'
POLICY=ROOT/'tools/playthroughs/current_roster_smb3_pole_v3.lua'
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')

def columns(b):
 q=Arena(b,17);q.put(AreaPointer=37,AreaType=1,WorldNumber=0,LevelNumber=0);q.invoke('GetAreaDataAddrs');q.array('AreaObjectLength',[255]*3);out={}
 for col in range(225):
  q.put(CurrentPageLoc=col//16,CurrentColumnPos=col%16,BlockBufferColumnPos=col%32);q.invoke('AreaParserCore');out[col]=[q.get('Block_Buffer_1',(col%32//16)*208+row*16+col%16)for row in range(13)]
 assert out[198][9:12]==[37,97,84]
 return out

def campaign(b,cols,var,form):
 text=inspect.getsource(prior.campaign);anchor='    return dict(passed=True,native_run=False,mode=mode,variant=var,';assert text.count(anchor)==1
 text=text.replace(anchor,'    return q,main,dict(passed=True,native_run=False,mode=mode,variant=var,')
 text=text.replace("q.get('GameEngineSubroutine')==8,('No staged death/transition'","q.get('GameEngineSubroutine')in[4,8],('No staged death/transition'")
 env=dict(vars(prior));env['PLAN']=prior.PLAN[:11]if form==4 else prior.PLAN[:1];exec(compile(text,str(__file__)+'::earned_prefix','exec'),env)
 q,main,prefix=env['campaign'](b,0,var);assert q.get('M3Form')==form and prior.quiet(q)
 prior.arena(q,dict(kind='idle',form=form));q.put(Player_X_Position=28,Player_PageLoc=12,MmOldX=28,ScrollLock=1,ScreenLeft_X_Pos=228,ScreenLeft_PageLoc=11,ScreenRight_X_Pos=227,ScreenRight_PageLoc=12)
 for col in range(192,224):
  for row,value in enumerate(cols[col]):q.set('Block_Buffer_1',value,(col%32//16)*208+row*16+col%16)
 end=address(b,'E_GroundArea2')-1;q.put(EnemyDataLow=end&255,EnemyDataHigh=end>>8,EnemyDataOffset=0)
 rows=[];jumped=False;admission=None
 for tick in range(160):
  x=q.get('Player_X_Position')+256*q.get('Player_PageLoc');prev=q.get('M3Previous');bits=65
  if x>=3120:
   if not jumped and not prev&128:jumped=True;admission=dict(update=tick,x=x,y=q.get('Player_Y_Position'),previous=prev,form=q.get('M3Form'))
   if jumped:bits=193
  main(bits);z=dict(update=tick,buttons=bits,x=q.get('Player_X_Position')+256*q.get('Player_PageLoc'),y=q.get('Player_Y_Position'),state=q.get('Player_State'),vy=q.get('Player_Y_Speed'),engine=q.get('GameEngineSubroutine'),form=q.get('M3Form'),previous=q.get('M3Previous'));rows.append(z)
  assert q.get('M3Form')==form
  if z['engine']==4:break
 assert admission and not admission['previous']&128 and rows[-1]['engine']==4 and min(z['y']for z in rows)<160,('Actual jump/pole entry',admission,rows[-8:])
 return dict(variant=var,mode=0,form=form,earned_prefix_calls=prefix['complete_GameLoop_calls'],calls=len(rows),fresh_A=admission,actual_pole_entry=rows[-1],rows=rows)

def main():
 assert sha(ROM)==EXPECTED;b=scoped_load(ROM);cols=columns(b);cases=[campaign(b,cols,var,form)for form in[0,4]for var in[0,1]]
 parent=ROOT/'build/verification/compact-ee1152-mario3-easy-v2';rows=list(csv.DictReader((parent/'trace.csv').open()));tail=rows[-100:];assert all(int(r['x'])in[3153,3154]and r['engine']=='8'and r['mask']=='65'for r in tail)
 proof=ROOT/'build/current_smb3_pole_v3_source.json';assert not proof.exists();put(proof,dict(passed=True,native_run=False,Lua_VM_executed=False,ROM_sha256=EXPECTED,cases=cases,compiled_columns={str(k):v for k,v in cols.items()if 194<=k<=200},original_v2=dict(trace_sha256=sha(parent/'trace.csv'),result_sha256=sha(parent/'result.json'),last_100_state='3153/3154, engine8,Right+B65,noA'),scope='Actual complete Main+NMI after physically earnedSmall/Frog prefixes, typed initial player3100/Y176 and actual parser-produced cells/camera/no enemy stream. Fresh real A then actual native flagpole engine4 entry; not a native fullroute/lag/otherform proof.',bindings={str(p):sha(p)for p in[Path(__file__),POLICY,ROM,ROM.with_suffix('.dbg'),ROM.with_suffix('.lbl'),ROOT/'tools/playthroughs/current_roster_smb3_stair_v2.lua',ROOT/'tools/playthroughs/current_roster_chip_pickup_v2.lua',ROOT/'tools/audit/current_smb3_powerups_prepare_v1.py']}))
 outputs=[]
 for identity in['mario3','luigi3']:
  out=ROOT/('build/verification/compact-ee1152-'+identity+'-easy-v3');prepare(Namespace(identity=identity,mode='easy',rom=ROM,expected_sha256=EXPECTED,output=out,frames=8000,policy=POLICY,replay=None));rp=out/'ready.json';z=json.loads(rp.read_text());cmd=out/'command.json';put(cmd,z['command'])
  for p in[Path(__file__),POLICY,proof,ROOT/'tools/playthroughs/current_roster_smb3_stair_v2.lua',cmd]:z['bindings'][str(p.resolve())]=sha(p)
  z.update(native_run=False,input_only=True,source_proof_sha256=sha(proof),scope='Unchanged v2 stair logic and all original strict8000 route guards/container/caps. Only source-bound raised flagpole base approach with real A release and fresh A before sidewall; no state/resource/physics changes.');put(rp,z);assert all(sha(Path(p))==h for p,h in z['bindings'].items());outputs.append(dict(identity=identity,ready=str(rp),sha256=sha(rp),command=str(cmd),bindings=len(z['bindings'])))
 put(ROOT/'build/current_smb3_pole_v3_handoff.json',dict(native_run=False,proof=str(proof),proof_sha256=sha(proof),readies=outputs));print(json.dumps(outputs),flush=True)
if __name__=='__main__':main()
