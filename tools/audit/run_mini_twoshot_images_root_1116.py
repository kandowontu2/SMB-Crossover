"""Private9826 two-live-fireball PNGs in RAM; exact functional replay retained."""
from hashlib import sha256
from pathlib import Path
import json
import replay_mini_twoshot_images_9826_1116 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from mesen_session_guard_v1 import require_free_workspace
from run_stdout_mesen_1110 import run

OUT = F.R/'build/smb2-flag-native-1113'
NATIVE = '531922c1508b2a7e3d9401d51f94a7a980c1a1856289f2bf7d578c9e203ed54b'


def main():
    g = json.loads((F.R/'docs/qa/allocations/mini-twoshot-images-root-1116.json').read_bytes())
    assert g['private_native_images_authorized'] and not g['Downloads_replacement_authorized']
    assert F.H(Path(F.__file__).read_bytes()) == g['factory_SHA256']
    parent = F.ROM.read_bytes()
    guard = check(F.ROM)
    assert F.H(parent) == F.C.PARENT and not guard['matching_patch_files']
    target = OUT/'candidate.nes'
    assert {p.name for p in OUT.iterdir() if p.is_file()} == {'candidate.nes', 'controller.lua'}
    assert target.read_bytes() == parent
    raw, composition = F.C.proposal(parent)
    assert composition['Sonic94_preserved'] and F.C.inverse(raw) == parent
    text = F.controller(raw, 'flower')
    assert F.H(text.encode()) == g['Lua_SHA256']
    Storage.preflight(private_root=OUT, fresh=True)
    require_free_workspace(F.R, target, allow_interactive=True)
    try:
        target.write_bytes(raw)
        assert target.read_bytes() == raw
        script = OUT/'controller.lua'
        script.write_bytes(text.encode())
        q = run(script, target, OUT/'capture', F.PIN, 180)
        assert target.read_bytes() == raw and F.ROM.read_bytes() == parent
        assert check(F.ROM) == guard and q['outputs_written'] == 0
        functional = F.functional_receipt(q['receipt'])
        digest = sha256(json.dumps(functional, sort_keys=True).encode()).hexdigest()
        report = {k: v for k, v in q.items() if k not in ('images', 'capture_preflight')}
        report.update(functional_receipt_SHA256=digest, exact_functional_match=digest == NATIVE,
                      image_metadata=[{k: v for k, v in im.items() if k != 'base64'} for im in q['images']])
        for im in q['images']:
            assert im['bytes'] <= 65536
            print('IMAGE '+json.dumps(im, separators=(',', ':')), flush=True)
        print('RESULT '+json.dumps(report, separators=(',', ':')), flush=True)
        assert q['passed'] and len(q['images']) == 2 and digest == NATIVE
    finally:
        target.write_bytes(parent)
        assert target.read_bytes() == parent and F.ROM.read_bytes() == parent
        assert check(F.ROM) == guard


if __name__ == '__main__':
    main()
