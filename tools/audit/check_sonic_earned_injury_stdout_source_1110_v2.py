"""Check the frozen Sonic injury controller's revised navigation and diagnostics."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import check_sonic_earned_injury_stdout_source_1110 as V1

LUA = V1.LUA.with_name('sonic_earned_injury_stdout_1110_v2.lua')
PIN = 'a6e1dc5caf708a6d7fbe21bc7d7d18207061befc5e9bb1972bedb2e7125b182c'
V1_PIN = '612ff932018b09e734affe19041d4f6ee4e09023d510ac1d518789df611d94dd'
MOCK_PIN = 'd10314c31111f05f9cbf2c02548529923480870e7652b058e1db8424bad527a3'


def startup(rt):
    host = rt.globals().host
    for _ in range(400):
        rt.execute('host.advance()')
        assert host.status is None
        if host.menu == 'game' and host.pad and host.pad['right']:
            break
    else:
        raise AssertionError('Mock natural Sonic menu timeout')
    assert list(host.edges.values()) == [
        'start', 'right', 'down', 'down', 'down', 'select', 'select', 'select', 'start', 'right']


def status_leak_negative():
    rt = V1.runtime(V1.OLD)
    rt.execute('host.cpu["cpu.pc"]=0x97a4;host.write(0x75b,1)')
    host = rt.globals().host
    for _ in range(400):
        rt.execute('host.advance()')
        if host.status is not None:
            break
    receipt, _ = V1.Base.result(rt)
    assert not receipt['passed'] and host.status == 1
    assert 'Native unpowered starting X40' in receipt['reason']
    assert receipt['first_active_1_1']['status'] == 1
    write, = receipt['observed_status_writes']
    assert (write['old'], write['new'], write['pc']) == (0, 1, 0x97a4)
    return dict(rejected=True, observed_write=write)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert args.output.resolve().is_relative_to(V1.ROOT / 'build') and not args.output.exists()
    assert sha256(Path(V1.__file__).read_bytes()).hexdigest() == MOCK_PIN
    assert sha256(V1.LUA.read_bytes()).hexdigest() == V1_PIN
    assert sha256(LUA.read_bytes()).hexdigest() == PIN
    assert sha256(V1.Base.DLL.read_bytes()).hexdigest() == V1.Base.DLL_SHA
    with patch.object(V1, 'LUA', LUA), patch.object(V1.Opening, 'startup', startup):
        paths = [V1.run(V1.OLD), V1.run(V1.NEW)]
        negative = status_leak_negative()
    print(json.dumps(dict(passed=True, source_API_mock_only=True, outputs_written=0,
                          Lua_SHA256=PIN, mock_paths=paths, status_leak_negative=negative),
                     sort_keys=True), flush=True)
    assert not args.output.exists()


if __name__ == '__main__':
    main()
