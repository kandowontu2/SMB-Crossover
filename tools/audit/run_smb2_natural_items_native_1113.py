"""Root's serial current-Downloads native SMB2/Doki item qualification."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import replay_smb2_natural_powerups_1113 as Replay
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

R = Path(__file__).resolve().parents[2]
OUT = R / 'build/smb2-flag-native-1113'
NIGHTLY = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PINS = {
    4: '36e52aae4abee6a26a42dd396239137d41195e4fe72ab85dfd0dfcb75b3bb81d',
    0: '18ffdb276851310ca47b3cf81b4c6296553c51880973fe821bda4ba5ac604637',
}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--variant', choices=tuple(str(i) for i in range(8)) + ('all',), default='4')
    p.add_argument('--mode', choices=Replay.MODES, default='injured-mushroom')
    p.add_argument('--metadata', action='store_true')
    p.add_argument('--skip', type=int, choices=range(8), nargs='*', default=[])
    args = p.parse_args()
    assert check(NIGHTLY)['ROM_sha256'] == Replay.PIN
    raw = NIGHTLY.read_bytes()
    variants = range(8) if args.variant == 'all' else (int(args.variant),)
    assert OUT.is_dir() and {p.name for p in OUT.iterdir()} == {'candidate.nes', 'controller.lua'}
    candidate_before = sha256((OUT / 'candidate.nes').read_bytes()).hexdigest()
    for variant in variants:
        if variant in args.skip:
            continue
        text = Replay.controller(raw, variant, args.mode)
        script_sha = sha256(text.encode()).hexdigest()
        if args.mode == 'injured-mushroom' and variant in PINS:
            assert script_sha == PINS[variant]
        summary = dict(ROM_SHA256=Replay.PIN, variant=variant,
                       identity=Replay.Root.NAMES[variant], item_mode=args.mode,
                       script_SHA256=script_sha, native_run=not args.metadata,
                       launch_context='actual Downloads', candidate_installed=False)
        if not args.metadata:
            script = OUT / 'controller.lua'
            script.write_text(text, encoding='utf-8', newline='\n')
            q = run(script, NIGHTLY, OUT / 'capture', Replay.PIN, 180)
            r = q['receipt']
            natural = r.get('natural', {})
            compact = {k: r.get(k) for k in ('passed', 'reason', 'physical_frames',
                'all_returned_Main', 'terminal', 'capture_files', 'runtime_state_writes')}
            compact['natural'] = {k: natural.get(k) for k in ('opening', 'injuries',
                'heads', 'prepares', 'birth', 'pickups', 'phase', 'since')}
            summary.update(passed=q['passed'], receipt_SHA256=q['receipt_SHA256'],
                           receipt=compact, outputs_written=q['outputs_written'])
        print(json.dumps(summary, separators=(',', ':')), flush=True)
        if not args.metadata:
            assert q['passed'], 'Native natural SMB2/Doki item qualification failed'
    assert sha256((OUT / 'candidate.nes').read_bytes()).hexdigest() == candidate_before
    assert check(NIGHTLY)['ROM_sha256'] == Replay.PIN


if __name__ == '__main__':
    main()
