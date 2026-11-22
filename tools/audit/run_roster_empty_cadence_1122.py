"""Measure empty 1-1 cadence through normal menus on the verified MMC5 nightly."""

import argparse
from functools import lru_cache
import json
from unittest.mock import patch

from check_ff_stdout_controller_source_1110 import LuaRuntime
from check_tmnt_render_oa import address
import check_remaining_roster_starts_1110 as Census
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
import prepare_kirby_contacts_current_1108_v1 as Authority
import run_sonic_current_empty_cadence_1122 as Timing
from run_stdout_mesen_1110 import run


@lru_cache(maxsize=1)
def roster(raw):
    assert Authority.sha(Authority.AUTHORITY) == Authority.AUTHORITY_ROM
    assert Authority.sha(Authority.AUTHORITY.with_suffix('.dbg')) == Authority.AUTHORITY_DBG
    bundle = dict(Authority.scoped_load(Authority.AUTHORITY), raw=raw)
    with patch.object(Census.W, 'bundle', lambda image: bundle if image is raw else None):
        census = Census.inventory(raw)
    assert census['distinct_named_entries'] == census['confirmable_named_entries'] == 101
    rows = {}
    for row in census['rows']:
        ident = row['name']
        if ident not in rows:
            rows[ident] = dict(row, checks=[dict(address=address(bundle, n), value=v)
                                           for n, v in row['variants'].items()])
    return rows


@lru_cache(maxsize=1)
def observer(raw):
    # Preserve the validated observer's actual Main entry and return tracking,
    # its clock, frame history and physical controller-read callbacks.
    text = Timing.controller(raw, 'sonic').split('\n', 1)[1]

    def replace(old, new):
        nonlocal text
        assert text.count(old) == 1, old
        text = text.replace(old, new, 1)

    start = text.index('local function work(')
    stop = text.index('local function state()', start)
    text = text[:start] + text[stop:]
    start = text.index('local function workMapped(')
    stop = text.index('local function frames(', start)
    text = text[:start] + text[stop:]
    start = text.index('local function empty()')
    stop = text.index('emu.addMemoryCallback(guarded(function()', start)
    text = text[:start] + '''local function identity()
 assert(r(0x6002)==C.raw,'Native selected character owner')
 for _,v in ipairs(C.checks)do assert(r(v.address)==v.value,'Native selected alternate')end
end
local function empty()
 identity()
 assert(r(0x75f)==2 and r(0x754)==5 and r(0x764)==0 and r(0x761)==0,'Ordinary 1-1 with two lives')
 assert(r(0x7ffc)==0 and r(0x7ffb)==0 and r(0x7fe1)==0,'Natural Easy without cheats')
 for i=0,5 do assert(r(0x10+i)==0,'Enemy entered empty profile')end
end
''' + text[stop:]
    replace('local portReads,pollFrames,motor,motorBase,motorLive= {},{},0,0,nil\nlocal motorHooked={}',
            'local portReads,pollFrames={},{}')
    replace('variant=r(0x5ffe),power=r(0x5fc5)', 'cycle=C.select,power=r(0x75b)')
    replace('form=C.form,actual_motor_returns=motor-motorBase,', 'character=C.name,')
    replace('Actual accepted motor returns, literal', 'Literal')
    replace('and work(2,0xc119)==1 and ticks<64', 'and ticks<64')
    replace('motorBase=motor;', '')
    replace(",motor=motor}", "}")
    replace("  assert(not motorLive and motor-observed.motor==1,'One accepted returned motor per complete Main')\n", '')
    replace(" for _,b in ipairs({4,4,4,1})do press(b)end\n"
            " assert(r(0x7309)==25,'MrGimmick slot');for _=1,C.select do press(32)end\n"
            " assert(r(0x6002)==43 and r(0x5ffe)==C.select,'Actual Sonic form')",
            " for _,b in ipairs(C.directions)do press(b)end\n"
            " assert(r(0x7309)==C.slot,'Actual compiled roster slot')\n"
            " for _=1,C.select do press(32)end\n identity()")
    replace("assert(ticks==64 and x()>40 and x()<160 and motor-motorBase==64,'Exact empty profile endpoint')",
            "assert(ticks==64 and phases[2].after.x>phases[2].before.x,'Right moves through the empty opening')")
    replace('Natural Sonic empty64-Main profile', 'Natural roster empty64-Main profile')
    return text


def controller(raw, row):
    config = dict(sha=Timing.PIN, name=row['name'], raw=row['raw'], slot=row['slot'],
                  select=row['cycle'], checks=row['checks'],
                  directions=[4] * (row['slot'] // 8) + [1] * (row['slot'] % 8))
    text = 'local C=' + Timing.value(config) + '\n' + observer(raw)
    LuaRuntime().compile(text)
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('characters', nargs='+', type=str.upper)
    args = parser.parse_args()
    guard = check(Timing.ROM)
    raw = Timing.ROM.read_bytes()
    assert guard['ROM_sha256'] == Timing.H(raw) == Timing.PIN
    selected = roster(raw)
    scripts = [controller(raw, selected[name]) for name in args.characters]

    out = Timing.SHARED
    candidate, script = out/'candidate.nes', out/'controller.lua'
    assert set(out.iterdir()) == {candidate, script} and candidate.read_bytes() == raw
    require_free_workspace(Timing.R, Timing.ROM, allow_interactive=True)
    previous = script.read_bytes()
    try:
        for text in scripts:
            script.write_bytes(text.encode())
            result = run(script, Timing.ROM, out/'capture', Timing.PIN, 90)
            assert result['outputs_written'] == 0 and not result['images']
            fields = ('passed', 'reason', 'character', 'phases', 'inclusive_video_frames',
                      'measured_Main', 'no_controller_read_frames', 'native_lag_NMI',
                      'inclusive_Main_costs', 'Main_return_histogram')
            report = {name: result['receipt'][name] for name in fields if name in result['receipt']}
            report.update(receipt_SHA256=result['receipt_SHA256'], script_SHA256=result['script_SHA256'])
            print('ROSTER CADENCE ' + json.dumps(report, separators=(',', ':')), flush=True)
    finally:
        script.write_bytes(previous)
        assert candidate.read_bytes() == Timing.ROM.read_bytes() == raw and check(Timing.ROM) == guard


if __name__ == '__main__':
    main()
