"""Explicit frozen-parent bindings for the unmodified-stage Ladder regression."""
import argparse
from hashlib import sha256
import json
import re
from pathlib import Path

import compose_karnov_ladder_native_1113 as Feature
import check_karnov_natural_bomb_1113 as Stock
from run_stdout_mesen_1110 import run

PARENT = Stock.STEVE
CANDIDATE = '526ef1df172c3172fccbd35aa0471a9ff9a5a256a416acba8f7530d147a5b3f2'
BASE_LUA = '78fd7b91ed30e8b54ca1dcf3ac84ee278b1fa07a92f67d041d8c709c488a41af'
OUT = Feature.Owner.R/'build/metal-flower-native-1112'


def controller(candidate, *, wait_for_entry=False):
    assert sha256(candidate).hexdigest() == CANDIDATE
    parent = Feature.inverse_current(candidate)
    assert sha256(parent).hexdigest() == PARENT
    rebuilt, info = Feature.proposal_current(parent)
    assert rebuilt == candidate
    text = Stock.controller(parent)
    assert sha256(text.encode()).hexdigest() == BASE_LUA
    # Bind the Bomb observer to the actual new source call, without changing
    # any gameplay decisions or loosening the frozen parent's authentication.
    symbols = info['controls']
    pc, end = symbols['KrBombEnemyVertical'], symbols['KrBombEnemyReturn']
    at = Feature.role_at('combat', pc)
    body = candidate[at:at+end-pc+1]
    call = Feature.jump(0x20, symbols['HandleEnemyFBallCol'])
    assert body.count(call) == 1
    ret = pc+body.index(call)+2  # JSR's saved return, before RTS adds one.
    old = re.search(r'local BOMB_CONTACT_RETURN=(\d+)', text).group(0)
    text = text.replace(old, f'local BOMB_CONTACT_RETURN={ret}', 1)
    assert text.count(PARENT) == 1
    text = text.replace(PARENT, CANDIDATE)
    if wait_for_entry:
        # The old observer counts a forced neutral fall as a travel stall.
        # Keep its travel bound once the existing controller has witnessed
        # native grounded entry; retain all life, HP and physical bounds.
        before = "if routePhase=='travel'and #pickups>=2 and #pickups<4 and r('GameEngineSubroutine')==8 then"
        after = before[:-5]+" and not(r('LevelNumber')==1 and r('AreaType')==2 and not undergroundReady)then"
        assert text.count(before) == 1
        text = text.replace(before, after)
    assert all(term not in text for term in ('emu.write', 'io.open', 'loadState', 'saveState'))
    return text


def compact(result):
    return {key: result[key] for key in (
        'passed', 'native_Mesen', 'ROM_SHA256', 'script_SHA256',
        'receipt_SHA256', 'receipt', 'outputs_written', 'seconds')}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--wait-for-entry', action='store_true')
    args = parser.parse_args()
    parent = Feature.Owner.NIGHTLY.read_bytes()
    if sha256(parent).hexdigest() == CANDIDATE:
        parent = Feature.inverse_current(parent)
    assert sha256(parent).hexdigest() == PARENT
    candidate, _ = Feature.proposal_current(parent)
    text = controller(candidate, wait_for_entry=args.wait_for_entry)
    if not args.run:
        print(json.dumps(dict(ROM_SHA256=CANDIDATE,
            script_SHA256=sha256(text.encode()).hexdigest(),
            authored_level_or_enemy_edits=0, native_run=False, outputs_written=0)))
    else:
        rom, script = OUT/'candidate.nes', OUT/'controller.lua'
        rom.write_bytes(candidate)
        script.write_text(text, encoding='utf-8', newline='\n')
        result = run(script, rom, OUT/'capture', CANDIDATE, 180)
        print(json.dumps(compact(result), separators=(',', ':')), flush=True)
        assert result['passed'], 'Unmodified-stage Karnov regression failed'
