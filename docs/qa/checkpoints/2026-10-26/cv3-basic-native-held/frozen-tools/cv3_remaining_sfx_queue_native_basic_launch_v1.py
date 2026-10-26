"""Exactly13 granted frozen baseline/candidate pairs, sequential, no retry/settings writes."""
from pathlib import Path
import argparse,datetime,hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
READY='2cc9dc9d2aab9759e5d6223fb969bf9d5bc40114dc50cb6981ac4eeb6e319b00'
ENV='357104cb1bdb76ba3e5154a31917cba3c4ca58a3172d71c1b8a114166d15e4be'
SETTINGS='8a439e0a5eeddc2d4776e516aacfc224c03048b9c7d23d9926a463460a7e748a'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--readiness',type=Path,required=True);p.add_argument('--environment',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert sha(a.readiness)==READY and sha(a.environment)==ENV;r=json.loads(a.readiness.read_text());e=json.loads(a.environment.read_text());a.output.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,a.output/'frozen-launcher.py');settings=Path('C:/Mesen2/settings.json');rows=[];launch_count=0
 def preflight():
  assert sha(settings)==SETTINGS,'SHARED_ENVIRONMENT_DRIFT: no launch permitted';assert sha(a.environment)==ENV and sha(a.readiness)==READY
  for q in e['unchanged_binding_checks']:assert sha(q['path'])==q['sha256'],('SHARED_FROZEN_INPUT_DRIFT',q['path'])
  assert sha(e['current_settings']['path'])==SETTINGS
  s=json.loads(settings.read_text(encoding='utf-8-sig'));assert s['Nes']['RemoveSpriteLimit']is False and s['Nes']['AdaptiveSpriteLimit']is False and s['Emulation']['RunAheadFrames']==0
 def save(stopped=False,reason=None):
  result=dict(completed=not stopped,native_executed=launch_count>0,native_launches=launch_count,retries=0,accepted=False,worker_released=True,early_stop=stopped,stop_reason=reason,readiness_sha256=READY,environment_sha256=ENV,settings_sha256=SETTINGS,cells=rows,tool_sha256=sha(__file__))
  (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n')
 preflight()
 for cell in r['future_cells']:
  name=cell['name'];record=dict(name=name,event=cell['event'],cold_numeric_mode=cell['cold_numeric_mode'],launches={});rows.append(record)
  for version in['baseline','candidate']:
   preflight();c=cell[version];command=c['future_separately_granted_command'];fixture=Path(command[command.index('--output')+1]);assert not(fixture/'proof.json').exists(),'No retry: native proof already exists';assert sha(fixture/'run.lua')==c['script']['sha256']and sha(c['ROM']['path'])==c['ROM']['sha256'];out=a.output/(name+'-'+version);out.mkdir();before=sha(settings);start=utc();launch=dict(start_UTC=start,command=command,settings_before_sha256=before,script_sha256=sha(fixture/'run.lua'),ROM_sha256=sha(c['ROM']['path']),readiness_sha256=READY,environment_sha256=ENV,launcher_sha256=sha(__file__),retries=0);(out/'launch.json').write_text(json.dumps(launch,indent=2)+'\n');launch_count+=1
   z=subprocess.run(command,cwd=ROOT,capture_output=True,text=True);(out/'host.stdout.txt').write_text(z.stdout);(out/'host.stderr.txt').write_text(z.stderr);launch.update(end_UTC=utc(),exit_code=z.returncode,settings_after_sha256=sha(settings),native_guard_passed=False)
   if sha(settings)!=before:
    launch['shared_environment_failure']=True;(out/'proof.json').write_text(json.dumps(launch,indent=2)+'\n');record['launches'][version]=dict(path=str(out/'proof.json'),sha256=sha(out/'proof.json'));save(True,'Shared settings drift after run; remaining launches cancelled');raise SystemExit(2)
   if z.returncode:
    # Host/observer assertions are not retried. Freeze the result and stop so
    # a human reviewer can classify before any independent pair continues.
    launch['failure_scope_unclassified']=True;(out/'proof.json').write_text(json.dumps(launch,indent=2)+'\n');record['launches'][version]=dict(path=str(out/'proof.json'),sha256=sha(out/'proof.json'));save(True,'Host/native assertion failure requires invariant classification; no retry');print(json.dumps(dict(name=name,version=version,stopped=True,exit=z.returncode)),flush=True);raise SystemExit(1)
   game=json.loads((fixture/'proof.json').read_text());assert game['passed']and game['updates']==140 and game['cases'][0]['modeReadback']==cell['cold_numeric_mode'];launch.update(native_guard_passed=True,complete_GAMEproof=dict(path=str(fixture/'proof.json'),sha256=sha(fixture/'proof.json')));(out/'proof.json').write_text(json.dumps(launch,indent=2)+'\n');record['launches'][version]=dict(path=str(out/'proof.json'),sha256=sha(out/'proof.json'),updates=game['updates'],draws=game['draws'],strict_completed_DMA=game['strict_completed_DMA']);print(json.dumps(dict(name=name,version=version,native_guard_passed=True,draws=game['draws'],launch_number=launch_count)),flush=True)
  compare=a.output/(name+'-comparison');cmd=[sys.executable,r['future_native_validator'],'--fixture',str(Path(cell['candidate']['script']['path']).parent),'--baseline',str(Path(cell['baseline']['script']['path']).parent),'--output',str(compare)];z=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True);(a.output/(name+'-verify.stdout.txt')).write_text(z.stdout);(a.output/(name+'-verify.stderr.txt')).write_text(z.stderr)
  if z.returncode:
   record['comparison_failure']=dict(exit_code=z.returncode,stdout_sha256=sha(a.output/(name+'-verify.stdout.txt')),stderr_sha256=sha(a.output/(name+'-verify.stderr.txt')));save(True,'Source/hardware comparison failure requires invariant classification; no retry');print(json.dumps(dict(name=name,source_or_hardware_comparison_failed=True,stopped=True)),flush=True);raise SystemExit(1)
  verdict=json.loads((compare/'proof.json').read_text());record['comparison']=dict(path=str(compare/'proof.json'),sha256=sha(compare/'proof.json'),passed=verdict['passed'],status=verdict['status']);save();print(json.dumps(dict(name=name,source_and_hardware_passed=True,strict_cadence_passed=verdict['passed'])),flush=True)
 assert launch_count==26;save();print(json.dumps(dict(completed=True,native_launches=26,retries=0,accepted=False,worker_released=True,cadence_passes=sum(row['comparison']['passed']for row in rows)),indent=2))
if __name__=='__main__':main()
