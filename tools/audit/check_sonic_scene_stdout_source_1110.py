"""Check scene-cookie opening and full-stage Lua API behavior in memory."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
from unittest.mock import patch

import check_sonic_native_scene_1110 as Scene
import check_sonic_stdout_controller_source_1110 as Opening

BASE = Opening.Base
ROOT = BASE.R
V1 = Opening.LUA
V2 = ROOT / 'tools/playthroughs/sonic_original_motion_stdout_1110_v2.lua'
FULL = ROOT / 'tools/playthroughs/sonic_original_full_stage_stdout_1110.lua'
OLD_PIN = '656cae0d855b426deffb2aba3d3965329961b300a330b350311a8c531223fabf'
COOKIE = bytes.fromhex('a72b01c0f80210577f684adf9ea78ed5')
OPEN_RUNTIME = Opening.runtime


def runtime(source, *, images=False):
    with patch.object(Opening, 'LUA', source):
        rt = OPEN_RUNTIME(images=images)
    work = rt.globals().host.work
    for bank in (2, 3):
        for offset, value in enumerate(COOKIE):
            work[bank * 8192 + 0x1fe0 + offset] = value
    return rt


def full_stage_mock(images):
    rt = runtime(FULL, images=images)
    Opening.startup(rt)
    host = rt.globals().host
    rt.execute('for i=1,1000 do host.gameMain() end')
    # Synthetic fixture writes exercise script callbacks only. The shipped
    # controller never receives these APIs or performs these writes.
    host.work[0x4000 + 0x30] = 0x88
    host.mem[0x10], host.mem[0x17], host.mem[0xbe] = 1, 6, 184
    target = host.mem[0x75] + 256 * host.mem[0x5c] + 48
    host.mem[0x76], host.mem[0x5d] = target & 255, target >> 8
    rt.execute('host.gameMain();host.event(1)')
    assert host.pad['a'] and host.pad['right']
    host.work[0x4000 + 0x30], host.work[0x4000 + 0x62] = 0x0c, 255
    host.mem[0x1e], host.mem[0xdc] = 1, 129
    rt.execute('host.gameMain()')
    host.mem[0x75], host.mem[0x5c], host.mem[0xbd], host.mem[0x0f] = 89, 12, 131, 4
    rt.execute('host.gameMain();host.event(2);host.event(1)')
    assert not host.pad['a'] and not host.pad['right']
    host.mem[0x0f], host.mem[0xbd] = 5, 158
    rt.execute('host.gameMain()')
    host.mem[0x761], host.mem[0x75], host.mem[0x5c] = 1, 40, 0
    host.mem[0x754], host.mem[0x0f] = 9, 7
    rt.execute('host.gameMain()')
    host.mem[0x754], host.mem[0x753], host.mem[0x0f] = 0, 2, 8
    host.mem[0x75], host.mem[0xbd] = 44, 48
    rt.execute('host.gameMain();host.event(2)')
    receipt, lines = BASE.result(rt)
    assert receipt['passed'] and host.status == 0, receipt
    assert receipt['native_flag']['engine'] == 4 and receipt['native_castle']['engine'] == 5
    assert receipt['native_entrance']['engine'] == 7 and receipt['active_1_2']['engine'] == 8
    jump, = receipt['jump_events']
    assert jump['reason'] == 'enemy' and jump['sampled']['saved'] & 128
    assert jump['accepted']['source_vy'][2] == 255
    assert sum(s.startswith('SMB_NATIVE_IMAGE ') for s in lines) == (2 if images else 0)
    rt.execute('host.gameMain();host.event(2)')
    assert len(host.prints) == len(lines)
    return dict(images=2 if images else 0, native_phase_callbacks=[4, 5, 7, 8],
                original_jump_sample_mock=True, physical_source_reads=host.work_reads)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert args.output.resolve().is_relative_to(ROOT / 'build') and not args.output.exists()
    assert sha256(V1.read_bytes()).hexdigest() == OLD_PIN
    assert V2.read_text() == V1.read_text().replace(Scene.OLD_COOKIE.hex(), COOKIE.hex())
    assert sha256(BASE.DLL.read_bytes()).hexdigest() == BASE.DLL_SHA
    text = FULL.read_text()
    for forbidden in ('io.open', 'emu.write', 'emu.saveState', 'emu.loadState', 'emu.reset',
                      'dofile', 'require(', 'os.execute'):
        assert forbidden not in text
    bundle = BASE.W.Symbols.bundle()
    constants = dict((name, int(value, 0)) for name, value in re.findall(
        r'(\w+)\s*=\s*(0x[0-9a-f]+)', text.split('local L={', 1)[1].split('\n}', 1)[0]))
    for name, value in constants.items():
        actual = 0x5ffe if name == 'FmAlts' else BASE.W.address(bundle, name)
        assert value == actual, (name, value, actual)
    _, _, p, _ = Scene.combined()
    assert p['packet']['cookie'] == COOKIE
    for name, value in {'SceneFeet': 0xd2e9, 'SceneSide': 0xd2f5,
                        'SceneHead': 0xd301, 'SceneBounds': 0xd310}.items():
        assert p['scene_program']['symbols'][name] == value
    with patch.object(Opening, 'runtime', side_effect=lambda images=False: runtime(V2, images=images)):
        opening = Opening.success(images=True)
    full = [full_stage_mock(False), full_stage_mock(True)]
    print(json.dumps(dict(passed=True, source_API_mock_only=True, outputs_written=0,
                          opening_SHA256=sha256(V2.read_bytes()).hexdigest(), opening=opening,
                          full_stage_SHA256=sha256(FULL.read_bytes()).hexdigest(), full_stage=full,
                          native_symbols=len(constants)), sort_keys=True), flush=True)
    assert not args.output.exists()


if __name__ == '__main__':
    main()
