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
PUBLIC_SMB2 = '3684f3d2a418a484befd80fca351d0dc5f9b472f6f067a0a7894994ea343679d'
PINS = {
    'first-item': 'b784ed4ed57a051231424e1f603dda8b160a34b749d23138649ae7d463fe4a47',
    'first-pipe': '65af12f18021d30e47bd9f4022c01148bf295da76017f744acc38456345b90b8',
    'full': '122f4984fcf4310ce19fb26e4a7a121c83c0fff08b62dbc85af6d95adfffee66',
    'full-enemy-guard': 'acf454572d604b049deebbb82300a07c6852c9712065d6d32f44932c6e38442f',
    'full-waiting-guard': '36307f8ca293bf558377591a05939ed74d4b5a8cc42152a38cdce1c998cf0fbc',
}
DIRECT_PINS = {
    'first-item': '5ef1c7955010c1abebcbefdcdbe6594b76024f123a89117436b5782cde7f1d53',
    'full-enemy-guard': '84161feb7c7d4c6f6eb938e85a0fb2d82aef0600a9132d9946f148f85f1dcec6',
    'full-waiting-guard': '6c6aac8a3d0fdfe334beebcf62b4514014e45d9e044f43926b3ee38e261c8d73',
}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--route', choices=tuple(PINS), required=True)
    p.add_argument('--metadata', action='store_true')
    p.add_argument('--reuse', action='store_true', help='Reuse the already composed exact14ae private file; no repeated parent build.')
    p.add_argument('--direct', action='store_true', help='Explicit granted769afe direct-foreign successor; first-item or full-enemy-guard only.')
    args = p.parse_args()
    if args.direct:
        import compose_dkjr_direct_platform_1113 as Direct
        assert args.route in DIRECT_PINS
    public_now = check(NIGHTLY)['ROM_sha256']
    assert public_now in (PARENT, PUBLIC_BUB, PUBLIC_SMB2)
    raw = NIGHTLY.read_bytes()
    if public_now == PUBLIC_SMB2:
        import compose_smb2_foreground_current_1113 as Current
        raw = Current.inverse(raw)
        assert sha256(raw).hexdigest() == PUBLIC_BUB
    if sha256(raw).hexdigest() == PUBLIC_BUB:
        import bub_native_noops_1113 as Bub
        raw = Bub.combined_reverse(raw)
        assert sha256(raw).hexdigest() == PARENT
    if args.reuse:
        image = (OUT / 'candidate.nes').read_bytes()
        if args.direct and sha256(image).hexdigest()==Direct.PIN:
            image=Direct.reverse(image)
        assert sha256(image).hexdigest() == C.PIN
        assert sha256(C.reverse(image)).hexdigest() == C.PARENT
    else:
        image, info = C.compose_current(raw)
        assert sha256(image).hexdigest() == C.PIN
        assert C.P.inverse_current(C.reverse(image)) == raw
        assert info['new_RAM_bytes'] == info['new_CHR_bytes'] == 0
    candidate=C.PIN
    expected=PINS[args.route]
    if args.direct:
        direct_parent=image
        image,direct_info=Direct.transform(image)
        assert Direct.reverse(image)==direct_parent and direct_info['changed_bytes']==141
        candidate=Direct.PIN
        full=args.route in ('full-enemy-guard','full-waiting-guard')
        text=Direct.controller(image,full=full,departure_enemy_guard=full,
                               approach_enemy_guard=args.route=='full-waiting-guard')
        expected=DIRECT_PINS[args.route]
    elif args.route == 'first-item':
        text = C.controller(image)
    elif args.route in ('full', 'full-enemy-guard', 'full-waiting-guard'):
        text = Replay.controller(image, descending_roof=(2,3), observe_prior=True,
                                 early_ledge=True, native_gap_observer=True,
                                 departure_enemy_guard=args.route!='full',
                                 approach_enemy_guard=args.route=='full-waiting-guard')
    else:
        text = Replay.controller(image, pipes=(1,), stop_after_pipe=1)
    assert sha256(text.encode()).hexdigest() == expected
    LuaRuntime().compile(text)
    summary = dict(ROM_SHA256=candidate, parent_SHA256=PARENT, current_Downloads_SHA256=public_now, route=args.route,
                   Lua_SHA256=expected, direct_foreign=args.direct, private_only=True, installed=False,
                   native_run=not args.metadata, reused_exact_private_candidate=args.reuse)
    if not args.metadata:
        assert OUT.is_dir()
        assert {p.name for p in OUT.iterdir() if p.is_file()} == {'candidate.nes', 'controller.lua'}
        rom, script = OUT / 'candidate.nes', OUT / 'controller.lua'
        rom.write_bytes(image)
        script.write_text(text, encoding='utf-8', newline='\n')
        q = run(script, rom, OUT / 'capture', candidate, 240)
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
