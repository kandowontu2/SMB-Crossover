"""Root single queue: Mini supported L/F transactions from actual Downloads."""
import argparse
import json
from pathlib import Path
import replay_mini_oneup_support_contact_1327_1116 as Life
import replay_mini_flower_1327_1116 as Flower
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from mesen_session_guard_v1 import require_free_workspace
from run_stdout_mesen_1110 import run

OUT = Life.R/'build/smb2-flag-native-1113'


def compact(value):
    if isinstance(value, dict):
        return {k: compact(v) for k, v in value.items()}
    if isinstance(value, list):
        if len(value) > 8:
            return dict(count=len(value), first=compact(value[:2]), last=compact(value[-2:]))
        return [compact(v) for v in value]
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--kind', choices=('oneup', 'flower', 'both'), default='both')
    kind = parser.parse_args().kind
    grant = json.loads((Life.R/'docs/qa/allocations/mini-supported-stock-downloads-root-1116.json').read_bytes())
    assert grant['actual_Downloads_native_authorized']
    assert not grant['ROM_replacement_or_gameplay_seeds_authorized']
    raw = Life.ROM.read_bytes()
    before = check(Life.ROM)
    assert Life.H(raw) == Life.PIN == grant['ROM_SHA256'] and not before['matching_patch_files']
    assert {p.name for p in OUT.iterdir() if p.is_file()} == {'candidate.nes', 'controller.lua'}
    assert (OUT/'candidate.nes').read_bytes() == raw
    for key in (('oneup', 'flower') if kind == 'both' else (kind,)):
        factory = Life if key == 'oneup' else Flower
        g = grant['cases'][key]
        assert factory.H(Path(factory.__file__).read_bytes()) == g['factory_SHA256']
        assert factory.R == Life.R and factory.ROM == Life.ROM and factory.PIN == Life.PIN
        text = factory.controller(raw, key)
        assert factory.H(text.encode()) == g['Lua_SHA256']
        Storage.preflight(private_root=OUT, fresh=True)
        require_free_workspace(Life.R, Life.ROM, allow_interactive=True)
        script = OUT/'controller.lua'
        script.write_bytes(text.encode())
        q = run(script, Life.ROM, OUT/'capture', Life.PIN, 180)
        assert Life.ROM.read_bytes() == (OUT/'candidate.nes').read_bytes() == raw
        assert check(Life.ROM) == before and not q['images'] and q['outputs_written'] == 0
        assert q['script_SHA256'] == g['Lua_SHA256']
        report = {k: v for k, v in q.items() if k not in ('images', 'capture_preflight', 'receipt')}
        report.update(kind=key, actual_Downloads=True, receipt=compact(q['receipt']))
        print('RESULT '+json.dumps(report, separators=(',', ':')), flush=True)
        assert q['passed'], 'Retain actual native negative before changing controls'
        r = q['receipt']
        assert not r['game_state_writes'] and r['gameplay_seeds'] == 0
        assert all(not v for k, v in r.items() if k.startswith('pending'))
        for name in ('Main', 'MiniMovement', 'MiniStep'):
            assert r[name+'_entries'] == r[name+'_returns']
        assert (r['terminal']['tier'], r['terminal']['lives']) == ((1, 3) if key == 'oneup' else (2, 2))
        assert r['item']['resumed_steps'] == r['item']['resumed_moves'] == 25
        assert r['item']['native_pickups'] == r['item']['primary_leaf_entries'] == r['item']['vector24_entries'] == 1
        assert r['item']['leaf_return']['C'] == 1
        birth = r['item']['manual_birth']
        assert birth['width'] == 32 and birth['manual_vertical'] and birth['actor']['id'] == 37
        assert birth['initial_center'] == birth['initial_left']+16


if __name__ == '__main__':
    main()
