"""Measure actual CPU/update/draw work in bounded seeded ship scenarios."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,csv,collections,statistics
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--variant',type=int,default=1);a=p.parse_args()
 out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);rom=a.rom.resolve()
 fixture=(ROOT/'tests/parodius-performance.lua').read_text();observer=(ROOT/'tools/audit/parodius_performance_observer.lua').read_text()
 assert fixture.count('PERFORMANCE_OBSERVER')==1
 script=out/'performance.lua';script.write_text(f'PN_VARIANT={a.variant}\n'+fixture.replace('PERFORMANCE_OBSERVER',observer))
 spec=importlib.util.spec_from_file_location('performance_mesen',ROOT/'tools/run_mesen.py');runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner);runner.ROOT=out
 code=runner.run(script,rom,timeout=60,emulator_options=['--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
 result=dict(ROM_sha256=sha(rom),fixture_sha256=sha(ROOT/'tests/parodius-performance.lua'),observer_sha256=sha(ROOT/'tools/audit/parodius_performance_observer.lua'),script_sha256=sha(script),exit=code)
 (out/'results.json').write_text(json.dumps(result,indent=2)+'\n');assert code==0
 folder=out/'build/verification';frames=list(csv.DictReader((folder/'parodius-performance-frames.csv').open()));calls=list(csv.DictReader((folder/'parodius-performance-calls.csv').open()))
 assert len(calls)>500 and{r['phase']for r in frames}>={'idle','enemies','normal-fire','full-fleet'}
 byphase={}
 for phase in('idle','enemies','normal-fire','full-fleet'):
  f=[r for r in frames if r['phase']==phase];c=[r for r in calls if r['phase']==phase]
  spans={}
  for name in sorted({r['name']for r in c}):
   values=[int(r['cpuCycles'])for r in c if r['name']==name];spans[name]=dict(calls=len(values),mean=statistics.mean(values),maximum=max(values),total=sum(values))
  byphase[phase]=dict(videoFrames=len(f),updates=sum(int(r['updates'])for r in f),draws=sum(int(r['draws'])for r in f),lagNmis=sum(int(r['lagNmis'])for r in f),peakEnemies=max(int(r['enemies'])for r in f),peakShots=max(int(r['bullets'])for r in f),spans=spans)
 native_inputs=folder/'performance-native-inputs.csv'
 result.update(passed=True,phases=byphase,native_input_sha256=sha(native_inputs),scope='ISR-excluded inclusive native CPU spans and updates/draws per video frame. Nested spans overlap; do not sum them as exclusive costs. Seeded arenas, not a campaign pass. Controller pulses use completed native update counts; the actual native input trace is retained for before/after equality.')
 (out/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,rom_sha256=result['ROM_sha256'],phases={p:{k:v for k,v in r.items()if k!='spans'}for p,r in byphase.items()})))


if __name__=='__main__':main()
