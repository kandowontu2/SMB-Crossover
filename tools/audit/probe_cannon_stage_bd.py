"""Explicit native stage-selection diagnostic; not an ordinary traversal proof."""
from pathlib import Path
import argparse,hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools'));import run_mesen
p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--world',type=int,default=4);p.add_argument('--level',type=int,default=0);p.add_argument('--area',type=int,default=0);a=p.parse_args()
P=R/'build/roster-through-2-2/claude-final-video-0-v0-mmc3'
O=R/'build/verification'/a.tag;assert not O.exists();O.mkdir()
cfg=json.loads((P/'manifest.json').read_text())['config']
cfg.update(limit=6000,out=O.as_posix()+'/',record=False,segmented=False,allowDeaths=True,
    replay=(P/'inputs.csv').as_posix(),policy=(P/'policy.lua').as_posix(),audit=(O/'audit.lua').as_posix())
lua=lambda v:'nil'if v is None else str(v).lower()if isinstance(v,bool)else json.dumps(v)
(O/'run.lua').write_text('ROSTER_CONFIG={\n'+''.join(f'{k}={lua(v)},\n'for k,v in cfg.items())+'}\ndofile('+json.dumps((P/'harness.lua').as_posix())+')\n',encoding='utf-8')
audit=r'''return function(cfg)
 local base=assert(dofile(BASE))(cfg)
 local frame,seeded=0,false
 local function r(n)return emu.read(assert(L[n]),emu.memType.nesDebug)end
 local function w(n,v)emu.write(assert(L[n]),v,emu.memType.nesDebug)end
 emu.addMemoryCallback(function()
  if not seeded then
   w('WorldNumber',SEED_WORLD);w('LevelNumber',SEED_LEVEL);w('AreaNumber',SEED_AREA)
   seeded=true;print('DIAGNOSTIC native stage selection at '..frame)
  end
 end,emu.callbackType.exec,L.LoadAreaPointer)
 return{failure=base.failure,frame=function(n)frame=n;base.frame(n);if n==600 then assert(seeded,'Diagnostic stage seed is admitted')end end,
  finish=base.finish}
end
'''.replace('BASE',json.dumps((R/'build/verification/world-actors-ba-mario/audit.lua').as_posix())).replace('SEED_WORLD',str(a.world)).replace('SEED_LEVEL',str(a.level)).replace('SEED_AREA',str(a.area))
(O/'audit.lua').write_text(audit,encoding='utf-8')
rom=P/'smb-crossover-mmc3.nes'
code=run_mesen.run(O/'run.lua',rom,timeout=100,emulator_options=['--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
result=json.loads((O/'result.json').read_text())if(O/'result.json').exists()else None
summary=dict(exit=code,result=result,ROM_sha256=hashlib.sha256(rom.read_bytes()).hexdigest(),
    authored_state='Only the initial world/level/area are selected through RAM at native LoadAreaPointer. Native terrain and actors parse normally afterwards. Ordinary original Mario controller inputs reused as diagnostic stimuli, not a route proof.',
    actor_or_OAM_writes=False,goal_complete=False)
(O/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary))
