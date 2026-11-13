"""Reuse the original-input Prince pickup route on the current nightly."""

import argparse
from functools import partial
from hashlib import sha256
import json
import sys
from unittest.mock import patch

import prince_cold_packet_1111 as Packet
import replay_prince_first_pickup_1112 as Old
import replay_prince_native_flag_1111 as Stage
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run


BASE = '65ee94ca9ac6e1b5ad44303d08f76ecbc175a88232c82ef8c32712edf150a643'
PIN = 'a3c5fa63872fbb3103ae57d9748fef233e8b2273e26d985aa4006b2492d81b8a'
OUTPUT = Old.R/'build/metal-flower-native-1112'
CONTROLLER = Stage.controller


class CheckedController(Exception):
    pass


def current_route(cookie, _historical_publication, brake, adaptive):
    # The shipped sword packet compacted this publication from D74B to D746.
    return CONTROLLER(cookie, 0xd746, brake, adaptive)


def run_current(script, *args, collect_sword=False, check_only=False, **kwargs):
    text = script.read_text(encoding='utf-8')
    # Flag/ID/state/X/Y in the inherited pickup probe all address slot5.
    # Its type must use the same slot, rather than the unrelated slot0 type.
    assert 'read(0x34)' in text
    text = text.replace('read(0x34)', 'read(0x39)')
    old = "progress=='fourth-descent-run' and s.action==1 and s.mode==1 and s.lock==0"
    if old in text:
        assert text.count(old) == 1
        text = text.replace(old, "progress=='fourth-descent-run' and running(s)")
    if collect_sword:
        # The native/CPU alignment probes distinguish X1214 (too far from
        # this ledge) from X1218..1230. Account for the original brake/turn.
        anchor = "progress=='flower-approach' and s.x>=1224"
        assert text.count(anchor) == 1
        text = text.replace(anchor, "progress=='flower-approach' and s.x>=1230")
        before = "      finish(flowerSeen,'Natural flower reveal after mushroom');return"
        assert text.count(before) == 1
        text = text.replace(before, """      if read(0x24)&128==0 then pad=0;return end
      assert(flowerSeen and read(0x39)==1,'Mature native flower in slot5')
      late.flower.left=1248
      while solid(late.flower.left-16,144)do late.flower.left=late.flower.left-16 end
      assert(late.flower.left>=1152 and late.flower.left<=1248,'Actual connected flower ledge')
      late.flower.geometry={}
      for col=1152,1328,16 do late.flower.geometry[#late.flower.geometry+1]={x=col,tile=tile(col,144)}end
      switch('flower-retreat',0);return""", 1)
        before = "    if progress=='flower-approach' and s.x>=1230 then"
        assert text.count(before) == 1
        body = (Old.R/'tools/reference/prince_natural_sword_1113.lua').read_text(encoding='utf-8')
        text = text.replace(before, body+"\n    if progress=='flower-approach' and s.x>=1230 then", 1)
    script.write_text(text, encoding='utf-8', newline='\n')
    if check_only:
        from check_ff_stdout_controller_source_1110 import LuaRuntime
        assert LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
        assert 'emu.write' not in text and 'io.open' not in text and 'takeScreenshot' not in text
        print(json.dumps(dict(compiles=True, script_SHA256=sha256(script.read_bytes()).hexdigest(),
                              ROM_SHA256=PIN, collect_sword=collect_sword, output_files=1,
                              native_run=False)), flush=True)
        raise CheckedController()
    result = run(script, *args, **kwargs)
    if collect_sword:
        route = result['receipt'].get('later_route', {})
        print(json.dumps(dict(event='Prince_sword_probe', passed=result['passed'],
            receipt_SHA256=result['receipt_SHA256'], script_SHA256=result['script_SHA256'],
            flower={k:v for k,v in route.get('flower',{}).items() if k!='trace'},
            sword=route.get('sword'), trace=route.get('swordTrace'),
            terminal=result['receipt']['terminal'], reason=result['receipt']['reason'])), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--descent', type=int, choices=(0, 4, 5, 68), default=0)
    parser.add_argument('--collect-sword', action='store_true')
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    assert check(Old.NIGHTLY)['ROM_sha256'] == PIN
    raw = Old.NIGHTLY.read_bytes()
    Packet.extract(raw)
    from compose_karnov_scene_motor_1113 import inverse
    parent = inverse(raw)
    assert Old.digest(Old.NIGHTLY) == PIN
    assert sha256(parent).hexdigest() == BASE
    assert Packet.extract(raw) == Packet.extract(parent)
    assert raw[Packet.COOKIE:Packet.COOKIE+16].hex() == 'a726024146cc2049b14dcc581a3340fe'
    command = ['prince-current', '--flower', '--face-right', '--runout-x', '390',
               '--hold-updates', '80', '--observe-updates', '100',
               '--descent', str(args.descent)]
    try:
        with patch.multiple(Old, PIN=PIN, OUTPUT=OUTPUT,
                            run=partial(run_current, collect_sword=args.collect_sword, check_only=args.check_only)), \
                patch.object(Stage, 'controller', current_route), patch.object(sys, 'argv', command):
            Old.main()
    except CheckedController:
        assert args.check_only


if __name__ == '__main__':
    main()
