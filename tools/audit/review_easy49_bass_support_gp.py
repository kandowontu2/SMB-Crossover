"""Classify every accepted Bass launch on the exact independently verified EL route."""
from pathlib import Path
import hashlib
import importlib.util
import json
from collections import Counter

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
P = R / 'build/roster-through-2-2'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = V / 'root49-el-bass-support-gp.json'
    assert not out.exists()
    fixed = P / 'root49gl-bass-fixed-9-v0-mmc3'
    probe = P / 'root49go-bass-support-9-v0-mmc3'
    assert (fixed / 'trace.csv').read_bytes() == (probe / 'trace.csv').read_bytes()
    assert (fixed / 'inputs.csv').read_bytes() == (probe / 'inputs.csv').read_bytes()
    parser = V / 'agent49g-samus-crouch-fix-proposal-b/image.py'
    s = importlib.util.spec_from_file_location('bass_support_review_image', parser)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    im = m.Image(V / 'root49-link-watch-ej/source/build/smb-crossover-mmc3.nes')
    assert sha(im.path) == '2872f04b870ad72cb54b22a67a10333995151a501282c6535f3adfbe0ae32060'
    symbol = im.sym('MTileAttribute')
    segment = im.segs[symbol['seg']]
    offset = segment['ooffs'] + symbol['val'] - segment['start']
    attrs = im.raw[offset:offset+256]
    events = [json.loads(s) for s in (probe / 'support-events.jsonl').read_text().splitlines()]
    classified, counts = [], Counter()
    for z in events:
        if z['event'] != 'Launch':
            continue
        assert z['fresh'] & 128 and z['yHigh'] == 1
        if z['state'] != 0:
            assert z['state'] in (1, 2) and z['jumpUsed'] == 1
            kind = 'accepted_air_secondary_jump'
        elif z['springAnimation']:
            assert z['springAnimation'] == 2 and z['tile2'] == z['tile13'] == 0x67
            spring = [a for a in z['actors'] if a[1] == 1 and a[2] == 50
                and abs(a[4]-z['x']) <= 16 and a[5] == z['feetY']]
            assert len(spring) == 1
            kind = 'actual_compressed_spring'
            z['support_actor'] = spring[0]
        elif (attrs[z['tile2']] & 1) or (attrs[z['tile13']] & 1):
            assert z['feetY'] % 16 == 0
            kind = 'actual_terrain_at_native_feet'
        else:
            supports = [a for a in z['actors'] if a[1] == 1 and a[2] in (37, 38, 39, 40)
                and a[5] == z['feetY'] and a[6] == a[0]]
            assert len(supports) == 1, z
            kind = 'actual_platform_with_own_collision_token'
            z['support_actor'] = supports[0]
        counts[kind] += 1
        classified.append(dict(classification=kind, **z))
    assert counts == dict(accepted_air_secondary_jump=103, actual_compressed_spring=1,
        actual_terrain_at_native_feet=128, actual_platform_with_own_collision_token=6)
    binding = V / 'root49-el-bass-support-go/binding.json'
    b = json.loads(binding.read_text())
    assert sha(V / 'root49-el-bass-support-go/core.lua') == b['core_sha256']
    refs = {}
    for folder in (probe, V / 'root49-el-bass-support-go'):
        for p in folder.iterdir():
            if p.is_file():
                refs[p.relative_to(R).as_posix()] = dict(sha256=sha(p), bytes=p.stat().st_size)
    report = dict(status='PASS_ALL238_ACTUAL_ACCEPTED_BASS_LAUNCHES_SCOPED_SUPPORT_AUDIT',
        script_sha256=sha(__file__), counts=dict(counts), accepted_grounded_launches=135,
        exact_GL_trace_all21_fields_and_input_bytes=True, endpoint_frames=26689,
        no_unknown_support_or_corner_catch_needed=True,
        method='Actual bank/eight-byte ExpandedMovement::Launch, LandPlyr and StopPlayerMove hooks. Grounded launches use actual2/13 feet adders, static solid metatile alignment, live platform Y+own collision token, or the actual compressed spring actor/animation.',
        qualifications=['This audits accepted launches, not ignored A presses or a claim of complete Flash movement parity.',
            'Air launches have actual native airborne state and consumed secondary-jump token1; the source-port rule remains separately qualified.',
            'No new ROM/source change, emulator write, save load, arsenal test, movie or perceptual certification.'],
        all_launch_receipts=classified, runtime_changes=False, accepted_release=False,
        goal_complete=False, references=refs)
    out.write_text(json.dumps(report, indent=2)+'\n')
    print(report['status'], dict(counts), sha(out))


if __name__ == '__main__':
    main()
