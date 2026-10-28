"""Finite earned-Frog/cold-Small input-only final stair route preparation."""
from pathlib import Path
from argparse import Namespace
import csv,inspect,json
import current_smb3_powerups_prepare_v1 as prior
from current_darkwing_stairs_prepare_v1 import compiled_map
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
from current_roster_compact_11_v1 import ROOT,prepare,sha
ROM=ROOT/'build/roster-20261028-fixes.nes';EXPECTED='ee1152a49deae31e82d202159310fa3719cbcfd85de571fd1b9ac15a1cd2a7b3'
POLICY=ROOT/'tools/playthroughs/current_roster_smb3_stair_v2.lua'
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')

def campaign(b,cols,var,form):
 # Retain the actual original campaign's coldinit/RNG/pickup/rise/collection;
 # return its actual carried actor and Main+NMI caller after physical Frog4.
 text=inspect.getsource(prior.campaign);anchor='    return dict(passed=True,native_run=False,mode=mode,variant=var,'
 assert text.count(anchor)==1;text=text.replace(anchor,'    return q,main,dict(passed=True,native_run=False,mode=mode,variant=var,')
 env=dict(vars(prior));env['PLAN']=prior.PLAN[:11]if form==4 else prior.PLAN[:1];exec(compile(text,str(Path(__file__))+'::earned_original_prefix','exec'),env)
 q,main,prefix=env['campaign'](b,0,var);assert q.get('M3Form')==form and prior.quiet(q)and q.get(prior.N['XVel'])==0
 prior.arena(q,dict(kind='idle',form=form));q.put(Player_X_Position=24,Player_PageLoc=9,MmOldX=24,ScrollLock=1)
 for col in range(128,160):
  for row,value in enumerate(cols[col]):q.set('Block_Buffer_1',value,(col%32//16)*208+row*16+col%16)
 end=address(b,'E_GroundArea2')-1;q.put(EnemyDataLow=end&255,EnemyDataHigh=end>>8,EnemyDataOffset=0)
 phase='approach';jump_age=-1;last_buttons=0;rows=[];landing=None;takeoff=None
 for tick in range(360):
  x=q.get('Player_X_Position')+256*q.get('Player_PageLoc');y=q.get('Player_Y_Position');ground=q.get('Player_State')==0;prev=q.get('M3Previous');vx=q.get('Player_X_Speed')
  bits=65
  if phase=='approach'and x>=2406 and y<=112:phase='land'
  if phase=='approach':
   if last_buttons&128:jump_age+=1
   elif ground:jump_age=-1
   obstacle=any(cols[(x+42)//16][(y+dy-32)//16]not in[0,35,38,194,195]for dy in[8,24]if 32<=y+dy<240)
   if ground and not last_buttons&128 and obstacle:bits=193;jump_age=0
   elif not ground and jump_age>=0 and jump_age<35:bits=193
  elif phase=='land':
   bits=2 if x>2424 else 1 if x<2418 else 2 if 0<vx<128 else 1 if vx>=128 else 0
   if ground and y+32<=144 and not prev&128:landing=dict(update=tick,x=x,y=y,vx=vx,previous=prev);phase='runup';bits=65
  elif phase=='runup':
   if ground and x>=2430 and not prev&128:takeoff=dict(update=tick,x=x,y=y,vx=vx,previous=prev);phase='cross';bits=193
  elif phase=='cross':
   bits=193
   if ground and x>=2472:phase='out'
  cam=max(2208,x-112);q.put(ScreenLeft_X_Pos=cam&255,ScreenLeft_PageLoc=cam>>8,ScreenRight_X_Pos=(cam+255)&255,ScreenRight_PageLoc=(cam+255)>>8)
  main(bits);last_buttons=bits;rows.append(dict(update=tick,phase=phase,x=q.get('Player_X_Position')+256*q.get('Player_PageLoc'),y=q.get('Player_Y_Position'),state=q.get('Player_State'),vx=q.get('Player_X_Speed'),vy=q.get('Player_Y_Speed'),form=q.get('M3Form'),previous=q.get('M3Previous'),buttons=bits))
  assert q.get('M3Form')==form and q.get('NumberofLives')==0
  if rows[-1]['x']>=2544 and q.get('Player_State')==0:break
 assert landing and takeoff and rows[-1]['x']>=2544,('Earned source stair crossing',form,var,landing,takeoff,rows[-8:])
 assert landing['y']==takeoff['y']==112 and landing['x']<=2436 and 2430<=takeoff['x']<=2434 and not takeoff['previous']&128
 return dict(mode=0,variant=var,form=form,earned_prefix=prefix,calls=len(rows),landing=landing,takeoff=takeoff,rows=rows)

def main():
 assert sha(ROM)==EXPECTED;b=scoped_load(ROM);cols=compiled_map(b);source=[]
 try:
  for form in[0,4]:
   for var in[0,1]:
    z=campaign(b,cols,var,form);source.append(z);print(json.dumps(dict(source_PASS=True,form=form,variant=var,calls=z['calls'],landing=z['landing'],takeoff=z['takeoff'])),flush=True)
 except Exception as e:
  negative=ROOT/'build/current_smb3_stair_v2_trial_negative.json';assert not negative.exists();put(negative,dict(passed=False,native_run=False,error=repr(e),completed=source));raise
 original=ROOT/'build/verification/compact-ee1152-mario3-easy-v1';rows=list(csv.DictReader((original/'trace.csv').open()));r=lambda frame:next(x for x in rows if int(x['frame'])==frame)
 assert(r(1689)['x'],r(1689)['y'],r(1690)['mask'])==('2328','176','193')and(r(1736)['x'],r(1736)['y'])==('2446','114')
 proof=ROOT/'build/current_smb3_stair_v2_source.json';assert not proof.exists();put(proof,dict(passed=True,native_run=False,Lua_VM_executed=False,ROM_sha256=EXPECTED,cases=source,
  scope='Fresh original complete Main+NMI source prefixes retain actual coldSmall0 or physically earned Frog4; no acquired form/RNG/private physics/resources/outcomes seeded. Then typed neutral external pose2328/176, actual parser-produced native1-1 cells and empty enemy stream, input-only plus following camera. One source poll/Main is not native polling or exact unlogged RAM reconstruction. Other forms keep original policy; all strict native guards/caps remain.',
  preserved_native_FALSE=dict(result_sha256=sha(original/'result.json'),last_actual_floor=r(1689),old_jump=r(1690),past_last_top=r(1736),terminal=r(1768),M3Form_limit='Native baseline CSV has PlayerStatus but no M3Form; Root identified Frog separately. This proof does not invent a serialized native form readback. New controller logs actual M3Form0/4 admission.'),
  bindings={str(p):sha(p)for p in[Path(__file__),POLICY,ROM,ROM.with_suffix('.dbg'),ROM.with_suffix('.lbl'),ROOT/'tools/audit/current_smb3_powerups_prepare_v1.py',ROOT/'tools/audit/current_darkwing_stairs_prepare_v1.py',ROOT/'tools/audit/link_pit_rygar_sophia_audit_cpu.py',ROOT/'tools/audit/check_tmnt_render_oa.py',ROOT/'tools/audit/verify_native_relocation.py',original/'result.json',original/'trace.csv',original/'inputs.csv']}))
 outputs=[]
 for identity in['mario3','luigi3']:
  out=ROOT/('build/verification/compact-ee1152-'+identity+'-easy-v2');prepare(Namespace(identity=identity,mode='easy',rom=ROM,expected_sha256=EXPECTED,output=out,frames=8000,policy=POLICY,replay=None))
  rp=out/'ready.json';z=json.loads(rp.read_text());cmd=out/'command.json';put(cmd,z['command'])
  for p in[Path(__file__),POLICY,proof,original/'result.json',original/'trace.csv',cmd]:z['bindings'][str(p.resolve())]=sha(p)
  z.update(native_run=False,input_only=True,original_mario_v1_FALSE_preserved=True,new_source_proof_sha256=sha(proof),scope='Same strict full1-1 to controlled1-2; only final native61 top landing/opposite-direction brake and freshA late-edge runup on supported Small/Frog forms. No game/default/settings/guards/caps changed. Source outcomes are not native clear claims.');put(rp,z);assert all(sha(Path(p))==h for p,h in z['bindings'].items());outputs.append(dict(identity=identity,ready=str(rp),sha256=sha(rp),bindings=len(z['bindings']),command=str(cmd)))
 put(ROOT/'build/current_smb3_stair_v2_handoff.json',dict(native_run=False,source_proof=str(proof),source_sha256=sha(proof),readies=outputs,owned_files=[str(Path(__file__)),str(POLICY)]));print(json.dumps(outputs),flush=True)

if __name__=='__main__':main()
