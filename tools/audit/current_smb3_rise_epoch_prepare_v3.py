"""Additive inclusive-Main rise epoch correction; no native/game mutations."""
from pathlib import Path
import csv,hashlib,json,re
R=Path(__file__).resolve().parents[2];B=R/'build'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')
PARENTS={'mario3':'e1f5578d513084b4ebb778460493d406dc66679e9a8a3df9ede8a382eb46f9e9','luigi3':'fff9b135e822298e6228ca21d1d19ef8027e7b1f3e8212f8869191f7b4553332'}

def main():
 old=R/'tests/current-smb3-powerups-v2.lua';new=R/'tests/current-smb3-powerups-v3.lua';text=old.read_text();assert not new.exists()
 substitutions=[('age=0,collect=0,form_before=', 'age=0,collect=0,started_main=updates,form_before='),
  ("assert(age>=48 and rec.collect==0,'No pickup during original48-update emergence');rec.collect=rec.collect+1;rec.collected_at=age;", "assert(updates-rec.started_main+1>=48 and rec.collect==0,'No pickup during original48-update emergence');rec.rise_Main_calls=updates-rec.started_main+1;rec.collect=rec.collect+1;rec.collected_at=age;")]
 altered=text
 for a,z in substitutions:assert altered.count(a)==1;altered=altered.replace(a,z)
 reversed_text=altered
 for a,z in reversed(substitutions):reversed_text=reversed_text.replace(z,a)
 assert reversed_text==text;new.write_text(altered,newline='\n')
 source=json.loads((B/'current_smb3_source_controls.json').read_text());assert source['passed']
 source_first=[r['records'][1]['collected_at']for r in source['records']];assert source_first==[48]*4
 original=B/'current-smb3-timer-mario3-hard-items-v2';rows=list(csv.DictReader((original/'native/components.csv').open()))
 start=next(r for r in rows if r['event']=='case-start'and r['case']=='2');last=rows[-1]
 assert int(start['update'])==91 and int(start['age'])==0 and int(last['update'])==137 and int(last['age'])==46
 # The failing callback was the subsequent GameLoop, after the original
 # maturity/owner/stamp assertions passed. No unrecorded stack is inferred.
 assert 138-91+1==48 and 47==138-91
 epoch=dict(passed=True,native_run=False,source_first_collection_Main_call_counts=source_first,native_case_start_update=91,native_initial_age=0,last_completed_update=137,last_completed_age=46,source_derived_next_callback_update=138,source_derived_next_callback_inclusive_Main_count=48,
  scope='Native failed callback update is derived from the exact control flow and preceding CSV, not a separately serialized native stack/timestamp. GameLoop+5 setup participates in that same first update. Mature state/owner/stamp assertions passed before the old age-only oracle failed.',strict_48_Main_requirement_retained=True,all_controller_inputs_game_hardware_caps_unchanged=True,exact_two_span_reverse_normalization=True)
 outputs=[]
 for identity,expected in PARENTS.items():
  parent=B/('current-smb3-timer-'+identity+'-hard-items-v2');ready=parent/'prepared-not-run.json';assert sha(ready)==expected;z=json.loads(ready.read_text())
  for o in z['bindings']:
   p=Path(o['path']);assert p.is_file()and sha(p)==o['sha256']and p.stat().st_size==o['bytes'],p
  out=B/('current-smb3-timer-'+identity+'-hard-items-v3');assert not out.exists();out.mkdir()
  put(out/'config.json',json.loads((parent/'config.json').read_text()));v=json.loads((parent/'source-controls.json').read_text());v['rise_epoch_only_successor']=dict(epoch,original_fixture_sha256=sha(old),corrected_fixture_sha256=sha(new),source_CPU_result_inherited_unchanged=True,Lua_VM_executed=False,native_result_inherited=False);put(out/'source-controls.json',v)
  run=(parent/'run.lua').read_text();assert run.count(old.as_posix())==1;run=run.replace(old.as_posix(),new.as_posix());assert run.replace(new.as_posix(),old.as_posix())==(parent/'run.lua').read_text()and not re.search(r'\\u[0-9a-fA-F]{4}',run);(out/'run.lua').write_text(run,newline='\n')
  cmd=json.loads((parent/'command.json').read_text());cmd['argv']=[str(out/'native')if s==str(parent/'native')else str(out/'run.lua')if s==str(parent/'run.lua')else s for s in cmd['argv']];put(out/'command.json',cmd);put(out/'epoch-controls.json',epoch)
  paths={Path(o['path'])for o in z['bindings']if Path(o['path'])not in{old,parent/'run.lua',parent/'config.json',parent/'source-controls.json',parent/'command.json'}}
  paths|={old,new,Path(__file__),ready,parent/'run.lua',parent/'config.json',parent/'source-controls.json',parent/'command.json',original/'launch.json',original/'native/components.csv'};paths|=set((original/'native').glob('*.log'));paths|={out/n for n in['run.lua','config.json','source-controls.json','command.json','epoch-controls.json']}
  z.update(status='PREPARED_DO_NOT_RUN',passed=False,native_run=False,goal_complete=False,parent_readiness_sha256=expected,change='Observe inclusive actual Main count since setup for the same strict48-update emergence; only two fixture spans and coordinator output paths change.',bindings=[dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))for p in sorted(paths)]);put(out/'prepared-not-run.json',z);outputs.append(dict(identity=identity,ready=str(out/'prepared-not-run.json'),sha256=sha(out/'prepared-not-run.json'),bindings=len(paths),command=str(out/'command.json')))
 put(B/'current_smb3_rise_epoch_v3_handoff.json',dict(native_run=False,game_change=False,originals_preserved=True,readies=outputs,epoch=epoch,owned_files=[str(Path(__file__)),str(new)]));print(json.dumps(outputs))

if __name__=='__main__':main()
