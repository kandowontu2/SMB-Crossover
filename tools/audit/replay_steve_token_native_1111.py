"""Verify Steve's natural token pickup and original glyphs in Mesen."""

import argparse
from hashlib import sha256
import json
from pathlib import Path

import check_steve_shatterhand_token_draw_1111 as Draw
import replay_steve_native_1111 as Punch
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run


R = Draw.H.ROOT
NIGHTLY = Draw.S.Donor.HOST
TAIL = R / 'tools/playthroughs/steve_token_native_1111.lua'


def controller():
    text = Punch.SCRIPT.read_text(encoding='utf-8')

    def change(old, new):
        nonlocal text
        assert text.count(old) == 1, old
        text = text.replace(old, new)

    change('local expected,pending={},{}', 'local expected,pending={},{}\n'
           'local tokenStarts,tokenSwitches,tokenFlights,tokenHud,tokenWorld=0,0,0,0,0')
    change('"enemy_slot":%d,"enemy_state":%d,"score":%d,"dma_matches":%d}',
           '"enemy_slot":%d,"enemy_state":%d,"score":%d,"dma_matches":%d,'
           '"token_starts":%d,"token_switches":%d,"token_world":%d,"token_flight":%d,"token_hud":%d}')
    change('read(0x10d+slot),dmaMatches))', 'read(0x10d+slot),dmaMatches,\n'
           'tokenStarts,tokenSwitches,tokenWorld,tokenFlights,tokenHud))')
    tail = TAIL.read_text(encoding='utf-8')
    change('local function tick()', tail + '\nlocal function tick()\n'
           "  if phase:sub(1,6)=='token-' then tokenTick();return end")
    change("      finish(true,'Steve held B and naturally defeated the first Goomba')",
           "      transition('token-approach',1)")
    change('right=pad&1~=0,down=pad&4~=0', 'right=pad&1~=0,left=pad&2~=0,down=pad&4~=0')
    change('select=pad&32~=0,b=pad&64~=0}', 'select=pad&32~=0,b=pad&64~=0,a=pad&128~=0}')
    change('  pending={}\n  local ok,message=coroutine.resume(route)',
           '  pending={}\n  verifyTokenDma()\n  local ok,message=coroutine.resume(route)')
    return text


def replay(script, rom, output, pin, info, *, beta):
    punch = info['punch']['symbols']
    return run(script, rom, output, pin, 110, extra_env={
        'SMB_STEVE_COOKIE': info['cookie'].hex(),
        'SMB_STEVE_BIRTH': str(punch['StevePunchBirth']),
        'SMB_STEVE_DRAW': str(punch['SteveDrawEmit']),
        'SMB_STEVE_TOKEN_PAIR': str(info['draw_pair']),
        'SMB_STEVE_TOKEN_BETA': str(int(beta)),
    })


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--beta', action='store_true')
    args = parser.parse_args()
    output = args.output.resolve()
    assert output.is_relative_to(R / 'build') and output != R / 'build'
    assert check(NIGHTLY)['ROM_sha256'] == Draw.Ingress.PIN
    image, info = Draw.proposal(NIGHTLY.read_bytes())
    pin = sha256(image).hexdigest()
    output.mkdir(exist_ok=True)
    candidate, script = output / 'candidate.nes', output / 'controller.lua'
    if candidate.exists():
        assert candidate.read_bytes() == image
    else:
        candidate.write_bytes(image)
    script.write_text(controller(), encoding='utf-8', newline='\n')
    result = replay(script, candidate, output / 'capture', pin, info, beta=args.beta)
    print(json.dumps(dict(candidate=pin, passed=result['passed'], receipt=result['receipt'],
                          receipt_SHA256=result['receipt_SHA256'], script_SHA256=result['script_SHA256']),
                     sort_keys=True), flush=True)
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
