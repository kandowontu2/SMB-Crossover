"""Bind actual composed ASM dependencies; no native/adoption claim."""
from pathlib import Path
import configparser,hashlib,json,re,subprocess
R=Path(__file__).resolve().parents[1];B=R/'build'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 out=B/'river-city-adopted-source-closure-v8.json';assert not out.exists()
 overlay=R;rom=B/'roster-shared-rcr-adopted-v8.nes'
 assert sha(rom)=='4cbd019100ba4dfc51fd9f71c5d3cabd844828eb7d5d2a4aa39413e3579ab39a'
 dep=B/'river-city-adopted-source-v8.d';obj=B/'river-city-adopted-source-v8.o';entry=B/'roster-shared-rcr-adopted-v8-objects/entrypoint.s'
 assert entry.read_bytes()==(overlay/'src/entrypoint.s').read_bytes()
 cfg=configparser.ConfigParser();cfg.optionxform=str;cfg.read(R/'build_options.ini')
 defs={k:v for s in cfg.values()for k,v in s.items()};defs.update(MAPPER_MMC3='0',MAPPER_MMC5='1',ENABLE_CROSSOVER='1',ENABLE_MMC5_EXPANDED='1')
 cmd=[str(R/'tools/Windows/cc65/bin/ca65.exe'),'--cpu','6502x','-g','-I',str(overlay/'src'),'-I',str(R/'src'),'-I',str(R),
      '--bin-include-dir',str(overlay),'--bin-include-dir',str(R),'--create-full-dep',str(dep),'-o',str(obj)]
 for k,v in defs.items():cmd+=['-D',k+'='+v]
 cmd+=[str(entry)];result=subprocess.run(cmd,cwd=R,capture_output=True,text=True);(B/'river-city-adopted-source-v8.log').write_text(result.stdout+result.stderr)
 assert result.returncode==0,result.stderr
 deps={}
 for word in re.split(r'(?<!\\)\s+',dep.read_text().split(':\t',1)[1].strip().removesuffix(':')):
  f=Path(word.replace('\\ ',' '));f=(f if f.is_absolute()else R/f).resolve();assert f.is_file();deps[str(f)]=sha(f)
 for name in ['src/river_city.s','src/river_city_core_host_v8.inc','src/river_city_shared_palette_host_v8.inc','src/mac_roster.s','src/roster_expansion_menu.inc',
              'src/zelda2_link_terrain.s','src/character_select.s','chr/characters/packed-mmc5-roster-expanded.chr','chr/raw/roster-expansion-menu.bin']:
  assert str((overlay/name).resolve())in deps,name
 assert str((R/'src/river_city_wall_prepass_v2.inc').resolve())in deps
 assert str((R/'src/celeste_mario_host_state.inc').resolve())in deps
 assert str((R/'src/celeste_mario_state.inc').resolve())not in deps
 files=[Path(__file__),rom,rom.with_suffix('.dbg'),rom.with_suffix('.lbl'),dep,overlay/'smb1base-mmc5-expanded.cfg',R/'build_options.ini']
 bindings=dict(deps)
 for p in files:bindings[str(p.resolve())]=sha(p)
 out.write_text(json.dumps(dict(source_CPU_only=True,native_run=False,ROM_sha256=sha(rom),actual_ASM_dependencies=len(deps),
   exact_staged_menu_inputs_confirmed=True,old_Celeste_state_not_consumed=True,command=cmd,bindings=bindings),indent=2)+'\n')
 print(json.dumps(dict(passed=True,ASM=len(deps),bindings=len(bindings),sha256=sha(out))))
if __name__=='__main__':main()
