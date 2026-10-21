"""Run bounded immutable-ROM walking/crowd cycle and actual-DMA benchmarks."""
from pathlib import Path
import argparse,hashlib,json,shutil,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import run_mesen
p=argparse.ArgumentParser();p.add_argument('version');p.add_argument('--tag',required=True);p.add_argument('--characters',default='4,5,10');p.add_argument('--mappers',default='mmc3,mmc5');p.add_argument('--source',type=Path);p.add_argument('--checkpoint',type=Path,help='Explicit immutable provisional/checkpoint directory');p.add_argument('--metrics-only',action='store_true');a=p.parse_args()
out=ROOT/f'build/profiling/plain-walking-{a.version}-{a.tag}';out.mkdir(parents=True,exist_ok=False)
source=a.source.resolve()if a.source else ROOT/'tools/profiling/plain_walking.lua';shutil.copyfile(source,out/'profile-source.lua')
frozen_source=out/'profile-source.lua'
manifest={'version':a.version,'scope':'Explicit flat crowd arena; controller Right/neutral; no attacks; not route evidence','metrics_only':a.metrics_only,'canonical_and_ppu_visibility_captured':not a.metrics_only,'script_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'run_mesen_sha256':hashlib.sha256((ROOT/'tools/run_mesen.py').read_bytes()).hexdigest(),'runs':[]}
for mapper in a.mappers.split(','):
 for char in map(int,a.characters.split(',')):
  d=out/f'{mapper}-c{char}';d.mkdir();stem=f'walk-{a.version}-{a.tag}-{mapper}-c{char}'
  checkpoint=a.checkpoint.resolve()if a.checkpoint else ROOT/f'build/checkpoints/roster-audit-{a.version}'
  rom=d/f'{stem}.nes';src=checkpoint/f'smb-crossover-{mapper}.nes'
  for ext in ('.nes','.lbl','.dbg'):shutil.copyfile(src.with_suffix(ext),rom.with_suffix(ext))
  script=d/'run.lua';script.write_text(f'PROFILE_CHARACTER={char}\nPROFILE_METRICS_ONLY={str(a.metrics_only).lower()}\nPROFILE_OUTPUT=[=[{(d/stem).as_posix()}]=]\ndofile([=[{frozen_source.as_posix()}]=])\n',encoding='utf8')
  code=run_mesen.run(script,rom,timeout=180,emulator_options=['--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
  log=ROOT/f'build/verification/{rom.stem}-{script.stem}.log';shutil.copyfile(log,d/'native.log')
  manifest['runs'].append({'mapper':mapper,'character':char,'exit':code,'rom_sha256':hashlib.sha256(rom.read_bytes()).hexdigest(),'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest()})
  (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
  print(mapper,char,code,flush=True)
  if code:raise SystemExit(code)
