"""Root native queue: actual Mini recovery/Star/support transaction."""
import json
from pathlib import Path
import replay_mini_star_music_1327_1116 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from mesen_session_guard_v1 import require_free_workspace
from run_stdout_mesen_1110 import run
from run_mini_supported_stock_downloads_root_1116 import compact

OUT = F.R/'build/smb2-flag-native-1113'


def main():
    g = json.loads((F.R/'docs/qa/allocations/mini-star-downloads-root-1116.json').read_bytes())
    assert g['actual_Downloads_native_authorized']
    assert not g['ROM_replacement_or_gameplay_seeds_authorized']
    assert F.H(Path(F.__file__).read_bytes()) == g['factory_SHA256']
    raw = F.ROM.read_bytes()
    before = check(F.ROM)
    assert F.H(raw) == F.PIN == g['ROM_SHA256'] and not before['matching_patch_files']
    assert {p.name for p in OUT.iterdir() if p.is_file()} == {'candidate.nes', 'controller.lua'}
    assert (OUT/'candidate.nes').read_bytes() == raw
    text = F.controller(raw, 'star')
    assert F.H(text.encode()) == g['Lua_SHA256']
    Storage.preflight(private_root=OUT, fresh=True)
    require_free_workspace(F.R, F.ROM, allow_interactive=True)
    script = OUT/'controller.lua'
    script.write_bytes(text.encode())
    q = run(script, F.ROM, OUT/'capture', F.PIN, 180)
    assert F.ROM.read_bytes() == (OUT/'candidate.nes').read_bytes() == raw
    assert check(F.ROM) == before and not q['images'] and q['outputs_written'] == 0
    assert q['script_SHA256'] == g['Lua_SHA256']
    report = {k: v for k, v in q.items() if k not in ('images', 'capture_preflight', 'receipt')}
    report.update(actual_Downloads=True, receipt=compact(q['receipt']))
    print('RESULT '+json.dumps(report, separators=(',', ':')), flush=True)
    assert q['passed'], 'Retain actual native negative before changing controls'
    r = q['receipt']
    assert not r['game_state_writes'] and r['gameplay_seeds'] == 0
    assert all(not v for k, v in r.items() if k.startswith('pending'))
    assert (r['terminal']['tier'], r['terminal']['lives'], r['terminal']['power']) == (0, 2, 0)
    assert r['item']['resumed_steps'] == r['item']['resumed_moves'] == 25
    assert r['item']['native_pickups'] == r['item']['primary_leaf_entries'] == r['item']['vector24_entries'] == 1
    assert r['item']['leaf_return']['C'] == 1
    assert r['item']['music64_writer']['value'] == 64
    assert r['item']['credit']['after']-r['item']['credit']['before'] == 1000
    assert r['item']['manual_birth']['width'] == 32
    assert r['route']['injury']['returned']


if __name__ == '__main__':
    main()
