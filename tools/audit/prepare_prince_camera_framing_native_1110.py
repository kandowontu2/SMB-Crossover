"""Materialize the qualified Prince camera image and its two native controls."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

from prepare_prince_full11_1110 import once
from prepare_prince_primary_align_native_1110 import (
    CANDIDATE as PARENT, CHR_START, COOKIE, NEW_COOKIE as PARENT_COOKIE,
    OUT as PRIOR, R, SYMBOLS, checked, read,
)
from prepare_selected_native_packet_v1 import prepare, sha


OUT = R / 'build/prince-camera-framing-native-1110'
PROOF = R / 'build/prince-camera-framing-1110/proof.json'
ROUTE = R / 'tools/playthroughs/prince_camera_framing_1110.lua'
BASE = PRIOR / 'prince-private.nes'
V8 = PRIOR / 'native'
PIN = 'bd9f111d79adb0700b968cd0b10459818ef28669ac21c9ede1aa5ebca6ea79dc'
NEW_COOKIE = bytes.fromhex('a726020a76ab288cb09bfb9977ff5d52')
PINS = {
    PROOF: '3a2d7be47b7f867a939f8ce4de5f1c6b9407cd729332b53e0e74fc73642765a6',
    V8 / 'ready.json': 'c91e3ce9e3b3749a9adecf0507bcee0ef5e8441c0ebded742b05448303d98665',
    V8 / 'controller.lua': '28f4a9e9943c389ca392d4ce8447ea4b21541fcc4feb35b9fa88762a26d5af9b',
    BASE: PARENT,
}


def rebuild(proof, old):
    assert len(old) == 2_097_168 and old[COOKIE:COOKIE + 16] == PARENT_COOKIE
    assert proof['passed'] and not proof['ROM_written'] and not proof['Mesen_run']
    assert (proof['parent_SHA256'], proof['expected_memory_only_SHA256']) == (PARENT, PIN)
    assert proof['Prince_cookie'] == NEW_COOKIE.hex()
    assert proof['layout']['worker'] == [0xd622, 0xd665]
    assert proof['layout']['rebased_tail'] == [0xdabf, 0xdac2]
    assert proof['direct_positions'] == 816 and proof['poses']['actual_native_poses'] == 408
    assert proof['real_vectors']['cuts'] == {'IRQ': 48, 'lagNMI': 48}
    late = proof['flat_corridor']['corrected'][-20:]
    assert (min(row['relative'] for row in late), max(row['relative'] for row in late)) == (119, 124)
    extents = {COOKIE: 16, **{CHR_START + page * 1024: 1024 for page in (617, 691, 692, 693, 695, 795, 291, 514)}}
    # The final carrier row ends at the authenticated packed-payload extent.
    extents[CHR_START + 514 * 1024] = proof['layout']['payload_bytes'] - 43 * 1024
    result = bytearray(old)
    for row in proof['patches']:
        at = row['offset']
        previous = bytes.fromhex(row['preimage'])
        replacement = bytes.fromhex(row['replacement'])
        assert len(previous) == len(replacement) == extents.pop(at)
        assert previous != replacement and old[at:at + len(previous)] == previous
        result[at:at + len(replacement)] = replacement
    assert not extents and result[COOKIE:COOKIE + 16] == NEW_COOKIE
    assert sha256(result).hexdigest() == PIN
    return result


def controller(opening):
    text = (V8 / 'controller.lua').read_text(encoding='utf-8')
    text = once(text, f'Q.ROM_sha256="{PARENT}"', f'Q.ROM_sha256="{PIN}"')
    cookie = lambda raw: 'Q.cookie={' + ','.join(map(str, raw)) + '}'
    text = once(text, cookie(PARENT_COOKIE), cookie(NEW_COOKIE))
    mode = 'Prince-camera-opening-1110' if opening else 'Prince-camera-full11-1110'
    text = once(text, 'Q.mode="Prince-original-first-pipe193"',
                f'Q.mode="{mode}";Q.cameraOpening={str(opening).lower()}')
    first = text.index('local function thirdCameraRoute(')
    end = text.index('local function controls_tick(finish)', first)
    text = text[:first] + ROUTE.read_text(encoding='utf-8') + '\n\n' + text[end:]
    anchor = 'local function controls_tick(finish)'
    text = once(text, anchor, anchor + '\n cameraSample()\n if completeCameraOpening(finish) then return end')
    if opening:
        text = once(text, '"full_stage":true,"helpers_added":false', '"full_stage":false,"helpers_added":false')
    assert 'emu.write(' not in text and text.count(PIN) == 1
    assert 'third-cam-' not in text and 'postPitPads' not in text and 'koopa-brake' not in text
    sys.path.insert(0, str(R / 'build/smb2-final62-observer-lua-deps-v1'))
    from lupa.lua54 import LuaRuntime
    assert LuaRuntime().eval('function(s) local f,e=load(s); assert(f,e); return true end')(text)
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve()
    assert out == OUT and not out.exists(), out
    direct = checked(PINS)
    proof, prior = map(read, (PROOF, V8 / 'ready.json'))
    assert prior['ROM_sha256'] == PARENT and prior['prepared'] and not prior['emulated_writes']
    inputs = direct | checked(prior['bindings']) | checked(proof['bindings'])
    image = rebuild(proof, BASE.read_bytes())
    controllers = {name: controller(opening) for name, opening in (('opening', True), ('full11', False))}
    out.mkdir()
    rom = out / 'prince-private.nes'
    rom.write_bytes(image)
    manifest = out / 'candidate.json'
    receipt = dict(prepared=True, private=True, parent_SHA256=PARENT, candidate_SHA256=PIN,
                   Prince_cookie=NEW_COOKIE.hex(), proof_SHA256=direct[PROOF], native_pending=True,
                   source_bindings={str(path.relative_to(R)): sha(path) for path in (Path(__file__), ROUTE)},
                   controller_SHA256={name: sha256(text.encode()).hexdigest() for name, text in controllers.items()})
    manifest.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    for name, source in controllers.items():
        scope = ('Opening 1-1 cold menu/DMA, ordinary forward input and actual viewport sample.' if name == 'opening' else
                 'Native 1-1 attempt with authored pipe and pit crossings, actual enemies and ordinary inputs.')
        prepare(out / name, rom, source, {Path(__file__), ROUTE, manifest, *inputs}, expected=PIN,
                timeout=prior['timeout'], allow_interactive=prior['allow_interactive'],
                scope=scope + ' No camera-dependent route steering.', rom_symbols=SYMBOLS)
    assert sum(path.is_file() for path in out.rglob('*')) == 8


if __name__ == '__main__':
    main()
