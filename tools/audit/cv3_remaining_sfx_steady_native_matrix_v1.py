"""Source-only identical fourteen BASIC fixtures for the steady successor."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--lua-root',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);rows=[]
 for mode in[0,1]:
  for label,event in[('dagger',0x13),('axe',0x15),('flame',0x24),('ice',0x21),('lightning',0x1e),('fireball',0x1f),('bat',0x2f)]:
   name=('hard-'if mode else'easy-')+label;fixture=a.output/name
   steps=[['cv3_remaining_sfx_steady_native_prepare_v1.py','--output',str(fixture),'--mode',str(mode),'--event',hex(event)],['cv3_remaining_sfx_steady_native_cpu_v1.py','--fixture',str(fixture),'--lua-root',str(a.lua_root),'--output',str(a.output/'CPU'/name)],['cv3_remaining_sfx_queue_native_startup_v2.py','--fixture',str(fixture),'--lua-root',str(a.lua_root),'--output',str(a.output/'startup'/name)]]
   for args in steps:
    cmd=[sys.executable,str(ROOT/'tools/audit'/args[0]),*args[1:]];z=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True);(a.output/(name+'-'+args[0]+'.log')).write_text(z.stdout+z.stderr);assert not z.returncode,(name,args[0],z.stderr)
   prior=D/'cv3-remaining-queue-native-basic-v3'/name
   if name=='easy-lightning':prior=D/'cv3-remaining-queue-native-v1/fixture-v1'
   cfg,old=[json.loads((q/'configuration.json').read_text())for q in[fixture,prior]];delta={k for k in set(cfg)|set(old)if cfg.get(k)!=old.get(k)};assert delta<={'hooks','perf_names'},(name,delta)
   assert set(old['hooks'])-set(cfg['hooks'])=={'Cv3FxResidentNoise::NC15'};assert set(cfg['hooks'])-set(old['hooks'])=={'Cv3FxResidentBody::Emit','Cv3FxSteadyTry','Cv3FxResidentBody'}
   for label2 in['CPU','startup']:assert json.loads((a.output/label2/name/'proof.json').read_text())['passed']
   rows.append(dict(name=name,event=event,mode=mode,fixture=str(fixture),script_sha256=sha(fixture/'run.lua'),configuration_sha256=sha(fixture/'configuration.json'),CPU_proof_sha256=sha(a.output/'CPU'/name/'proof.json'),startup_proof_sha256=sha(a.output/'startup'/name/'proof.json'),prior_same_input_fixture=str(prior),prior_configuration_sha256=sha(prior/'configuration.json'),metadata_deltas=sorted(delta),source_image_hook='Genuine new Cv3FxResidentBody::Emit, replacing removed private NC15; no fake alias.',extra_perf_hooks=['Cv3FxSteadyTry','Cv3FxResidentBody']))
   (a.output/'progress.json').write_text(json.dumps(rows,indent=2)+'\n');print(name+' SOURCE ONLY PASS',flush=True)
 r=dict(passed=True,native_executed=False,accepted=False,cells=rows,source_only_real_release_NMI_cases=3*len(rows),full_startup_cases=len(rows),scope='Source-only assembled original actual owner+fullNMI replay into read-only startup-static observer, plus439 inactive complete Lua frames. Literal historical controller/arena/resource/seed and hardware/cadence guard body unchanged; only genuinely replaced emission hook, linked physical hook bytes and two diagnostic perf entries differ. No native launch/grant or140update gameplay acceptance.',tool_sha256=sha(__file__));(a.output/'proof.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(passed=True,cells=len(rows),native_executed=False),indent=2))
if __name__=='__main__':main()
