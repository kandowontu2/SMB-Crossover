"""Return two actual bounded RAM pictures without making capture files."""
from hashlib import sha256
import json
from pathlib import Path
import replay_celeste_flower_images_00bb_1116 as F
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT = F.R/'build/smb2-flag-native-1113'
GRANT = F.R/'docs/qa/allocations/celeste-images-downloads-root-1116.json'


def main():
    g = json.loads(GRANT.read_bytes())
    assert g['actual_Downloads_native_images_authorized'] and not g['ROM_replacement_authorized']
    assert F.digest(Path(F.__file__).read_bytes()) == g['factory_SHA256']
    raw = F.ROM.read_bytes()
    guard = check(F.ROM)
    assert F.digest(raw) == F.PIN == g['ROM_SHA256']
    assert {p.name for p in OUT.iterdir() if p.is_file()} == {'candidate.nes', 'controller.lua'}
    assert (OUT/'candidate.nes').read_bytes() == raw
    text = F.controller(raw, 'flower')
    assert F.digest(text.encode()) == g['Lua_SHA256']
    Storage.preflight(private_root=OUT, reserved_bytes=0, reserved_files=0, fresh=True)
    require_free_workspace(F.R, F.ROM, allow_interactive=True)
    script = OUT/'controller.lua'
    script.write_bytes(text.encode())
    q = run(script, F.ROM, OUT/'capture', F.PIN, 240)
    assert F.ROM.read_bytes() == (OUT/'candidate.nes').read_bytes() == raw and check(F.ROM) == guard
    assert q['outputs_written'] == 0 and q['script_SHA256'] == g['Lua_SHA256']
    functional = F.functional_receipt(q['receipt'])
    functional_sha = sha256(json.dumps(functional, sort_keys=True).encode()).hexdigest()
    report = {k: v for k, v in q.items() if k not in ('images', 'capture_preflight')}
    report.update(actual_Downloads=True, functional_receipt_SHA256=functional_sha,
                  exact_functional_receipt_match=functional_sha == g['functional_native_receipt_SHA256'],
                  image_metadata=[{k: v for k, v in im.items() if k != 'base64'} for im in q['images']])
    for im in q['images']:
        assert im['bytes'] <= g['maximum_PNG_bytes_each']
        print('IMAGE '+json.dumps(im, separators=(',', ':')), flush=True)
    print('RESULT '+json.dumps(report, separators=(',', ':')), flush=True)
    assert q['passed'] and report['exact_functional_receipt_match']
    assert len(q['images']) == g['maximum_images']


if __name__ == '__main__':
    main()
