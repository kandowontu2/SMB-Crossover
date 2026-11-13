"""Root's private native first-item/first-pipe checks for the pinned successor."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import compose_dkjr_descending_platform_1113 as C
import replay_dkjr_descending_platform_1113 as Replay
from check_ff_stdout_controller_source_1110 import LuaRuntime
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

NIGHTLY = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
OUT = Path(__file__).resolve().parents[2] / 'build/metal-flower-native-1112'
PARENT = '7ef2de351d3a4ae60b3ada2eb1aa56b330873dc106ad43428ec6803bf420d4fc'
PUBLIC_BUB = 'f88cfe5aee15bb3921c691b7f06d905246be9ff88b9b43eea71c2405722724a7'
PINS = {
    'first-item': 'b784ed4ed57a051231424e1f603dda8b160a34b749d23138649ae7d463fe4a47',
    'first-pipe': '65af12f18021d30e47bd9f4022c01148bf295da76017f744acc38456345b90b8',
}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--route', choices=tuple(PINS), required=True)
    p.add_argument('--metadata', action='store_true')
    p.add_argument('--reuse', action='store_true', help='Reuse the already composed exact14ae private file; no repeated parent build.')
    args = p.parse_args()
    public_now = check(NIGHTLY)['ROM_sha256']
    assert public_now in (PARENT, PUBLIC_BUB)
    raw = NIGHTLY.read_bytes()
    if public_now == PUBLIC_BUB:
        import bub_native_noops_1113 as Bub
        raw = Bub.combined_reverse(raw)
        assert sha256(raw).hexdigest() == PARENT
    if args.reuse:
        image = (OUT / 'candidate.nes').read_bytes()
        assert sha256(image).hexdigest() == C.PIN
        assert sha256(C.reverse(image)).hexdigest() == C.PARENT
    else:
        image, info = C.compose_current(raw)
        assert sha256(image).hexdigest() == C.PIN
        assert C.P.inverse_current(C.reverse(image)) == raw
        assert info['new_RAM_bytes'] == info['new_CHR_bytes'] == 0
    if args.route == 'first-item':
        text = C.controller(image)
    else:
        text = Replay.controller(image, pipes=(1,), stop_after_pipe=1)
    assert sha256(text.encode()).hexdigest() == PINS[args.route]
    LuaRuntime().compile(text)
    summary = dict(ROM_SHA256=C.PIN, parent_SHA256=PARENT, current_Downloads_SHA256=public_now, route=args.route,
                   Lua_SHA256=PINS[args.route], private_only=True, installed=False,
                   native_run=not args.metadata, reused_exact_private_candidate=args.reuse)
    if not args.metadata:
        assert OUT.is_dir()
        assert {p.name for p in OUT.iterdir() if p.is_file()} == {'candidate.nes', 'controller.lua'}
        rom, script = OUT / 'candidate.nes', OUT / 'controller.lua'
        rom.write_bytes(image)
        script.write_text(text, encoding='utf-8', newline='\n')
        q = run(script, rom, OUT / 'capture', C.PIN, 240)
        receipt = {k: v for k, v in q['receipt'].items() if k != 'events'}
        receipt['last_events'] = q['receipt'].get('events', [])[-12:]
        summary.update(passed=q['passed'], receipt_SHA256=q['receipt_SHA256'],
                       receipt=receipt, outputs_written=q['outputs_written'])
    print(json.dumps(summary, separators=(',', ':')), flush=True)
    assert check(NIGHTLY)['ROM_sha256'] == public_now
    if not args.metadata:
        assert q['passed'], 'Private native DK component check did not pass'


if __name__ == '__main__':
    main()
