"""Root native queue: both ordinary Rogue tank transactions from Downloads."""
import json
from pathlib import Path
import replay_rogue_natural_mf_1327_1116 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from mesen_session_guard_v1 import require_free_workspace
from run_stdout_mesen_1110 import run

OUT = F.R/'build/smb2-flag-native-1113'


def main():
    g = json.loads((F.R/'docs/qa/allocations/rogue-mf-downloads-root-1116.json').read_bytes())
    assert g['actual_Downloads_native_authorized']
    assert not g['ROM_replacement_or_gameplay_seeds_authorized']
    assert F.H(Path(F.__file__).read_bytes()) == g['factory_SHA256']
    raw = F.ROM.read_bytes()
    before = check(F.ROM)
    assert F.H(raw) == F.PIN == g['ROM_SHA256'] and not before['matching_patch_files']
    assert {p.name for p in OUT.iterdir() if p.is_file()} == {'candidate.nes', 'controller.lua'}
    assert (OUT/'candidate.nes').read_bytes() == raw
    text = F.controller(raw)
    assert F.H(text.encode()) == g['Lua_SHA256']
    Storage.preflight(private_root=OUT, fresh=True)
    require_free_workspace(F.R, F.ROM, allow_interactive=True)
    script = OUT/'controller.lua'
    script.write_bytes(text.encode())
    q = run(script, F.ROM, OUT/'capture', F.PIN, 180)
    assert F.ROM.read_bytes() == (OUT/'candidate.nes').read_bytes() == raw
    assert check(F.ROM) == before and not q['images'] and q['outputs_written'] == 0
    assert q['script_SHA256'] == g['Lua_SHA256']
    report = {k: v for k, v in q.items() if k not in ('images', 'capture_preflight')}
    report['actual_Downloads'] = True
    print('RESULT '+json.dumps(report, separators=(',', ':')), flush=True)
    assert q['passed'], 'Retain actual native negative before changing controls'
    r = q['receipt']
    assert not r['game_state_writes'] and r['pending_scopes'] == 0
    assert (r['terminal']['tanks'], r['terminal']['gear'], r['terminal']['lives'],
            r['terminal']['missiles'], r['terminal']['max_missiles']) == (1, 0, 2, 5, 5)
    m = r['completed_tank_gate']
    for collector, credit in ((m['collector'], m['credit']), (r['collector'], r['score_credit'])):
        p, a = collector['physical_boxes']['player'], collector['physical_boxes']['item']
        assert min(p[2], a[2])-max(p[0], a[0])+1 > 0
        assert min(p[3], a[3])-max(p[1], a[1])+1 > 0
        assert collector['C'] == 1
        assert credit['writer']['after']-credit['writer']['before'] == 1000
        assert all(credit['postcredit_returned'][n] >= 25
                   for n in ('RdControlStep', 'RdLifeMovement', 'GameLoop'))
    assert m['collector']['after']['health_raw'] == [153, 25]
    assert r['collector']['before']['health_raw'] == r['collector']['after']['health_raw'] == r['terminal']['health_raw']


if __name__ == '__main__':
    main()
