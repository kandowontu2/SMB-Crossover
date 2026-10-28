"""Source-only consumed-facing/brake successor; preserves every v3 negative."""
from pathlib import Path
import csv,hashlib,inspect,json,re,sys
R=Path(__file__).resolve().parents[2];B=R/'build';sys.path.insert(0,str(R/'tools/audit'))
import current_smb3_powerups_prepare_v1 as prior
from link_pit_rygar_sophia_audit_cpu import scoped_load
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')
SOURCE_OLD="""                elif kind in ['shot','tail','tailblock']:
                    button=(2 if task.get('face',1)==2 else 1)if 4<=age<8 else 64 if 8<=age<12 else 0"""
SOURCE_NEW="""                elif kind=='shot'and task['form']==6:
                    direction=task.get('face',1);flip=0 if direction==2 else 64
                    phase=rec.setdefault('hammer_phase','aim')
                    if age>=4:
                        if phase=='aim':
                            if q.get('PlayerFacingDir')==direction and q.get(N['FlipBits'])&64==flip:
                                phase=rec['hammer_phase']='brake'
                            else:button=direction
                        if phase=='brake'and q.get('Player_X_Speed')==0 and q.get(N['XVel'])==0 and not q.get('M3Previous')&64:
                            phase=rec['hammer_phase']='press'
                            rec['hammer_launch_admission']=dict(age=age,face=q.get('PlayerFacingDir'),flip=q.get(N['FlipBits']),VX=q.get('Player_X_Speed'),nativeVX=q.get(N['XVel']),previous=q.get('M3Previous'),x=q.get('Player_X_Position'),enemyX=q.get('Enemy_X_Position',0),enemyY=q.get('Enemy_Y_Position',0))
                        if phase=='press':
                            if any(q.get('M3ShotKind',i)>0 for i in range(2)):rec['hammer_phase']='done'
                            else:button=64
                elif kind in ['shot','tail','tailblock']:
                    button=(2 if task.get('face',1)==2 else 1)if 4<=age<8 else 64 if 8<=age<12 else 0"""
LUA_OLD="""  elseif phase=='shot'or phase=='tail'or phase=='tailblock'then if age>=3 and age<7 then if t.face==2 then b.left=true else b.right=true end end;b.b=age>=7 and age<11"""
LUA_NEW="""  elseif phase=='shot'and t.form==6 then
   local direction=t.face or 1;local flip=direction==2 and 0 or 64
   rec.hammer_phase=rec.hammer_phase or'aim'
   if age>=3 then
    if rec.hammer_phase=='aim'then
     if r('PlayerFacingDir')==direction and(nr('FlipBits')&64)==flip then rec.hammer_phase='brake'
     elseif direction==2 then b.left=true else b.right=true end
    end
    if rec.hammer_phase=='brake'and r('Player_X_Speed')==0 and nr('XVel')==0 and(r('M3Previous')&64)==0 then
     rec.hammer_phase='press';rec.hammer_launch_admission={age=age,face=r('PlayerFacingDir'),flip=nr('FlipBits'),VX=r('Player_X_Speed'),nativeVX=nr('XVel'),previous=r('M3Previous'),x=r('Player_X_Position'),enemyX=r('Enemy_X_Position',0),enemyY=r('Enemy_Y_Position',0)}
    end
    if rec.hammer_phase=='press'then
     if r('M3ShotKind',0)>0 or r('M3ShotKind',1)>0 then rec.hammer_phase='done'else b.b=true end
    end
   end
  elseif phase=='shot'or phase=='tail'or phase=='tailblock'then if age>=3 and age<7 then if t.face==2 then b.left=true else b.right=true end end;b.b=age>=7 and age<11"""

