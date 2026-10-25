"""Capture current-ROM front-end artwork with ordinary buttons only."""
from pathlib import Path
import hashlib, json, re, subprocess

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/player-guide-agent'
ASSETS=ROOT/'docs/player-guide/assets'
OUT.mkdir(parents=True,exist_ok=True); ASSETS.mkdir(parents=True,exist_ok=True)
ROM=ROOT/'build/checkpoints/ryu-overlap-hr/build/smb-crossover-mmc3.nes'
labels={m[2]:int(m[1],16) for m in re.finditer(r'^al ([0-9A-Fa-f]+) \.([\w]+)$',ROM.with_suffix('.lbl').read_text(),re.M)}
press={120:'start',200:'select',240:'select',280:'right',340:'right',400:'right',440:'select',480:'select',520:'right',580:'right',640:'right',700:'right',760:'right',820:'right',880:'right',940:'right',1000:'b',1040:'down',1080:'a',1140:'down',1180:'a',1260:'down',1300:'a'}
shots={100:'title',160:'mario',220:'luigi',300:'megaman',360:'samus',420:'bill',460:'lance',540:'link',600:'simon',660:'pit',720:'rygar',780:'scrooge',840:'bass',900:'ryu',960:'sophia',1120:'options-easy',1220:'options-hard',1340:'cheats'}
code=['local frame=0','local L={}']
code += [f'L["{n}"]={labels[n]}' for n in ('SelectedCharacter','CrossoverMenuState','CrossoverBehaviorVersion','MarioVariant','BillVariant') if n in labels]
code += ['local function r(n) return emu.read(L[n],emu.memType.nesDebug) end','local press={'+','.join(f'[{f}]="{b}"' for f,b in press.items())+'}','local shots={'+','.join(f'[{f}]="{b}"' for f,b in shots.items())+'}', 'emu.addEventCallback(function() local p={} for f,b in pairs(press) do if frame>=f and frame<f+3 then p[b]=true end end emu.setInput(p,0) end,emu.eventType.inputPolled)', 'emu.addEventCallback(function() frame=frame+1 local tag=shots[frame] if tag then local f=assert(io.open([=['+ASSETS.as_posix()+']=].."/menu-"..tag..".png","wb")); f:write(emu.takeScreenshot());f:close(); print(tag.." character="..r("SelectedCharacter").." menu="..r("CrossoverMenuState").." mode="..r("CrossoverBehaviorVersion")) end if frame==1360 then emu.stop(0) end end,emu.eventType.endFrame)']
lua=OUT/'capture-menu.lua';lua.write_text('\n'.join(code))
r=subprocess.run(['C:/mesen2/Mesen.exe','--testRunner','--enableStdout','--timeout=30',str(lua),str(ROM)],capture_output=True,text=True,timeout=45)
(OUT/'capture-menu.log').write_text(r.stdout+'\n'+r.stderr)
assert r.returncode==0,(r.returncode,r.stdout,r.stderr)
manifest={'method':'Cold boot; ordinary controller input only; no emulated RAM/ROM/register writes or save states. Native full screenshots.','rom':str(ROM.relative_to(ROOT)),'rom_sha256':hashlib.sha256(ROM.read_bytes()).hexdigest(),'images':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in ASSETS.glob('menu-*.png')}}
(OUT/'menu-provenance.json').write_text(json.dumps(manifest,indent=2))
print(r.stdout)
