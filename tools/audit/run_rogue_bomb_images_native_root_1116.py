"""View actual earned Bomb and explosion; keep the native functional receipt."""
import argparse
import json
from hashlib import sha256
from pathlib import Path
import replay_rogue_bomb_images_cb95_root_1116 as F
import build_storage_guard_v1 as Storage
from mesen_session_guard_v1 import require_free_workspace
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT = F.R/'build/smb2-flag-native-1113'


def main():
    global F
    p = argparse.ArgumentParser()
    p.add_argument('--explosion', action='store_true')
    p.add_argument('--fuse', action='store_true', help='Reproduce the retained premature-fuse observer only')
    a = p.parse_args()
    assert not(a.explosion and a.fuse)
    name = 'rogue-bomb-images-native-root-1116.json'
    if not a.fuse:
        import replay_rogue_bomb_explosion_images_cb95_root_1116 as F
        name = 'rogue-bomb-explosion-images-native-root-1116.json'
    g = json.loads((F.R/'docs/qa/allocations'/name).read_bytes())
    assert g['actual_Downloads_native_images_authorized'] and not g['game_changes_or_seeds_authorized']
    assert F.H(Path(F.__file__).read_bytes()) == g['factory_SHA256']
    raw = F.ROM.read_bytes()
    guard = check(F.ROM)
    assert F.H(raw) == g['ROM_SHA256'] and not guard['matching_patch_files']
    assert {p.name for p in OUT.iterdir() if p.is_file()} == {'candidate.nes', 'controller.lua'}
    assert (OUT/'candidate.nes').read_bytes() == raw
    text = F.controller(raw)
    assert F.H(text.encode()) == g['Lua_SHA256']
    Storage.preflight(private_root=OUT, fresh=True)
    require_free_workspace(F.R, F.ROM, allow_interactive=True)
    script = OUT/'controller.lua'
    script.write_bytes(text.encode())
    q = run(script, F.ROM, OUT/'capture', g['ROM_SHA256'], 180)
    assert F.ROM.read_bytes() == (OUT/'candidate.nes').read_bytes() == raw
    assert check(F.ROM) == guard and q['outputs_written'] == 0
    functional = dict(q['receipt'])
    functional.pop('visual', None)
    functional['Mesen_images'] = 0
    digest = sha256(json.dumps(functional, sort_keys=True).encode()).hexdigest()
    report = {k: v for k, v in q.items() if k not in ('images', 'capture_preflight')}
    report.update(actual_Downloads=True, functional_receipt_SHA256=digest,
        exact_functional_match=digest == g['functional_native_receipt_SHA256'],
        image_metadata=[{k: v for k, v in im.items() if k != 'base64'} for im in q['images']])
    for im in q['images']:
        assert im['bytes'] <= g['maximum_PNG_bytes_each']
        print('IMAGE '+json.dumps(im, separators=(',', ':')), flush=True)
    print('RESULT '+json.dumps(report, separators=(',', ':')), flush=True)
    assert q['passed'] and len(q['images']) == 2 and report['exact_functional_match']


if __name__ == '__main__':
    main()
