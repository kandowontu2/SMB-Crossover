"""All four turtles/both modes, one worker, with the unchanged native arena."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    fixture=ROOT/'tests/tmnt-performance.lua';observer=ROOT/'tools/audit/tmnt_performance_observer.lua'
    q=dict(passed=False,complete=False,ROM_sha256=sha(a.rom),driver_sha256=sha(fixture),observer_sha256=sha(observer),runs=[],native_workers=1,goal_complete=False)
    for variant,name in enumerate(['leonardo','raphael','michelangelo','donatello']):
        for mode in ['easy','hard']:
            key=name+'-'+mode;out=a.output/key;out.mkdir()
            script=out/'run.lua';script.write_text('TMNT_CFG={variant='+str(variant)+',mode='+json.dumps(mode)+',observer='+json.dumps(observer.as_posix())+'}\ndofile('+json.dumps(fixture.as_posix())+')\n')
            args=[sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(out),str(script),str(a.rom.resolve()),'--timeout','90',
              '--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
            r=subprocess.run(args,cwd=ROOT,capture_output=True,text=True);(out/'host.log').write_text(r.stdout+r.stderr)
            result=json.loads((out/'result.json').read_text())if(out/'result.json').exists()else None
            q['runs'].append(dict(identity=key,variant=variant,mode=mode,exit=r.returncode,result=result));(a.output/'progress.json').write_text(json.dumps(q,indent=2)+'\n')
            assert r.returncode==0 and result and result['passed'],(key,(r.stdout+r.stderr)[-1400:]);print(key,'PASS',flush=True)
    q.update(complete=True,passed=True);(a.output/'results.json').write_text(json.dumps(q,indent=2)+'\n');(a.output/'progress.json').write_text(json.dumps(q,indent=2)+'\n')
if __name__=='__main__':main()
