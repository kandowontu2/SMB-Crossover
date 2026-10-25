from pathlib import Path
import importlib.util,json,struct
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;O=D/'ryu-head-oversized-mmc3-v10/menu-observer-v1';O.mkdir(exist_ok=False)
f=D/'ryu-head-oversized-mmc3-v10/menu-v1/source-sprite-off/menu-walk.lua';t=f.read_text();t=t.replace('if frame>18000 then','if frame>1200 then');t=t.replace("error('menu walk timed out at identity '..which..', state '..r('CrossoverMenuState'))","error('menu walk timed out at identity '..which..', state '..r('CrossoverMenuState')..', index '..r('CrossoverMenuIndex')..', char '..r('SelectedCharacter')..', proto '..r('ProtoVariant')..', mode '..r('X5ChrMode')..', portrait '..r('M3CacheProfile'))")
p=O/'run.lua';p.write_text(t);f=R/'tools/run_mesen.py';s=importlib.util.spec_from_file_location('runner',f);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.ROOT=O
raise SystemExit(m.run(p,D/'ryu-head-oversized-mmc3-v10/candidate.nes',timeout=45,emulator_options=['--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false']))
