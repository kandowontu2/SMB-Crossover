"""Run real-menu Roll ability arenas against the explicitly supplied ROM."""
from pathlib import Path
import argparse,hashlib,importlib.util,json
ROOT=Path(__file__).resolve().parents[2]
def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--suite',choices=('components','rewards'),default='components');p.add_argument('--behavior',choices=('easy','hard'),default='easy');p.add_argument('--outlines',action='store_true');p.add_argument('--profile',action='store_true');a=p.parse_args()
 rom=a.rom.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
 s=importlib.util.spec_from_file_location('roll_mesen',ROOT/'tools/run_mesen.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.ROOT=out
 body=ROOT/('tests/roll-'+a.suite+'.lua');script=out/(a.suite+'.lua')
 constants=dict(ROLL_HARD=a.behavior=='hard',ROLL_OUTLINES=a.outlines,ROLL_PROFILE=a.profile,ROLL_MENU_PATH=(ROOT/'tests/roll-menu.lua').as_posix(),ROLL_OBSERVER_PATH=(ROOT/'tools/audit/roll_render_observer.lua').as_posix(),ROLL_PERFORMANCE_PATH=(ROOT/'tools/audit/roll_performance_observer.lua').as_posix())
 script.write_text('\n'.join(k+'='+json.dumps(v)for k,v in constants.items())+'\n'+body.read_text())
 code=m.run(script,rom,timeout=45,emulator_options=['--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
 sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 (out/'results.json').write_text(json.dumps(dict(ROM_sha256=sha(rom),script_sha256=sha(script),test_sha256=sha(body),menu_sha256=sha(ROOT/'tests/roll-menu.lua'),observer_sha256=sha(ROOT/'tools/audit/roll_render_observer.lua'),profiler_sha256=sha(ROOT/'tools/audit/roll_performance_observer.lua')if a.profile else None,behavior=a.behavior,outlines=a.outlines,exit=code),indent=2)+'\n')
 return code
if __name__=='__main__':raise SystemExit(main())
