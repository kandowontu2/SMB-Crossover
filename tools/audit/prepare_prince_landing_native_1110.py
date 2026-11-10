"""Emit one qualified private ROM and verify Prince's natural Easy landing."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from prepare_selected_native_packet_v1 import prepare, sha, R
from stage_complete_roster_1110 import apply

BASE = R / 'build/complete-roster-native-1110/candidate.nes'
PIN = 'c10b7d87f466bf028096bddd33b7ac2baee242870ee83ccc4eebd529af57bd7f'
PROOF = R / 'build/prince-previous-sole-1110/proof.json'
QUALIFIED = PROOF.with_name('qualified-proof.json')
PRIOR = R / 'build/prince-camera-roof-native-1110/native'

COMPACT = r'''
-- Retain one final screenshot and one aggregate result. CSV and ancillary
-- diagnostic serialization still runs against sinks; emulated checks remain.
local originalOpen=io.open
local sink={}
function sink:write(...) return self end
function sink:flush() return true end
function sink:close() return true end
io.open=function(path,mode)
 if (mode=='w' or mode=='wb') and path:sub(1,#OUTPUT)==OUTPUT then
  local name=path:sub(#OUTPUT+1)
  if name:sub(-4)=='.png' then return originalOpen(OUTPUT..'terminal.png',mode)end
  if name=='result.json' or name=='full11.json' then return originalOpen(OUTPUT..'result.json',mode)end
  return sink
 end
 return originalOpen(path,mode)
end
'''

LANDING = r'''
local naturalLanding=nil
emu.addMemoryCallback(function()
 if r('SelectedCharacter')~=38 or r('GameEngineSubroutine')~=8 then return end
 local wx=r('Player_X_Position')+256*r('Player_PageLoc')
 if wx<850 or wx>920 then return end
 local mapped=emu.convertAddress(0x9806)
 if not mapped or mapped.memType~=emu.memType.nesPrgRom or mapped.address//8192~=126 then return end
 assert(not naturalLanding,'One native target Goomba stomp')
 local slot=r('ObjectOffset')
 naturalLanding={frame=frame,Main=admitted,x=wx,slot=slot,HP=ps(0x6cf),
  previous_sole=ps(PREVIOUS_SOLE),current_sole=ps(0x84),
  enemy_head=emu.read(0x65d+4*slot,emu.memType.nesDebug),
  behavior=r('CrossoverBehaviorVersion'),action=ps(0x616)}
end,emu.callbackType.exec,0x9806)
local function landingFinish()
 if not naturalLanding then return false end
 local slot=naturalLanding.slot
 local enemyState=emu.read(0x1f+slot,emu.memType.nesDebug)
 local enemyFlag=emu.read(0x10+slot,emu.memType.nesDebug)
 if enemyState~=4 and enemyFlag~=0 then return false end
 assert(naturalLanding.behavior==0 and naturalLanding.previous_sole<=naturalLanding.enemy_head
   and naturalLanding.enemy_head<naturalLanding.current_sole,'Actual descending sole crosses actual enemy head')
 assert(naturalLanding.HP==5 and ps(0x6cf)==5 and r('NumberofLives')==2,'Natural landing retains all HP and lives')
 shot('prince-natural-landing')
 writejson('result.json',{passed=true,ROM_sha256=Q.ROM_sha256,controller_only=true,
  script_RAM_writes=false,full_stage=false,frames=frame,admitted=admitted,
  reason='Natural third-pipe Easy landing invokes native stomp without donor injury',
  landing=naturalLanding,enemy_state=enemyState,enemy_flag=enemyFlag,
  terminal={HP=ps(0x6cf),lives=r('NumberofLives'),x=r('Player_X_Position')+256*r('Player_PageLoc'),
   engine=r('GameEngineSubroutine'),action=ps(0x616)},
  scope='Original controller-only third-pipe route through the reproduced X891 contact. Full1-1 and later leading-enemy contact remain separate.'})
 done=true;emu.stop(0);return true
end
'''


def once(source, old, new):
    assert source.count(old) == 1, old
    return source.replace(old, new)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(R / 'build')
    assert not out.exists() or set(p.name for p in out.iterdir()) <= {'candidate.nes'}
    initial, qualified = (json.loads(p.read_text()) for p in (PROOF, QUALIFIED))
    assert initial['passed'] and qualified['passed']
    assert qualified['initial_proof_SHA256'] == sha(PROOF)
    for q in (initial, qualified):
        for path, digest in q['bindings'].items():
            assert sha(R / path) == digest, path
    assert sha(BASE) == initial['parent_SHA256'] == qualified['parent_SHA256'] == PIN
    raw = apply(BASE.read_bytes(), initial['patches'], 'Prince previous sole')
    from hashlib import sha256
    digest = sha256(raw).hexdigest()
    assert digest == initial['expected_memory_only_SHA256'] == qualified['expected_memory_only_SHA256']
    out.mkdir(exist_ok=True)
    rom = out / 'candidate.nes'
    if rom.exists():
        assert rom.read_bytes() == raw
    else:
        rom.write_bytes(raw)
    source = (PRIOR / 'controller.lua').read_text()
    marker = '-- Controller-only source; Q is supplied by the hash-bound plan preparer.'
    override = 'Q.ROM_sha256=' + json.dumps(digest) + '\nQ.cookie={' + ','.join(map(str, bytes.fromhex(qualified['Prince_cookie']))) + '}\n'
    source = once(source, marker, COMPACT + '\n' + override + marker)
    previous_sole = qualified['layout']['previous_sole_operand'] - 0xc000
    source = once(source, 'local function fullTick(finish)',
                  LANDING.replace('PREVIOUS_SOLE', str(previous_sole)) + '\nlocal function fullTick(finish)\n if landingFinish() then return true end')
    assert 'emu.write(' not in source
    from prepare_prince_camera_framing_native_1110 import SYMBOLS
    labels, debug = SYMBOLS
    packet = out / 'natural-landing'
    prepare(packet, rom, source, {Path(__file__), PROOF, QUALIFIED, PRIOR / 'controller.lua'},
            expected=digest, timeout=240, allow_interactive=True, rom_symbols=(labels, debug),
            scope='Natural Prince Easy third-pipe landing, same original controller through X891, actual native stomp and no HP/life loss. Original donor movement unchanged; only one aggregate JSON and final PNG retained. Full1-1 not claimed.')
    run = subprocess.run([sys.executable, '-B', str(R / 'tools/audit/run_small_mesen_packet_1110.py'),
                          '--files', '6', str(packet / 'run.py')])
    result = json.loads((packet / 'capture/result.json').read_text())
    print(json.dumps(dict(exit=run.returncode, passed=result['passed'], reason=result['reason'], ROM_sha256=digest)), flush=True)
    raise SystemExit(run.returncode)


if __name__ == '__main__':
    main()
