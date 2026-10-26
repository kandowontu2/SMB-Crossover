"""Source/CPU/Lua qualification of13 remaining prepared BASIC cells, never native."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepared',type=Path,required=True);p.add_argument('--lua-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);rows=[]
 for mode in[0,1]:
  for label,event in[('dagger',0x13),('axe',0x15),('flame',0x24),('ice',0x21),('lightning',0x1e),('fireball',0x1f),('bat',0x2f)]:
   if mode==0 and event==0x1e:continue
   name=('hard-'if mode else'easy-')+label;fixture=a.prepared/name;cfg=json.loads((fixture/'configuration.json').read_text());assert cfg['mode']==mode and cfg['cases'][0]['event']==event;cp=a.output/(name+'-cpu');st=a.output/(name+'-startup')
   for tool,dest in[('cv3_remaining_sfx_queue_native_cpu_v4.py',cp),('cv3_remaining_sfx_queue_native_startup_v2.py',st)]:
    cmd=[sys.executable,str(ROOT/'tools/audit'/tool),'--fixture',str(fixture),'--lua-root',str(a.lua_root),'--output',str(dest)];r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True);(a.output/(name+'-'+tool+'.log')).write_text(r.stdout+r.stderr);assert not r.returncode,(name,tool,r.stderr)
   c=json.loads((cp/'proof.json').read_text());s=json.loads((st/'proof.json').read_text());assert c['passed']and s['passed']and c['native_executed']is False and s['native_executed']is False and c['actual_numeric_mode']==s['actual_numeric_mode_configuration']==mode;rows.append(dict(name=name,event=event,mode=mode,script_sha256=sha(fixture/'run.lua'),cpu=dict(path=str(cp/'proof.json'),sha256=sha(cp/'proof.json')),startup=dict(path=str(st/'proof.json'),sha256=sha(st/'proof.json')),new_effect_original_ordered_image_equal=c['new_effect_original_ordered_image_equal'],legacy1F_declared_unchanged_adapter_order=c['legacy1F_declared_unchanged_adapter_order']));(a.output/'progress.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(dict(name=name,passed=True,native_executed=False)),flush=True)
 result=dict(passed=True,native_executed=False,cells=rows,real_assembled_producer_consumer_cases=3*len(rows),complete_startup_cases=len(rows),scope='Thirteen remaining BASIC effect/mode cells only. Each actual assembled ability release and fullNMI ISR replayed into real read-only Lua hooks at no/before-head/after-head interference, plus full inactive439-frame startup. Existing1F retains declared adapter image order; every other effect matches ordered original source. No Mesen,140-update gameplay run, native timing, adoption or lifecycle/priority/pressure qualification.',tool_sha256=sha(__file__))
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,native_executed=False,cells=len(rows),CPU_owner_cases=3*len(rows)),indent=2))
if __name__=='__main__':main()
