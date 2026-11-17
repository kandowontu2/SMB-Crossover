"""Native passive HUD continuity over the unchanged naturally earned Bomb run."""
import json
from hashlib import sha256
from pathlib import Path
import replay_rogue_hud_continuity_cb95_1116 as F
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

R = Path(__file__).resolve().parents[2]
OUT = R/'build/smb2-flag-native-1113'
ROM = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')


def H(raw):
    return sha256(raw).hexdigest()


def main():
    g = json.loads((R/'docs/qa/allocations/rogue-hud-continuity-native-root-1116.json').read_bytes())
    assert g['actual_Downloads_native_diagnostic_authorized'] and not g['game_changes_or_seeds_authorized']
    assert H(Path(F.__file__).read_bytes()) == g['factory_SHA256']
    raw = ROM.read_bytes()
    guard = check(ROM)
    assert H(raw) == g['ROM_SHA256'] and not guard['matching_patch_files']
    assert {p.name for p in OUT.iterdir() if p.is_file()} == {'candidate.nes', 'controller.lua'}
    assert (OUT/'candidate.nes').read_bytes() == raw
    text = F.controller(raw, source=False)
    assert H(text.encode()) == g['Lua_SHA256']
    Storage.preflight(private_root=OUT, fresh=True)
    require_free_workspace(R, ROM, allow_interactive=True)
    script = OUT/'controller.lua'
    script.write_bytes(text.encode())
    q = run(script, ROM, OUT/'capture', g['ROM_SHA256'], 180)
    assert ROM.read_bytes() == (OUT/'candidate.nes').read_bytes() == raw
    assert check(ROM) == guard and q['outputs_written'] == 0 and not q['images']
    functional = dict(q['receipt'])
    diagnostic = functional.pop('hud_continuity', None)
    digest = sha256(json.dumps(functional, sort_keys=True).encode()).hexdigest()
    report = {k: v for k, v in q.items() if k not in ('images', 'capture_preflight')}
    report.update(actual_Downloads=True, functional_receipt_SHA256=digest,
        exact_functional_match=digest == g['functional_native_receipt_SHA256'])
    print('RESULT '+json.dumps(report, separators=(',', ':')), flush=True)
    assert q['passed'] and diagnostic and report['exact_functional_match']


if __name__ == '__main__':
    main()
