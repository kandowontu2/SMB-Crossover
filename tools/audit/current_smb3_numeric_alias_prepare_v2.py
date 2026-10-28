"""Additive numeric-alias-only SMB3 fixture successor; never launches Mesen."""
from pathlib import Path
import hashlib,json,re,sys
R=Path(__file__).resolve().parents[2];B=R/'build'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')
PARENT_READY={'mario3':'cdfc090d068fe9bc767c2a5f8687d7492afb87534665f0f1900f5a76b2ac2e0d','luigi3':'f76dcaf94ba6e53bc0a7157c96764db0c7a61b904455f2d58004e60da63fc579'}

def main():
 old=R/'tests/current-smb3-powerups.lua';new=R/'tests/current-smb3-powerups-v2.lua'
 before="local function nr(n)return r(assert(C.native[n],n))end"
 after="local function nr(n)local name=assert(C.native[n],n);return r(name)end"
 text=old.read_text();assert text.count(before)==1 and not new.exists();new.write_text(text.replace(before,after),newline='\n')
 assert new.read_text().replace(after,before)==text,'Exact one-line reverse normalization'
 marker='-- All callback registration is startup-static.';end="hook('DmaComplete',function()\n if not imagePending"
 assert text[text.index(marker):text.index(end)]==new.read_text()[new.read_text().index(marker):new.read_text().index(end)]
 outputs=[]
 for identity,expected in PARENT_READY.items():
  parent=B/('current-smb3-timer-'+identity+'-hard-items-v1');ready=parent/'prepared-not-run.json';assert sha(ready)==expected
  z=json.loads(ready.read_text())
  for record in z['bindings']:
   p=Path(record['path']);assert p.is_file()and sha(p)==record['sha256']and p.stat().st_size==record['bytes'],p
  cfg=json.loads((parent/'config.json').read_text());aliases=cfg['native'];assert aliases
  # Lua assert returns every argument. The old final-position call supplied
  # (name,error_message) as r(name,index), hence the actual string addition.
  # A local assignment takes the first result before calling r(name).
  controls=[]
  for key,name in aliases.items():
   assert isinstance(name,str)and isinstance(cfg['ram'][name],int)
   controls.append(dict(key=key,source_name=name,address=cfg['ram'][name],old_extra_index=key,corrected_index=0))
  out=B/('current-smb3-timer-'+identity+'-hard-items-v2');assert not out.exists();out.mkdir()
  put(out/'config.json',cfg)
  source=json.loads((parent/'source-controls.json').read_text());source['additive_fixture_successor']=dict(original_fixture_sha256=sha(old),corrected_fixture_sha256=sha(new),exact_one_line_reverse=True,source_CPU_evidence_inherited_unchanged=True,Lua_VM_executed=False,native_outcome_inherited=False)
  put(out/'source-controls.json',source)
  run=(parent/'run.lua').read_text();assert run.count(old.as_posix())==1;run=run.replace(old.as_posix(),new.as_posix());assert run.replace(new.as_posix(),old.as_posix())==(parent/'run.lua').read_text();assert not re.search(r'\\u[0-9a-fA-F]{4}',run)
  (out/'run.lua').write_text(run,newline='\n')
  cmd=json.loads((parent/'command.json').read_text());cmd['argv']=[str(out/'native')if s==str(parent/'native')else str(out/'run.lua')if s==str(parent/'run.lua')else s for s in cmd['argv']]
  put(out/'command.json',cmd)
  paths={Path(x['path'])for x in z['bindings']if Path(x['path'])not in{old,parent/'run.lua',parent/'config.json',parent/'source-controls.json',parent/'command.json'}}
  paths|={new,old,Path(__file__),ready,parent/'run.lua',parent/'config.json',parent/'source-controls.json',parent/'command.json'}
  paths|={out/n for n in['run.lua','config.json','source-controls.json','command.json']}
  if identity=='mario3':
   paths|={parent/'launch.json',parent/'native/components.csv'};paths|=set((parent/'native').glob('*.log'))
  put(out/'alias-controls.json',dict(passed=True,native_run=False,Lua_VM_executed=False,scope='Source-level Lua multiple-result/assignment contract and actual numeric alias metadata; no substitute for native fixture execution.',aliases=controls,reverse_normalization_exact=True,strict_guard_byte_exact=True,ROM_controller_plan_setup_resources_hardware_guard_caps_unchanged=True,original_negative='Actual Mario v1 helper exception; zero completed components. Luigi v1 remains native-unrun.'))
  paths.add(out/'alias-controls.json')
  z.update(status='PREPARED_DO_NOT_RUN',native_run=False,passed=False,goal_complete=False,parent_readiness_sha256=expected,change='One local assignment prevents assert error-message becoming r index; other fixture bytes identical. Output paths only in coordinator; identical ROM/config/plan/guards/caps.',bindings=[dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))for p in sorted(paths)])
  put(out/'prepared-not-run.json',z);outputs.append(dict(identity=identity,ready=str(out/'prepared-not-run.json'),sha256=sha(out/'prepared-not-run.json'),bindings=len(paths),command=str(out/'command.json')))
 put(B/'current_smb3_numeric_alias_v2_handoff.json',dict(native_run=False,source_game_change=False,old_fixture_sha256=sha(old),new_fixture_sha256=sha(new),exact_one_line_reverse=True,original_negative_preserved=True,readies=outputs,owned_files=[str(Path(__file__)),str(new)]))
 print(json.dumps(outputs))

if __name__=='__main__':main()