def main():
 old=R/'tests/current-smb3-powerups-v3.lua';new=R/'tests/current-smb3-powerups-v4.lua'
 original=old.read_text();assert original.count(LUA_OLD)==1 and not new.exists()
 altered=original.replace(LUA_OLD,LUA_NEW);assert altered.replace(LUA_NEW,LUA_OLD)==original
 # These diagnostic fields are actual callback/readback values, not a modeled
 # native trajectory or arbitrary baseline/resource refresh.
 event_old="r('NumberofLives'),value or 0},',')"
 event_new="r('NumberofLives'),value or 0,nr('FlipBits'),nr('XVel'),r('Enemy_X_Position',0),r('Enemy_PageLoc',0),r('Enemy_Y_Position',0),r('Enemy_State',0),r('Enemy_Flag',0),r('M3ShotX',1),r('M3ShotPage',1),r('M3ShotY',1),r('M3ShotVX',1),r('M3ShotVY',1),r('M3ShotAge',1)},',')"
 assert altered.count(event_old)==1;altered=altered.replace(event_old,event_new)
 header='shot0,shot1,star,lives,value\\n';headnew='shot0,shot1,star,lives,value,flip,native_vx,enemy_x,enemy_page,enemy_y,enemy_state,enemy_flag,shot_x,shot_page,shot_y,shot_vx,shot_vy,shot_age\\n'
 assert altered.count(header)==1;altered=altered.replace(header,headnew)
 reverted=altered.replace(headnew,header).replace(event_new,event_old).replace(LUA_NEW,LUA_OLD);assert reverted==original
 new.write_text(altered,newline='\n')
 rom=B/'current_smb3_timer.nes';assert sha(rom)=='b01dcf080e07f5c7526fbf5ed177fe2131c6d5fcbbab5eed8773a66f6a34171d'
 b=scoped_load(rom);source=inspect.getsource(prior.campaign);assert source.count(SOURCE_OLD)==1
 updated=source.replace(SOURCE_OLD,SOURCE_NEW);assert updated.replace(SOURCE_NEW,SOURCE_OLD)==source
 env=dict(vars(prior));exec(compile(updated,str(Path(__file__))+'::reviewed_source_mirror','exec'),env)
 records=[]
 for mode in [0,1]:
  for variant in [0,1]:
   z=env['campaign'](b,mode,variant);records.append(z)
   print(json.dumps(dict(source_PASS=True,mode=mode,variant=variant,calls=z['complete_GameLoop_calls'])),flush=True)
 rows=list(csv.DictReader((B/'current-smb3-timer-mario3-hard-items-v3/native/components.csv').open()))
 bad=[r for r in rows if r['case']=='20'];alloc=next(r for r in bad if int(r['shot1'])==2)
 assert alloc['update']=='2248'and alloc['age']=='8'and not any(r['event']in['actual-source-Defeat','actual-source-ProjectileDamage','case-complete']for r in bad)
 proof=dict(passed=True,source_CPU_only=True,native_run=False,Lua_VM_executed=False,ROM_sha256=sha(rom),
  original_v3_FALSE=dict(first_observed_Hammer=dict(alloc),last_completed=dict(bad[-1]),missing_outcome='No observed required target damage/defeat; real Hammer DID allocate.',unlogged='Native v3 lacks actual target/shot coordinates, velocities and consumed native FlipBits. Exact native first trajectory miss is not reconstructible; no product-fault claim.'),
  change='Hammer-only real consumed facing then genuine zero native+exported horizontal velocity/B release before one real B press. Existing allocation/defeat/cleanup/1100-case and global guards/caps unchanged. Diagnostic CSV adds real source values; no resource/physics/outcome writes.',
  source_records=records,complete_GameLoop_calls=sum(z['complete_GameLoop_calls']for z in records),
  exact_controller_and_diagnostic_reverse_normalization=True,source_controller_mirror='Same ordered predicates; source first case age1 versus native setup age0/input next-update offset is explicitly retained.',
  bindings={str(p):sha(p)for p in[Path(__file__),old,new,rom,rom.with_suffix('.dbg'),rom.with_suffix('.lbl'),R/'tools/audit/current_smb3_powerups_prepare_v1.py',B/'current-smb3-timer-mario3-hard-items-v3/native/components.csv']})
 sourcefile=B/'current_smb3_hammer_aim_v4_source.json';assert not sourcefile.exists();put(sourcefile,proof)
 outputs=[]
 for identity in ['mario3','luigi3']:
  parent=B/('current-smb3-timer-'+identity+'-hard-items-v3');rp=parent/'prepared-not-run.json';z=json.loads(rp.read_text())
  for f in z['bindings']:assert sha(Path(f['path']))==f['sha256'],f['path']
  out=B/('current-smb3-timer-'+identity+'-hard-items-v4');assert not out.exists();out.mkdir()
  cfg=json.loads((parent/'config.json').read_text());ram=cfg['ram']
  names=set(re.findall(r"(?<![A-Za-z_])[rw]\('([A-Za-z_][A-Za-z_0-9:]*)'",altered))|set(re.findall(r'\bC\.ram\.([A-Za-z_][A-Za-z_0-9]*)',altered))
  for n in names:ram[n]=prior.address(b,n)
  assert all(isinstance(v,int)for v in ram.values());put(out/'config.json',cfg)
  # Preserve original config serialization semantics; only genuine RAM metadata
  # additions and output path/current fixture differ in the new coordinator.
  run=(parent/'run.lua').read_text();match=re.search(r'CURRENT_SMB3_POWERUPS=(\{.*\})\n',run)
  assert match;oldcfg=run[match.start(1):match.end(1)];run=run[:match.start(1)]+prior.lua(cfg)+run[match.end(1):]
  assert run.count(old.as_posix())==1;run=run.replace(old.as_posix(),new.as_posix());assert not re.search(r'\\u[0-9a-fA-F]{4}',run)
  (out/'run.lua').write_text(run,newline='\n');put(out/'source-controls.json',dict(passed=True,source_CPU_only=True,native_run=False,actual_new_source_proof=str(sourcefile),sha256=sha(sourcefile),cases=24,modes=[0,1],variants=[0,1],full_Main_calls=proof['complete_GameLoop_calls']))
  cmd=json.loads((parent/'command.json').read_text());cmd['argv']=[str(out/'native')if s==str(parent/'native')else str(out/'run.lua')if s==str(parent/'run.lua')else s for s in cmd['argv']];put(out/'command.json',cmd)
  paths={Path(f['path'])for f in z['bindings']if Path(f['path'])not in{old,parent/'run.lua',parent/'config.json',parent/'source-controls.json',parent/'command.json'}}
  paths|={old,new,Path(__file__),rp,parent/'run.lua',parent/'config.json',parent/'source-controls.json',parent/'command.json',sourcefile};paths|={out/n for n in['run.lua','config.json','source-controls.json','command.json']}
  z.update(status='PREPARED_DO_NOT_RUN',passed=False,native_run=False,parent_readiness_sha256=sha(rp),change=proof['change'],bindings=[dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))for p in sorted(paths)])
  put(out/'prepared-not-run.json',z);outputs.append(dict(identity=identity,ready=str(out/'prepared-not-run.json'),sha256=sha(out/'prepared-not-run.json'),bindings=len(paths),command=str(out/'command.json')))
 put(B/'current_smb3_hammer_aim_v4_handoff.json',dict(native_run=False,game_change=False,original_v3_preserved=True,source_proof=str(sourcefile),source_sha256=sha(sourcefile),readies=outputs,owned_files=[str(Path(__file__)),str(new)]));print(json.dumps(outputs),flush=True)

if __name__=='__main__':main()
