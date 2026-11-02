"""Deliver tested playable Bub/Bob WIP without claiming full-route completion."""
import json
from pathlib import Path
from prepare_selected_native_packet_v1 import R, prepare, sha
from nightly_patch_guard_v1 import check

P = R / 'build/bub-menu-candidate-1102-v2'
O = R / 'build/bub-delivery-1102-v9'
D = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PIN = '613b3300b09e530ec920835b95df53f3115d865ed854e273809d4cafa52407ce'


def read(p):
    return json.loads(p.read_text())


def main():
    rom = P / 'combined-event.nes'
    assert sha(rom) == PIN
    names = ['bub-cold', 'bob-cold', 'bub-controls', 'bob-controls', 'bub-pop',
             'bub-easy2', 'bub-ride', 'bob-ride', 'bub-ceiling']
    for name in names:
        p = P / ('native-event-' + name)
        q, b = read(p / 'ready.json'), read(p / 'capture/binding.json')
        assert read(p / 'capture/result.json')['passed'] and b['exit_code'] == 0
        assert b['ROM_sha256'] == PIN and b['ready_sha256'] == sha(p / 'ready.json')
        for source, h in q['bindings'].items():
            assert sha(source) == h, source
    assert sha(D) == 'f5c30ceaa36894f3e814ef277081ecd9cf434a934c0f7b3f514c2291be0e1cfc'
    before = check(D)
    D.write_bytes(rom.read_bytes())
    after = check(D)
    assert sha(D) == PIN
    O.mkdir(exist_ok=True)
    for name in ['bub-controls', 'bob-ride']:
        source = P / ('native-event-' + name) / 'controller.lua'
        out = O / ('downloads-' + name)
        prepare(out, rom, source.read_text(), [Path(__file__), source, D], expected=PIN,
                timeout=230, allow_interactive=True,
                scope='Actual Downloads launch of tested playable Bub/Bob WIP. No backup. Core controls/earned ride only; full1-1 and all powerups still incomplete.')
        q = read(out / 'ready.json')
        q['ROM'] = str(D)
        (out / 'ready.json').write_text(json.dumps(q, indent=2) + '\n')
    report = dict(installed=True, ROM_sha256=PIN, previous_sha256=before['ROM_sha256'],
                  destination=str(D), backup_created=False, before=before, after=after,
                  verified_native_runs=names, downloads_launch_verified=False,
                  remaining='Full1-1: first2 pipes pass, second moving-away Goomba pop timing under controller correction. Idle/walk roughly half rate. All-character/all-powerup goal remains incomplete.')
    (O / 'delivery.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
