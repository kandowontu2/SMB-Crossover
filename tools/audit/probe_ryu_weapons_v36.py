"""Passive receipts around an unchanged failing native weapon fixture."""
from pathlib import Path
import argparse, hashlib, json, shutil, sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import run_mesen

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--tag',required=True)
parser.add_argument('--hold',type=int,default=1)
args=parser.parse_args()
assert 1 <= args.hold <= 8
OUT=ROOT/f'build/verification/ryu-weapons-v36d-negative-probe-{args.tag}'
OUT.mkdir(exist_ok=False)
fixture=(ROOT/'tests/expanded-weapons.lua').read_text()
original_sha=hashlib.sha256((ROOT/'tests/expanded-weapons.lua').read_bytes()).hexdigest()
if args.hold>1:
    assert 'select=c==10 and frame==560' in fixture
    fixture=fixture.replace('select=c==10 and frame==560',f'select=c==10 and frame>=560 and frame<{560+args.hold}',1)
(OUT/'fixture.lua').write_text(fixture)
report={'scope':'Original fixture arenas/oracles retained; hardware Select hold is explicit, passive observer only otherwise; not a route', 'select_hold_frames':args.hold, 'original_fixture_sha256':original_sha, 'used_fixture_sha256':hashlib.sha256((OUT/'fixture.lua').read_bytes()).hexdigest(), 'runs':[]}
for version in ('v35','v36-provisional-d'):
    for mapper in ('mmc3','mmc5'):
        d=OUT/f'{version}-{mapper}';d.mkdir()
        checkpoint=ROOT/f'build/checkpoints/roster-audit-{version}'
        src=checkpoint/f'smb-crossover-{mapper}.nes'
        rom=d/f'ryu-weapon-{version}-{mapper}.nes'
        for ext in ('.nes','.lbl','.dbg'):shutil.copyfile(src.with_suffix(ext),rom.with_suffix(ext))
        script=d/'observe.lua'
        script.write_text(f'''dofile([=[{(ROOT/'tests/menu-bootstrap.lua').as_posix()}]=])
EXPANDED_CHARACTER=10
dofile([=[{(OUT/'fixture.lua').as_posix()}]=])
local frame=0
local f=assert(io.open([=[{(d/'passive.csv').as_posix()}]=],'w'))
local names={{'SelectedCharacter','CrossoverMenuState','OperMode','OperMode_Task','GameEngineSubroutine','TimerControl','GamePauseStatus','SavedJoypad1Bits','InvFresh','Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_State','PlayerStatus','PlayerFacingDir','InvOwnedLo','InvSelected','RgShotType','RgShotX','RgShotPage','RgShotY','RgShotVXHi','Enemy_Flag','Enemy_ID','Enemy_State','MmEnemyHealthLo','Enemy_X_Position','Enemy_Y_Position','MmEnemyFlash','RgEnemyStun'}}
local function count(n)
 if n=='InvOwnedLo' or n=='InvSelected' then return 12 end
 if n:find('RgShot') then return 9 end
 if n:find('Enemy') then return 5 end
 return 0
end
f:write('frame');for _,n in ipairs(names)do for i=0,count(n)do f:write(','..n..'+'..i)end end;f:write('\\n')
emu.addEventCallback(function()
 frame=frame+1
 if frame>=495 then
 f:write(frame)
 for _,n in ipairs(names)do for i=0,count(n)do f:write(','..emu.read(assert(L[n],n)+i,emu.memType.nesDebug))end end
 f:write('\\n');f:flush()
 end
end,emu.eventType.endFrame)
''')
        exit_code=run_mesen.run(script,rom,timeout=60)
        source_log=ROOT/f'build/verification/{rom.stem}-{script.stem}.log'
        shutil.copyfile(source_log,d/'native.log')
        report['runs'].append({'version':version,'mapper':mapper,'exit':exit_code,'rom_sha256':hashlib.sha256(rom.read_bytes()).hexdigest(),'passive_sha256':hashlib.sha256((d/'passive.csv').read_bytes()).hexdigest() if (d/'passive.csv').exists() else None})
        (OUT/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
        print(version,mapper,exit_code,flush=True)
