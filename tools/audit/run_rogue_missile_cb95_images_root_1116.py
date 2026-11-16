"""Privatecb95 earned missile PNGs in RAM; functional native receipt exact."""
from hashlib import sha256
from pathlib import Path
import json
import compose_rogue_missile_9826_1116 as C
import replay_rogue_missile_cb95_images_1116 as F
import build_storage_guard_v1 as Storage
from nightly_patch_guard_v1 import check
from mesen_session_guard_v1 import require_free_workspace
from run_stdout_mesen_1110 import run

OUT = C.R/'build/smb2-flag-native-1113'
NATIVE = '5b4fb48db68d93793c1f7db250e777e35d6d54117137f5d193a75eb61d144e4e'


def main():
    g = json.loads((C.R/'docs/qa/allocations/rogue-missile-cb95-images-root-1116.json').read_bytes())
    assert g['private_native_images_authorized'] and not g['Downloads_replacement_authorized']
    assert C.H(Path(F.__file__).read_bytes()) == g['factory_SHA256']
    parent = C.ROM.read_bytes()
    guard = check(C.ROM)
    assert C.H(parent) == C.PARENT and not guard['matching_patch_files']
    target = OUT/'candidate.nes'
    assert {p.name for p in OUT.iterdir() if p.is_file()} == {'candidate.nes', 'controller.lua'}
    assert target.read_bytes() == parent
    raw, proof = C.proposal(parent)
    assert proof['protected'] == ['Mini20', 'Sonic94'] and C.inverse(raw) == parent
    text = F.controller(raw)
    assert C.H(text.encode()) == g['Lua_SHA256']
    Storage.preflight(private_root=OUT, fresh=True)
    require_free_workspace(C.R, target, allow_interactive=True)
    try:
        target.write_bytes(raw)
        assert target.read_bytes() == raw
        script = OUT/'controller.lua'
        script.write_bytes(text.encode())
        q = run(script, target, OUT/'capture', C.CANDIDATE, 180)
        assert target.read_bytes() == raw and C.ROM.read_bytes() == parent
        assert check(C.ROM) == guard and q['outputs_written'] == 0
        functional = dict(q['receipt'])
        functional.pop('visual', None)
        functional['Mesen_images'] = 0
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
        assert target.read_bytes() == parent and C.ROM.read_bytes() == parent
        assert check(C.ROM) == guard


if __name__ == '__main__':
    main()
