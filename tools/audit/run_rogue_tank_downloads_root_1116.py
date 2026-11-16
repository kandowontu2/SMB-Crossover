"""Root single-queue actual Downloads Rogue tank; reporting-tag adapter only."""
import json
from pathlib import Path
import replay_rogue_natural_tank_1327_1116 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from mesen_session_guard_v1 import require_free_workspace
from run_stdout_mesen_1110 import run

OUT = F.R/'build/smb2-flag-native-1113'


def main():
    grant = json.loads((F.R/'docs/qa/allocations/rogue-tank-downloads-root-1116.json').read_bytes())
    assert grant['actual_Downloads_native_authorized']
    assert not grant['ROM_replacement_or_gameplay_seeds_authorized']
    assert F.H(Path(F.__file__).read_bytes()) == grant['factory_SHA256']
    raw = F.ROM.read_bytes()
    before = check(F.ROM)
    assert F.H(raw) == F.PIN == grant['ROM_SHA256'] and not before['matching_patch_files']
    assert {p.name for p in OUT.iterdir() if p.is_file()} == {'candidate.nes', 'controller.lua'}
    assert (OUT/'candidate.nes').read_bytes() == raw
    source = F.controller(raw)
    assert F.H(source.encode()) == grant['source_Lua_SHA256']
    old, new = 'ROGUE_STOCK_RECEIPT ', 'SMB_NATIVE_RECEIPT '
    assert source.count(old) == 1 and new not in source
    text = source.replace(old, new, 1)
    assert text.replace(new, old, 1) == source
    F.LuaRuntime().compile(text)
    Storage.preflight(private_root=OUT, fresh=True)
    require_free_workspace(F.R, F.ROM, allow_interactive=True)
    script = OUT/'controller.lua'
    script.write_bytes(text.encode())
    q = run(script, F.ROM, OUT/'capture', F.PIN, 180)
    assert F.ROM.read_bytes() == (OUT/'candidate.nes').read_bytes() == raw
    assert check(F.ROM) == before and not q['images'] and q['outputs_written'] == 0
    assert q['script_SHA256'] == F.H(text.encode())
    report = {k: v for k, v in q.items() if k not in ('images', 'capture_preflight')}
    report.update(actual_Downloads=True, source_Lua_SHA256=grant['source_Lua_SHA256'],
                  reporting_tag_only_changed=True)
    print('RESULT '+json.dumps(report, separators=(',', ':')), flush=True)
    assert q['passed'], 'Retain actual native negative before changing controls'
    r = q['receipt']
    assert not r['game_state_writes'] and r['pending_scopes'] == 0
    assert r['terminal']['tanks'] == 1 and r['terminal']['health_raw'] == [153, 25]
    assert r['terminal']['lives'] == 2 and r['terminal']['status'] == 1
    boxes = r['collector']['physical_boxes']
    p, a = boxes['player'], boxes['item']
    assert min(p[2], a[2])-max(p[0], a[0])+1 > 0
    assert min(p[3], a[3])-max(p[1], a[1])+1 > 0
    assert all(r['score_credit']['postcredit_returned'][n] >= 25
               for n in ('RdControlStep', 'RdLifeMovement', 'GameLoop'))


if __name__ == '__main__':
    main()
